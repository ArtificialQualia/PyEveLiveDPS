import re
from tkinter import messagebox

import logging
import sys
import time
import os

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class CharacterDetector():
    def __init__(self):
        self.observer = observer
        self.filename = os.environ['HOMEPATH'] + "\\Documents\\EVE\\logs\\Gamelogs"
        
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(self.filename):
            print("file created")
            self.observer.stop()

class LogReader():
    def __init__(self):
        path = os.environ['HOMEPATH'] + "\\Documents\\EVE\\logs\\Gamelogs"
        self.log = open(path + "\\20170703_161846.txt", 'r')
        #self.log = open("C:\\Users\\Kendall\\Documents\\EVE\\logs\\Gamelogs\\20170703_001918.txt", 'r')
        self.log.readline()
        self.log.readline()
        characterLine = self.log.readline()
        character = re.search("(?<=Listener: ).*", characterLine)
        if character:
            character = character.group(0)
        else:
            messagebox.showinfo("Error", "this is not a character logfile")
        print(character)
        self.log.readline()
        self.log.readline()
        self.logLine = self.log.readline()
        if (self.logLine == "------------------------------------------------------------\n"):
            self.log.readline()
            collisionCharacter = re.search("(?<=Listener: ).*", self.log.readline()).group(0)
            messagebox.showinfo("Error", "Log file collision on characters:\n\n" + character + " and " + collisionCharacter +
                                "\n\nThis happens when both characters log in at exactly the same second.\n" + 
                                "This makes it impossible to know which character owns which log.\n\n" + 
                                "Please restart the client of the character you want to track to use this program.")
        self.log.read()
            
    def readLog(self):
        logData = self.log.read()
        
        damageOut = 0
        damageOutGroup = re.findall("\(combat\) <.*?><b>([0-9]+).*>to<", logData)
        if damageOutGroup:
            for match in damageOutGroup:
                damageOut += int(match)
                
        damageIn = 0
        damageInGroup = re.findall("\(combat\) <.*?><b>([0-9]+).*>from<", logData)
        if damageInGroup:
            for match in damageInGroup:
                damageIn += int(match)
                
        return damageOut, damageIn