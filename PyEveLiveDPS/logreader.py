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
import settings
import data.oreVolume
_oreVolume = data.oreVolume._oreVolume
from tkinter import messagebox, IntVar, filedialog
if (platform.system() == "Windows"):
    import win32com.client

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

_emptyResult = [[] for x in range(0,8)]
_emptyResult.append(0)

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
                    newLogReader = LogReader(logPath, self.mainWindow)
                except BadLogException:
                    return
                self.logReaders[i] = newLogReader
                return
        
        try:
            newLogReader = LogReader(logPath, self.mainWindow)
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
            self.playbackLogReader = PlaybackLogReader(logPath, self.mainWindow)
            self.mainWindow.addPlaybackFrame(self.playbackLogReader.startTimeLog, self.playbackLogReader.endTimeLog)
        except BadLogException:
            self.playbackLogReader = None
            
    def stopPlayback(self):
        self.playbackLogReader = None
        self.mainWindow.removePlaybackFrame()
        
    def readLog(self):
        if (self.playbackLogReader):
            return self.playbackLogReader.readLog()
        elif (len(self.menuEntries) > 0):
            return self.logReaders[self.selectedIndex.get()].readLog()
        else:
            return _emptyResult
    
    def catchupLog(self):
        self.mainWindow.animator.catchup()
        try:
            self.logReaders[self.selectedIndex.get()].catchup()
        except IndexError:
            pass
        
class BaseLogReader():
    def __init__(self, logPath, mainWindow):
        self.mainWindow = mainWindow
        pilotAndWeaponRegex = '.*ffffffff>(.*)\[.*\((.*)\)<.*> \- (.*)[\-<]'
        self.damageOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*>to<" + pilotAndWeaponRegex)
        
        self.damageInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*>from<" + pilotAndWeaponRegex)
        
        self.armorRepairedOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote armor repaired to <" + pilotAndWeaponRegex)
        self.hullRepairedOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote hull repaired to <" + pilotAndWeaponRegex)
        self.shieldBoostedOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote shield boosted to <" + pilotAndWeaponRegex)
        
        self.armorRepairedInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote armor repaired by <" + pilotAndWeaponRegex)
        self.hullRepairedInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote hull repaired by <" + pilotAndWeaponRegex)
        self.shieldBoostedInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote shield boosted by <" + pilotAndWeaponRegex)
        
        self.capTransferedOutRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote capacitor transmitted to <" + pilotAndWeaponRegex)
        
        self.capNeutralizedOutRegex = re.compile("\(combat\) <.*?ff7fffff><b>([0-9]+).*> energy neutralized <" + pilotAndWeaponRegex)
        self.nosRecievedRegex = re.compile("\(combat\) <.*?><b>\+([0-9]+).*> energy drained from <" + pilotAndWeaponRegex)
        
        self.capTransferedInRegex = re.compile("\(combat\) <.*?><b>([0-9]+).*> remote capacitor transmitted by <" + pilotAndWeaponRegex)
        #add nos recieved to this group in readlog
        
        self.capNeutralizedInRegex = re.compile("\(combat\) <.*?ffe57f7f><b>([0-9]+).*> energy neutralized <" + pilotAndWeaponRegex)
        self.nosTakenRegex = re.compile("\(combat\) <.*?><b>\-([0-9]+).*> energy drained to <" + pilotAndWeaponRegex)
        
        self.minedRegex = re.compile("\(mining\) .* <b><.*?><.*?>([0-9]+).*> units of .*<b>(.+)</b>")
        
    def readLog(self, logData):
        damageOut = self.extractValues(self.damageOutRegex, logData)
        damageIn = self.extractValues(self.damageInRegex, logData)
        logisticsOut = self.extractValues(self.armorRepairedOutRegex, logData)
        logisticsOut.extend(self.extractValues(self.hullRepairedOutRegex, logData))
        logisticsOut.extend(self.extractValues(self.shieldBoostedOutRegex, logData))
        logisticsIn = self.extractValues(self.armorRepairedInRegex, logData)
        logisticsIn.extend(self.extractValues(self.hullRepairedInRegex, logData))
        logisticsIn.extend(self.extractValues(self.shieldBoostedInRegex, logData))
        capTransfered = self.extractValues(self.capTransferedOutRegex, logData)
        capRecieved = self.extractValues(self.capTransferedInRegex, logData)
        capRecieved.extend(self.extractValues(self.nosRecievedRegex, logData))
        capDamageDone = self.extractValues(self.capNeutralizedOutRegex, logData)
        capDamageDone.extend(self.extractValues(self.nosRecievedRegex, logData))
        capDamageRecieved = self.extractValues(self.capNeutralizedInRegex, logData)
        capDamageRecieved.extend(self.extractValues(self.nosTakenRegex, logData))
        mined = self.extractValues(self.minedRegex, logData, mining=True)
                
        return damageOut, damageIn, logisticsOut, logisticsIn, capTransfered, capRecieved, capDamageDone, capDamageRecieved, mined
    
    def extractValues(self, regex, logData, mining=False):
        returnValue = 0
        group = regex.findall(logData)
        if mining:
            if group:
                for amount,type in group:
                    if self.mainWindow.settings.getMiningM3Setting():
                        if type in _oreVolume:
                            returnValue += int(amount) * _oreVolume[type]
                        else:
                            returnValue += int(amount)
                    else:
                        returnValue += int(amount)
            return returnValue
        returnValue = []
        if group:
            for match in group:
                returnGroup = {}
                returnGroup['amount'] = int(match[0])
                returnGroup['pilotName'] = match[1]
                returnGroup['shipType'] = match[2]
                returnGroup['weaponType'] = match[3]
                returnValue.append(returnGroup)
        return returnValue
    
