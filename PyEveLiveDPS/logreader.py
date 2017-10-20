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
if (platform.system() == "Windows"):
    import win32com.client

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class CharacterDetector(FileSystemEventHandler):
    def __init__(self, mainWindow, characterMenu):
        self.mainWindow = mainWindow
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
        self.playbackLogReader = None
        
        try:
            oneDayAgo = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
            fileList = sorted(os.listdir(self.path), key=lambda file: os.stat(os.path.join(self.path, file)).st_mtime)
            for filename in fileList:
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
        except FileNotFoundError:
            messagebox.showerror("Error", "Can't find the EVE logs directory.  Do you have EVE installed?  \n\n" +
                                 "Path checked: " + self.path + "\n\n" +
                                 "PELD will continue to run, but will not track EVE data.")
        
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
        
    def stop(self):
        self.observer.stop()
        
    def playbackLog(self, logPath):
        try:
            self.playbackLogReader = PlaybackLogReader(logPath)
            self.mainWindow.mainMenu.menu.delete(4)
            self.mainWindow.mainMenu.menu.insert_command(4, label="Stop Log Playback", command=self.stopPlayback)
        except BadLogException:
            self.playbackLogReader = None
            
    def stopPlayback(self):
        self.playbackLogReader = None
        getLogFilePath = lambda: tk.filedialog.askopenfilename(initialdir=self.characterDetector.path, title="Select log file")
        self.mainWindow.mainMenu.menu.delete(4)
        self.mainWindow.mainMenu.menu.insert_command(4, label="Playback Log", command=lambda: self.playbackLog(getLogFilePath()))
        
    def readLog(self):
        if (self.playbackLogReader):
            try:
                return self.playbackLogReader.readLog()
            except EndOfLogException:
                self.playbackLogReader = None
                messagebox.showinfo("Playback done", "End of log file reached, resuming normal operation.")
                return 0,0,0,0,0,0,0,0
        elif (len(self.menuEntries) > 0):
            return self.logReaders[self.selectedIndex.get()].readLog()
        else:
            return 0,0,0,0,0,0,0,0
    
    def catchupLog(self):
        self.mainWindow.animator.catchup()
        try:
            self.logReaders[self.selectedIndex.get()].catchup()
        except IndexError:
            pass
        
class BaseLogReader():
    def __init__(self, logPath):
        self.damageOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*>to<")
        
        self.damageInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*>from<")
        
        self.armorRepairedOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote armor repaired to <")
        self.hullRepairedOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote hull repaired to <")
        self.shieldBoostedOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote shield boosted to <")
        
        self.armorRepairedInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote armor repaired by <")
        self.hullRepairedInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote hull repaired by <")
        self.shieldBoostedInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote shield boosted by <")
        
        self.capTransferedOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote capacitor transmitted to <")
        
        self.capNeutralizedOutRegex = re.compile("\(combat\) <.*?ff7fffff><b>([0-9]+).*> energy neutralized <")
        self.nosRecievedRegex = re.compile("\(combat\) <.*?><b>\+([0-9]+).*> energy drained from <")
        
        self.capTransferedInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote capacitor transmitted by <")
        #add nos recieved to this group in readlog
        
        self.capNeutralizedInRegex = re.compile("\(combat\) <.*?ffe57f7f><b>([0-9]+).*> energy neutralized <")
        self.nosTakenRegex = re.compile("\(combat\) <.*?><b>\-([0-9]+).*> energy drained to <")
        
    def readLog(self, logData):
        damageOut = self.extractValues(self.damageOutRegex, logData)
        damageIn = self.extractValues(self.damageInRegex, logData)
        logisticsOut = self.extractValues(self.armorRepairedOutRegex, logData)
        logisticsOut += self.extractValues(self.hullRepairedOutRegex, logData)
        logisticsOut += self.extractValues(self.shieldBoostedOutRegex, logData)
        logisticsIn = self.extractValues(self.armorRepairedInRegex, logData)
        logisticsIn += self.extractValues(self.hullRepairedInRegex, logData)
        logisticsIn += self.extractValues(self.shieldBoostedInRegex, logData)
        capTransfered = self.extractValues(self.capTransferedOutRegex, logData)
        capRecieved = self.extractValues(self.capTransferedInRegex, logData)
        capRecieved += self.extractValues(self.nosRecievedRegex, logData)
        capDamageDone = self.extractValues(self.capNeutralizedOutRegex, logData)
        capDamageDone += self.extractValues(self.nosRecievedRegex, logData)
        capDamageRecieved = self.extractValues(self.capNeutralizedInRegex, logData)
        capDamageRecieved += self.extractValues(self.nosTakenRegex, logData)
                
        return damageOut, damageIn, logisticsOut, logisticsIn, capTransfered, capRecieved, capDamageDone, capDamageRecieved
    
    def extractValues(self, regex, logData):
        returnValue = 0
        group = regex.findall(logData)
        if group:
            for match in group:
                returnValue += int(match)
        return returnValue
    
