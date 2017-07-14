"""
This file contains two classes:

    CharacterDetector:
        This class monitors the eve gamelog directory for new files,
        as well as initializes PELD with the last day's worth of eve logs
        and keeps track of what eve character belongs to which log.
        
        When a new file enters the gamelog directory, CharacterDetector
        either replaces an existing character with the new log file,
        or adds a new character to the character menu.
        
    LogReader:
        This class does the actual reading of the logs.  Each eve
        character has it's own instance of this class.  This class
        contains the regex which process new log entries into a consumable
        format.
"""

import re
import os
import datetime
import time
import platform
from tkinter import messagebox, IntVar
import win32com.client

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class CharacterDetector(FileSystemEventHandler):
    def __init__(self, characterMenu):
        self.characterMenu = characterMenu
        self.observer = Observer()
        
        if (platform.system() == "Windows"):
            oShell = win32com.client.Dispatch("Wscript.Shell")
            self.path = oShell.SpecialFolders("MyDocuments") + "\\EVE\\logs\\Gamelogs\\"
        else:
            self.path = os.environ['HOME'] + "/Documents/EVE/logs/Gamelogs/"
        
        self.menuEntries = []
        self.logReaders = []
        self.selectedIndex = IntVar()
        
        oneDayAgo = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        for filename in os.listdir(self.path):
            timeString = filename.strip(".txt")
            try:
                fileTime = datetime.datetime.strptime(timeString, "%Y%m%d_%H%M%S")
            except ValueError:
                continue
            if (fileTime >= oneDayAgo):
                self.addLog(self.path + filename)
        
        self.selectedIndex.set(0)
        
        self.observer.schedule(self, self.path, recursive=False)
        self.observer.start()
        
    def on_created(self, event):
        self.addLog(event.src_path)
        
    def addLog(self, logPath):
        log = open(logPath, 'r', encoding="utf8")
        log.readline()
        log.readline()
        characterLine = log.readline()
        character = re.search("(?<=Listener: ).*", characterLine)
        if character:
            character = character.group(0)
        else:
            #print("Log created, but not a character log.")
            return
        log.close()
        
        for i in range(len(self.menuEntries)):
            if (character == self.menuEntries[i]):
                try:
                    newLogReader = LogReader(logPath)
                except BadLogException:
                    return
                self.logReaders[i] = newLogReader
                return
        
        try:
            newLogReader = LogReader(logPath)
        except BadLogException:
            return
        self.logReaders.append(newLogReader)
        self.characterMenu.menu.add_radiobutton(label=character, variable=self.selectedIndex, 
                                                value=len(self.menuEntries), command=self.catchupLog)
        self.menuEntries.append(character)
        
    def setGraphInstance(self, graphInstance):
        self.graphInstance = graphInstance
        
    def stop(self):
        self.observer.stop()
        
    def readLog(self):
        if (len(self.menuEntries) > 0):
            return self.logReaders[self.selectedIndex.get()].readLog()
        else:
            return 0,0
    
    def catchupLog(self):
        self.graphInstance.catchup()
        self.logReaders[self.selectedIndex.get()].catchup()
        
class LogReader():
    def __init__(self, logPath):
        self.log = open(logPath, 'r', encoding="utf8")
        self.log.readline()
        self.log.readline()
        characterLine = self.log.readline()
        character = re.search("(?<=Listener: ).*", characterLine)
        if character:
            character = character.group(0)
        else:
            raise BadLogException("not character log")
        self.log.readline()
        self.log.readline()
        self.logLine = self.log.readline()
        if (self.logLine == "------------------------------------------------------------\n"):
            self.log.readline()
            collisionCharacter = re.search("(?<=Listener: ).*", self.log.readline()).group(0)
            messagebox.showinfo("Error", "Log file collision on characters:\n\n" + character + " and " + collisionCharacter +
                                "\n\nThis happens when both characters log in at exactly the same second.\n" + 
                                "This makes it impossible to know which character owns which log.\n\n" + 
                                "Please restart the client of the character you want to track to use this program.\n" + 
                                "If you already did, you can ignore this message, or delete this log file:\n" + logPath)
            raise BadLogException("log file collision")
        self.log.read()
        
        self.damageOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*>to<")
        self.damageInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*>from<")
        self.armorRepairedRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote armor repaired to <")
        self.hullRepairedRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote hull repaired to <")
        self.shieldBoostedRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote shield boosted to <")
            
    def readLog(self):
        logData = self.log.read()
        
        damageOut = 0
        damageOutGroup = self.damageOutRegex.findall(logData)
        if damageOutGroup:
            for match in damageOutGroup:
                damageOut += int(match)
                
        damageIn = 0
        damageInGroup = self.damageInRegex.findall(logData)
        if damageInGroup:
            for match in damageInGroup:
                damageIn += int(match)
                
        logistics = 0
        armorRepGroup = self.armorRepairedRegex.findall(logData)
        if armorRepGroup:
            for match in armorRepGroup:
                logistics += int(match)
        hullRepGroup = self.hullRepairedRegex.findall(logData)
        if hullRepGroup:
            for match in hullRepGroup:
                logistics += int(match)
        shieldBoostGroup = self.shieldBoostedRegex.findall(logData)
        if shieldBoostGroup:
            for match in shieldBoostGroup:
                logistics += int(match)
                
        return damageOut, damageIn, logistics
    
    def catchup(self):
        self.log.read()
    
class BadLogException(Exception):
    pass