class PlaybackLogReader(BaseLogReader):
    def __init__(self, logPath, mainWindow):
        super().__init__(logPath, mainWindow)
        self.mainWindow = mainWindow
        self.paused = False
        self.logPath = logPath
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
            self.startTimeLog = datetime.datetime.strptime(re.search("(?<=Session Started: ).*", self.log.readline()).group(0), "%Y.%m.%d %X")
        else:
            messagebox.showerror("Error", "This doesn't appear to be a EVE combat log.\nPlease select a different file.")
            raise BadLogException("not character log")
        self.log.readline()
        self.logLine = self.log.readline()
        while (self.logLine == "------------------------------------------------------------\n"):
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
        self.startTimeDelta = datetime.datetime.utcnow() - self.startTimeLog
        
        #inefficient, but ok for our normal log size
        endOfLog = open(logPath, 'r', encoding="utf8")
        line = endOfLog.readline()
        while ( line != '' ):
            line = endOfLog.readline()
            try:
                nextTimeString = self.timeRegex.findall(line)[0]
            except IndexError:
                continue
            self.endTimeLog = datetime.datetime.strptime(nextTimeString, "[ %Y.%m.%d %X ]")
        endOfLog.close()
        
        endOfLog = open(logPath, 'r', encoding="utf8")
        line = endOfLog.readline()
        self.logEntryFrequency = [0] * (self.endTimeLog - self.startTimeLog).seconds
        while ( line != '' ):
            line = endOfLog.readline()
            try:
                nextTimeString = self.timeRegex.findall(line)[0]
                entryTime = datetime.datetime.strptime(nextTimeString, "[ %Y.%m.%d %X ]")
                self.logEntryFrequency[(entryTime - self.startTimeLog).seconds] += 1
            except IndexError:
                continue
        endOfLog.close()
        
    def newStartTime(self, newTime):
        self.log.close()
        self.log = open(self.logPath, 'r', encoding="utf8")
        self.startTimeDelta = datetime.datetime.utcnow() - newTime
        self.nextTime = self.startTimeLog
        while ( self.nextTime < newTime ):
            line = self.log.readline()
            try:
                nextTimeString = self.timeRegex.findall(line)[0]
            except IndexError:
                continue
            self.nextTime = datetime.datetime.strptime(nextTimeString, "[ %Y.%m.%d %X ]")
        
    def readLog(self):
        if self.paused:
            return _emptyResult
        logData = ""
        logReaderTime = datetime.datetime.utcnow() - self.startTimeDelta
        self.mainWindow.playbackFrame.timeSlider.set((logReaderTime - self.startTimeLog).seconds)
        while ( self.nextTime < logReaderTime ):
            logData += self.nextLine
            self.nextLine = self.log.readline()
            if (self.nextLine == ''):
                self.mainWindow.playbackFrame.pauseButtonRelease(None)
                return _emptyResult
            try:
                nextTimeString = self.timeRegex.findall(self.nextLine)[0]
            except IndexError:
                continue
            self.nextTime = datetime.datetime.strptime(nextTimeString, "[ %Y.%m.%d %X ]")
        return super().readLog(logData)
        
        
class LogReader(BaseLogReader):
    def __init__(self, logPath, mainWindow):
        super().__init__(logPath, mainWindow)
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
    
    def catchup(self):
        self.log.read()
    
class BadLogException(Exception):
    pass