class PlaybackLogReader(BaseLogReader):
    def __init__(self, logPath):
        super().__init__(logPath)
        try:
            self.log = open(logPath, 'r', encoding="utf8")
            self.log.readline()
            self.log.readline()
        except:
            messagebox.showerror("Error", "This doesn't appear to be a EVE log file.\nPlease select a different file.")
            raise BadLogException("not character log")
        characterLine = self.log.readline()
        character = re.search("(?<=Listener: ).*", characterLine)
        if character:
            character = character.group(0)
            startTimeLog = datetime.datetime.strptime(re.search("(?<=Session Started: ).*", self.log.readline()).group(0), "%Y.%m.%d %X")
        else:
            messagebox.showerror("Error", "This doesn't appear to be a EVE combat log.\nPlease select a different file.")
            raise BadLogException("not character log")
        self.log.readline()
        self.logLine = self.log.readline()
        if (self.logLine == "------------------------------------------------------------\n"):
            self.log.readline()
            collisionCharacter = re.search("(?<=Listener: ).*", self.log.readline()).group(0)
            #Since we currently don't have a use for characters during playback, this is not needed for now.
            #messagebox.showerror("Error", "Log file collision on characters:\n\n" + character + " and " + collisionCharacter +
            #                    "\n\nThis happens when both characters log in at exactly the same second.\n" + 
            #                    "This makes it impossible to know which character owns this log.\n\n" + 
            #                    "Playback will continue\nlog file:\n" + logPath)
            self.log.readline()
            self.log.readline()
            self.logLine = self.log.readline()
        self.timeRegex = re.compile("^\[ .*? \]")
        self.nextLine = self.logLine
        self.nextTime = datetime.datetime.strptime(self.timeRegex.findall(self.nextLine)[0], "[ %Y.%m.%d %X ]")
        self.startTimeDelta = datetime.datetime.utcnow() - startTimeLog
        print(self.nextTime)
        
    def readLog(self):
        logData = ""
        while ( self.nextTime < datetime.datetime.utcnow() - self.startTimeDelta ):
            logData += self.nextLine
            self.nextLine = self.log.readline()
            if (self.nextLine == ''):
                raise EndOfLogException("End of log")
            try:
                nextTimeString = self.timeRegex.findall(self.nextLine)[0]
            except IndexError:
                continue
            self.nextTime = datetime.datetime.strptime(nextTimeString, "[ %Y.%m.%d %X ]")
            print(self.nextTime)
        if logData != '': print(logData)
        return super().readLog(logData)
        
        
class LogReader(BaseLogReader):
    def __init__(self, logPath):
        super().__init__(logPath)
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
            messagebox.showerror("Error", "Log file collision on characters:\n\n" + character + " and " + collisionCharacter +
                                "\n\nThis happens when both characters log in at exactly the same second.\n" + 
                                "This makes it impossible to know which character owns which log.\n\n" + 
                                "Please restart the client of the character you want to track to use this program.\n" + 
                                "If you already did, you can ignore this message, or delete this log file:\n" + logPath)
            raise BadLogException("log file collision")
        self.log.read()
            
    def readLog(self):
        logData = self.log.read()
        return super().readLog(logData)
    
    def extractValues(self, regex, logData):
        returnValue = 0
        group = regex.findall(logData)
        if group:
            for match in group:
                returnValue += int(match)
        return returnValue
    
    def catchup(self):
        self.log.read()
    
class BadLogException(Exception):
    pass
class EndOfLogException(Exception):
    pass