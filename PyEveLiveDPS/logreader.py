"""
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
import tkinter as tk
from peld import settings
import logging
import data.oreVolume
_oreVolume = data.oreVolume._oreVolume
from tkinter import messagebox, IntVar, filedialog

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

_emptyResult = [[] for x in range(0,9)]

# this holds the regex strings for all the different languages the eve game log can be in
_logLanguageRegex = {
    'english': {
        'character': "(?<=Listener: ).*",
        'sessionTime': "(?<=Session Started: ).*",
        'pilotAndWeapon': '(?:.*ffffffff>(?P<default_pilot>[^\(\)<>]*)(?:\[.*\((?P<default_ship>.*)\)<|<)/b.*> \-(?: (?P<default_weapon>.*?)(?: \-|<)|.*))',
        'damageOut': "\(combat\) <.*?><b>([0-9]+).*>to<",
        'damageIn': "\(combat\) <.*?><b>([0-9]+).*>from<",
        'armorRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> remote armor repaired to <",
        'hullRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> remote hull repaired to <",
        'shieldBoostedOut': "\(combat\) <.*?><b>([0-9]+).*> remote shield boosted to <",
        'armorRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> remote armor repaired by <",
        'hullRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> remote hull repaired by <",
        'shieldBoostedIn': "\(combat\) <.*?><b>([0-9]+).*> remote shield boosted by <",
        'capTransferedOut': "\(combat\) <.*?><b>([0-9]+).*> remote capacitor transmitted to <",
        'capNeutralizedOut': "\(combat\) <.*?ff7fffff><b>([0-9]+).*> energy neutralized <",
        'nosRecieved': "\(combat\) <.*?><b>\+([0-9]+).*> energy drained from <",
        'capTransferedIn': "\(combat\) <.*?><b>([0-9]+).*> remote capacitor transmitted by <",
        'capNeutralizedIn': "\(combat\) <.*?ffe57f7f><b>([0-9]+).*> energy neutralized <",
        'nosTaken': "\(combat\) <.*?><b>\-([0-9]+).*> energy drained to <",
        'mined': "\(mining\) .* <b><.*?><.*?>([0-9]+).*> units of .*<b>(.+)</b>"
    },
    'russian': {
        'character': "(?<=Ð¡Ð»ÑƒÑˆÐ°Ñ‚ÐµÐ»ÑŒ: ).*",
        'sessionTime': "(?<=Ð¡ÐµÐ°Ð½Ñ� Ð½Ð°Ñ‡Ð°Ñ‚: ).*",
        'pilotAndWeapon': '(?:.*ffffffff>(?:<localized .*?>)?(?P<default_pilot>[^\(\)<>]*)(?:\[.*\((?:<localized .*?>)?(?P<default_ship>.*)\)<|<)/b.*> \-(?: (?:<localized .*?>)?(?P<default_weapon>.*?)(?: \-|<)|.*)',
        'damageOut': "\(combat\) <.*?><b>Ð£Ñ‰ÐµÑ€Ð± ([0-9]+).*> Ð½Ð°Ð½Ð¾Ñ�Ð¸Ñ‚ ÑƒÐ´Ð°Ñ€ Ð¿Ð¾ <",
        'damageIn': "\(combat\) <.*?><b>Ð£Ñ‰ÐµÑ€Ð± ([0-9]+).*> ÑƒÐ´Ð°Ñ€ Ð¾Ñ‚ <",
        'armorRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> ÐµÐ´Ð¸Ð½Ð¸Ñ† Ð·Ð°Ð¿Ð°Ñ�Ð° Ð¿Ñ€Ð¾Ñ‡Ð½Ð¾Ñ�Ñ‚Ð¸ Ð±Ñ€Ð¾Ð½Ð¸ Ð¾Ñ‚Ñ€ÐµÐ¼Ð¾Ð½Ñ‚Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð¾ <",
        'hullRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> ÐµÐ´Ð¸Ð½Ð¸Ñ† Ð·Ð°Ð¿Ð°Ñ�Ð° Ð¿Ñ€Ð¾Ñ‡Ð½Ð¾Ñ�Ñ‚Ð¸ ÐºÐ¾Ñ€Ð¿ÑƒÑ�Ð° Ð¾Ñ‚Ñ€ÐµÐ¼Ð¾Ð½Ñ‚Ð¸Ñ€Ð¾Ð²Ð°Ð½Ð¾ <",
        'shieldBoostedOut': "\(combat\) <.*?><b>([0-9]+).*> ÐµÐ´Ð¸Ð½Ð¸Ñ† Ð·Ð°Ð¿Ð°Ñ�Ð° Ð¿Ñ€Ð¾Ñ‡Ð½Ð¾Ñ�Ñ‚Ð¸ Ñ‰Ð¸Ñ‚Ð¾Ð² Ð½Ð°ÐºÐ°Ñ‡Ð°Ð½Ð¾ <",
        'armorRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> ÐµÐ´Ð¸Ð½Ð¸Ñ† Ð·Ð°Ð¿Ð°Ñ�Ð° Ð¿Ñ€Ð¾Ñ‡Ð½Ð¾Ñ�Ñ‚Ð¸ Ð±Ñ€Ð¾Ð½Ð¸ Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð¾ Ð´Ð¸Ñ�Ñ‚Ð°Ð½Ñ†Ð¸Ð¾Ð½Ð½Ñ‹Ð¼ Ñ€ÐµÐ¼Ð¾Ð½Ñ‚Ð¾Ð¼ Ð¾Ñ‚ <",
        'hullRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> ÐµÐ´Ð¸Ð½Ð¸Ñ† Ð·Ð°Ð¿Ð°Ñ�Ð° Ð¿Ñ€Ð¾Ñ‡Ð½Ð¾Ñ�Ñ‚Ð¸ ÐºÐ¾Ñ€Ð¿ÑƒÑ�Ð° Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð¾ Ð´Ð¸Ñ�Ñ‚Ð°Ð½Ñ†Ð¸Ð¾Ð½Ð½Ñ‹Ð¼ Ñ€ÐµÐ¼Ð¾Ð½Ñ‚Ð¾Ð¼ Ð¾Ñ‚ <",
        'shieldBoostedIn': "\(combat\) <.*?><b>([0-9]+).*> ÐµÐ´Ð¸Ð½Ð¸Ñ† Ð·Ð°Ð¿Ð°Ñ�Ð° Ð¿Ñ€Ð¾Ñ‡Ð½Ð¾Ñ�Ñ‚Ð¸ Ñ‰Ð¸Ñ‚Ð¾Ð² Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð¾ Ð½Ð°ÐºÐ°Ñ‡ÐºÐ¾Ð¹ Ð¾Ñ‚ <",
        'capTransferedOut': "\(combat\) <.*?><b>([0-9]+).*> ÐµÐ´Ð¸Ð½Ð¸Ñ† Ð·Ð°Ð¿Ð°Ñ�Ð° Ñ�Ð½ÐµÑ€Ð³Ð¸Ð¸ Ð½Ð°ÐºÐ¾Ð¿Ð¸Ñ‚ÐµÐ»Ñ� Ð¾Ñ‚Ð¿Ñ€Ð°Ð²Ð»ÐµÐ½Ð¾ Ð² <",
        'capNeutralizedOut': "\(combat\) <.*?ff7fffff><b>([0-9]+).*> Ñ�Ð½ÐµÑ€Ð³Ð¸Ð¸ Ð½ÐµÐ¹Ñ‚Ñ€Ð°Ð»Ð¸Ð·Ð¾Ð²Ð°Ð½Ð¾ <",
        'nosRecieved': "\(combat\) <.*?><b>\+([0-9]+).*> Ñ�Ð½ÐµÑ€Ð³Ð¸Ð¸ Ð¸Ð·Ð²Ð»ÐµÑ‡ÐµÐ½Ð¾ Ð¸Ð· <",
        'capTransferedIn': "\(combat\) <.*?><b>([0-9]+).*> ÐµÐ´Ð¸Ð½Ð¸Ñ† Ð·Ð°Ð¿Ð°Ñ�Ð° Ñ�Ð½ÐµÑ€Ð³Ð¸Ð¸ Ð½Ð°ÐºÐ¾Ð¿Ð¸Ñ‚ÐµÐ»Ñ� Ð¿Ð¾Ð»ÑƒÑ‡ÐµÐ½Ð¾ Ð¾Ñ‚ <",
        'capNeutralizedIn': "\(combat\) <.*?ffe57f7f><b>([0-9]+).*> Ñ�Ð½ÐµÑ€Ð³Ð¸Ð¸ Ð½ÐµÐ¹Ñ‚Ñ€Ð°Ð»Ð¸Ð·Ð¾Ð²Ð°Ð½Ð¾ <",
        'nosTaken': "\(combat\) <.*?><b>\-([0-9]+).*> Ñ�Ð½ÐµÑ€Ð³Ð¸Ð¸ Ð¸Ð·Ð²Ð»ÐµÑ‡ÐµÐ½Ð¾ Ð¸ Ð¿ÐµÑ€ÐµÐ´Ð°Ð½Ð¾ <",
        'mined': "\(mining\) .* <b><.*?><.*?>([0-9]+).*<b>(?:<localized .*?>)?(.+)\*</b>"
    },
    'french': {
        'character': "(?<=Auditeur: ).*",
        'sessionTime': "(?<=Session commencÃ©e: ).*",
        'pilotAndWeapon': '(?:.*ffffffff>(?:<localized .*?>)?(?P<default_pilot>[^\(\)<>]*)(?:\[.*\((?:<localized .*?>)?(?P<default_ship>.*)\)<|<)/b.*> \-(?: (?:<localized .*?>)?(?P<default_weapon>.*?)(?: \-|<)|.*)',
        'damageOut': "\(combat\) <.*?><b>([0-9]+).*>sur<",
        'damageIn': "\(combat\) <.*?><b>([0-9]+).*>de<",
        'armorRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> points de blindage transfÃ©rÃ©s Ã  distance Ã  <",
        'hullRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> points de structure transfÃ©rÃ©s Ã  distance Ã  <",
        'shieldBoostedOut': "\(combat\) <.*?><b>([0-9]+).*> points de boucliers transfÃ©rÃ©s Ã  distance Ã  <",
        'armorRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> points de blindage rÃ©parÃ©s Ã  distance par <",
        'hullRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> points de structure rÃ©parÃ©s Ã  distance par <",
        'shieldBoostedIn': "\(combat\) <.*?><b>([0-9]+).*> points de boucliers transfÃ©rÃ©s Ã  distance par <",
        'capTransferedOut': "\(combat\) <.*?><b>([0-9]+).*> points de capaciteur transfÃ©rÃ©s Ã  distance Ã  <",
        'capNeutralizedOut': "\(combat\) <.*?ff7fffff><b>([0-9]+).*> d'Ã©nergie neutralisÃ©e en faveur de <",
        'nosRecieved': "\(combat\) <.*?><b>([0-9]+).*> d'Ã©nergie siphonnÃ©e aux dÃ©pens de <",
        'capTransferedIn': "\(combat\) <.*?><b>([0-9]+).*> points de capaciteur transfÃ©rÃ©s Ã  distance par <",
        'capNeutralizedIn': "\(combat\) <.*?ffe57f7f><b>([0-9]+).*> d'Ã©nergie neutralisÃ©e aux dÃ©pens de <",
        'nosTaken': "\(combat\) <.*?><b>([0-9]+).*> d'Ã©nergie siphonnÃ©e en faveur de <",
        'mined': "\(mining\) .* <b><.*?><.*?>([0-9]+).*<b>(?:<localized .*?>)?(.+)\*</b>"
    },
    'german': {
        'character': "(?<=EmpfÃ¤nger: ).*",
        'sessionTime': "(?<=Sitzung gestartet: ).*",
        'pilotAndWeapon': '(?:.*ffffffff>(?:<localized .*?>)?(?P<default_pilot>[^\(\)<>]*)(?:\[.*\((?:<localized .*?>)?(?P<default_ship>.*)\)<|<)/b.*> \-(?: (?:<localized .*?>)?(?P<default_weapon>.*?)(?: \-|<)|.*)',
        'damageOut': "\(combat\) <.*?><b>([0-9]+).*>gegen<",
        'damageIn': "\(combat\) <.*?><b>([0-9]+).*>von <",
        'armorRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> Panzerungs-Fernreparatur zu <",
        'hullRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> Rumpf-Fernreparatur zu <",
        'shieldBoostedOut': "\(combat\) <.*?><b>([0-9]+).*> Schildfernbooster aktiviert zu <",
        'armorRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> Panzerungs-Fernreparatur von <",
        'hullRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> Rumpf-Fernreparatur von <",
        'shieldBoostedIn': "\(combat\) <.*?><b>([0-9]+).*> Schildfernbooster aktiviert von <",
        'capTransferedOut': "\(combat\) <.*?><b>([0-9]+).*> Fernenergiespeicher Ã¼bertragen zu <",
        'capNeutralizedOut': "\(combat\) <.*?ff7fffff><b>([0-9]+).*> Energie neutralisiert <",
        'nosRecieved': "\(combat\) <.*?><b>\+([0-9]+).*> Energie transferiert von <",
        'capTransferedIn': "\(combat\) <.*?><b>([0-9]+).*> Fernenergiespeicher Ã¼bertragen von <",
        'capNeutralizedIn': "\(combat\) <.*?ffe57f7f><b>\-([0-9]+).*> Energie neutralisiert <",
        'nosTaken': "\(combat\) <.*?><b>\-([0-9]+).*> Energie transferiert zu <",
        'mined': "\(mining\) .* <b><.*?><.*?>([0-9]+).*<b>(?:<localized .*?>)?(.+)\*</b>"
    },
    'japanese': {
        'character': "(?<=傍聴者: ).*",
        'sessionTime': "(?<=セッション開始: ).*",
        'pilotAndWeapon': '(?:.*ffffffff>(?:<localized .*?>)?(?P<default_pilot>[^\(\)<>]*)(?:\[.*\((?:<localized .*?>)?(?P<default_ship>.*)\)<|<)/b.*> \-(?: (?:<localized .*?>)?(?P<default_weapon>.*?)(?: \-|<)|.*)',
        'damageOut': "\(combat\) <.*?><b>([0-9]+).*>対象:<",
        'damageIn': "\(combat\) <.*?><b>([0-9]+).*>攻撃者:<",
        'armorRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> remote armor repaired to <",
        'hullRepairedOut': "\(combat\) <.*?><b>([0-9]+).*> remote hull repaired to <",
        'shieldBoostedOut': "\(combat\) <.*?><b>([0-9]+).*> remote shield boosted to <",
        'armorRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> remote armor repaired by <",
        'hullRepairedIn': "\(combat\) <.*?><b>([0-9]+).*> remote hull repaired by <",
        'shieldBoostedIn': "\(combat\) <.*?><b>([0-9]+).*> remote shield boosted by <",
        'capTransferedOut': "\(combat\) <.*?><b>([0-9]+).*> remote capacitor transmitted to <",
        'capNeutralizedOut': "\(combat\) <.*?ff7fffff><b>([0-9]+).*> エネルギーニュートラライズ 対象:<",
        'nosRecieved': "\(combat\) <.*?><b>\+([0-9]+).*> エネルギードレイン 対象:<",
        'capTransferedIn': "\(combat\) <.*?><b>([0-9]+).*> remote capacitor transmitted by <",
        'capNeutralizedIn': "\(combat\) <.*?ffe57f7f><b>([0-9]+).*>のエネルギーが解放されました<",
        'nosTaken': "\(combat\) <.*?><b>\-([0-9]+).*> エネルギードレイン 攻撃者:<",
        'mined': "\(mining\) .* <b><.*?><.*?>([0-9]+).*<b>(?:<localized .*?>)?(.+)\*</b>"
    }
}

_logReaders = []

class CharacterDetector(FileSystemEventHandler):
    def __init__(self, mainWindow, characterMenu):
        self.mainWindow = mainWindow
        self.characterMenu = characterMenu
        self.observer = Observer()
        
        if (platform.system() == "Windows"):
            import win32com.client
            oShell = win32com.client.Dispatch("Wscript.Shell")
            self.path = oShell.SpecialFolders("MyDocuments") + "\\EVE\\logs\\Gamelogs\\"
        else:
            self.path = os.environ['HOME'] + "/Documents/EVE/logs/Gamelogs/"
        
        self.menuEntries = []
        self.logReaders = _logReaders
        self.selectedIndex = IntVar()
        self.playbackLogReader = None
        
        try:
            oneDayAgo = datetime.datetime.now() - datetime.timedelta(hours=24)
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
            
            if len(self.menuEntries) == 0:
                self.characterMenu.menu.add_command(label='No character logs detected for past 24 hours', state=tk.DISABLED)
            
            self.observer.schedule(self, self.path, recursive=False)
            self.observer.start()
        except FileNotFoundError:
            logging.error('EVE logs directory not found, path checked: ' + self.path)
            messagebox.showerror("Error", "Can't find the EVE logs directory.  Do you have EVE installed?  \n\n" +
                                 "Path checked: " + self.path + "\n\n" +
                                 "PELD will continue to run, but will not track EVE data.")
            self.characterMenu.menu.add_command(label='No EVE installation detected', state=tk.DISABLED)

        self.characterMenu.menu.add_separator()
        from settings.overviewSettings import OverviewSettingsWindow
        self.characterMenu.menu.add_command(label='Open overview settings', command=OverviewSettingsWindow)
        
    def on_created(self, event):
        self.addLog(event.src_path)
        
    def addLog(self, logPath):
        logging.info('Processing log file: ' + logPath)
        log = open(logPath, 'r', encoding="utf8")
        log.readline()
        log.readline()
        characterLine = log.readline()
        try:
            character, language = ProcessCharacterLine(characterLine)
        except BadLogException:
            logging.info("Log " + logPath + " is not a character log.")
            return
        log.close()
        
        if len(self.menuEntries) == 0:
            self.characterMenu.menu.delete(0)
        
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
        self.characterMenu.menu.insert_radiobutton(0, label=character, variable=self.selectedIndex, 
                                                value=len(self.menuEntries), command=self.catchupLog)
        self.menuEntries.append(character)
        
    def stop(self):
        self.observer.stop()
        
    def playbackLog(self, logPath):
        try:
            self.mainWindow.animator.queue = None
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

    def createOverviewRegex(self, overviewSettings):
        if overviewSettings:
            def safeGetIndex(elem, _list):
                try:
                    return _list.index(elem)
                except ValueError:
                    return 10
            try:
                keyLambda = lambda e: safeGetIndex(e[0], overviewSettings['shipLabelOrder'])
                sortedShipLabels = sorted(overviewSettings['shipLabels'], key=keyLambda)
                pilotAndWeaponRegex = "(?:(?:.*ffffffff>"
                for shipLabel in sortedShipLabels[:]:
                    shipLabel[1] = dict(shipLabel[1])
                    if not shipLabel[1]['state']:
                        if shipLabel[1]['type'] in ['pilot name', 'ship type']:
                            identifier = shipLabel[1]['type'].split()[0]
                            pilotAndWeaponRegex += '(?P<'+identifier+'>)'
                        continue
                    if shipLabel[1]['type'] == None:
                        safePre = re.escape(shipLabel[1]['pre'])
                        pilotAndWeaponRegex += '(?:'+safePre+')?'
                    elif shipLabel[1]['type'] in ['alliance', 'corporation', 'ship name']:
                        safePre = re.escape(shipLabel[1]['pre'])
                        safePost = re.escape(shipLabel[1]['post'])
                        pilotAndWeaponRegex += '(?:'+safePre+'.*?'+safePost+')?'
                    elif shipLabel[1]['type'] in ['pilot name', 'ship type']:
                        safePre = re.escape(shipLabel[1]['pre'])
                        safePost = re.escape(shipLabel[1]['post'])
                        identifier = shipLabel[1]['type'].split()[0]
                        pilotAndWeaponRegex += '(?:'+safePre+'(?:<localized .*?>)?(?P<'+identifier+'>.*?)'+safePost+')'
                    else:
                        continue
                pilotAndWeaponRegex += ".*> \-(?: (?:<localized .*?>)?(?P<weapon>.*?)(?: \-|<)|.*))"
                pilotAndWeaponRegex += '|' + _logLanguageRegex[self.language]['pilotAndWeapon'] + ')?'
                return pilotAndWeaponRegex
            except Exception as e:
                logging.error('error parsing overview settings: ' + str(e))
                return None
        else:
            return None
        
    def compileRegex(self):
        basicPilotAndWeaponRegex = _logLanguageRegex[self.language]['pilotAndWeapon']
        basicPilotAndWeaponRegex += '(?P<pilot>)(?P<ship>)(?P<weapon>)'

        overviewSettings = settings.getOverviewSettings(self.character)
        pilotAndWeaponRegex = self.createOverviewRegex(overviewSettings) or basicPilotAndWeaponRegex

        self.damageOutRegex = re.compile(_logLanguageRegex[self.language]['damageOut'] + basicPilotAndWeaponRegex)
        
        self.damageInRegex = re.compile(_logLanguageRegex[self.language]['damageIn'] + basicPilotAndWeaponRegex)
        
        self.armorRepairedOutRegex = re.compile(_logLanguageRegex[self.language]['armorRepairedOut'] + pilotAndWeaponRegex)
        self.hullRepairedOutRegex = re.compile(_logLanguageRegex[self.language]['hullRepairedOut'] + pilotAndWeaponRegex)
        self.shieldBoostedOutRegex = re.compile(_logLanguageRegex[self.language]['shieldBoostedOut'] + pilotAndWeaponRegex)
        
        self.armorRepairedInRegex = re.compile(_logLanguageRegex[self.language]['armorRepairedIn']+ pilotAndWeaponRegex)
        self.hullRepairedInRegex = re.compile(_logLanguageRegex[self.language]['hullRepairedIn'] + pilotAndWeaponRegex)
        self.shieldBoostedInRegex = re.compile(_logLanguageRegex[self.language]['shieldBoostedIn'] + pilotAndWeaponRegex)
        
        self.capTransferedOutRegex = re.compile(_logLanguageRegex[self.language]['capTransferedOut'] + pilotAndWeaponRegex)
        
        self.capNeutralizedOutRegex = re.compile(_logLanguageRegex[self.language]['capNeutralizedOut'] + pilotAndWeaponRegex)
        self.nosRecievedRegex = re.compile(_logLanguageRegex[self.language]['nosRecieved'] + pilotAndWeaponRegex)
        
        self.capTransferedInRegex = re.compile(_logLanguageRegex[self.language]['capTransferedIn'] + pilotAndWeaponRegex)
        #add nos recieved to this group in readlog
        
        self.capNeutralizedInRegex = re.compile(_logLanguageRegex[self.language]['capNeutralizedIn'] + pilotAndWeaponRegex)
        self.nosTakenRegex = re.compile(_logLanguageRegex[self.language]['nosTaken'] + pilotAndWeaponRegex)
        
        self.minedRegex = re.compile(_logLanguageRegex[self.language]['mined'])
        
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
        returnValue = []
        group = regex.finditer(logData)
        if mining:
            for match in group:
                amount = match.group(1)
                _type = match.group(2)
                if amount != 0:
                    returnGroup = {}
                    if settings.getMiningM3Setting():
                        if _type in _oreVolume:
                            returnGroup['amount'] = int(amount) * _oreVolume[_type]
                        else:
                            returnGroup['amount'] = int(amount)
                    else:
                        returnGroup['amount'] = int(amount)
                    returnValue.append(returnGroup)
            return returnValue
        for match in group:
            amount = match.group(1) or 0
            pilotName = match.group('default_pilot') or match.group('pilot') or '?'
            shipType = match.group('ship') or match.group('default_ship') or pilotName
            weaponType = match.group('default_weapon') or match.group('weapon') or 'Unknown'
            if amount != 0:
                returnGroup = {}
                returnGroup['amount'] = int(amount)
                returnGroup['pilotName'] = pilotName.strip()
                returnGroup['shipType'] = shipType
                returnGroup['weaponType'] = weaponType
                returnValue.append(returnGroup)
        return returnValue
    
class PlaybackLogReader(BaseLogReader):
    def __init__(self, logPath, mainWindow):
        super().__init__(logPath, mainWindow)
        logging.info('Processing playback log file: ' + logPath)
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
        try:
            self.character, self.language = ProcessCharacterLine(characterLine)
        except BadLogException:
            messagebox.showerror("Error", "This doesn't appear to be a EVE combat log.\nPlease select a different file.")
            raise BadLogException("not character log")
        logging.info('Log language is ' + self.language)
        
        startTimeRegex = _logLanguageRegex[self.language]['sessionTime']
        self.startTimeLog = datetime.datetime.strptime(re.search(startTimeRegex, self.log.readline()).group(0), "%Y.%m.%d %X")

        self.log.readline()
        self.logLine = self.log.readline()
        while (self.logLine == "------------------------------------------------------------\n"):
            self.log.readline()
            collisionCharacter, language = ProcessCharacterLine(self.log.readline())
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
        
        self.compileRegex()
        
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
            self.nextLine = line
        
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
        self.character, self.language = ProcessCharacterLine(characterLine)
        logging.info('Log language is ' + self.language)
        self.log.readline()
        self.log.readline()
        self.logLine = self.log.readline()
        if (self.logLine == "------------------------------------------------------------\n"):
            self.log.readline()
            collisionCharacter, language = ProcessCharacterLine(self.log.readline())
            logging.error('Log file collision on characters' + self.character + " and " + collisionCharacter)
            messagebox.showerror("Error", "Log file collision on characters:\n\n" + self.character + " and " + collisionCharacter +
                                "\n\nThis happens when both characters log in at exactly the same second.\n" + 
                                "This makes it impossible to know which character owns which log.\n\n" + 
                                "Please restart the client of the character you want to track to use this program.\n" + 
                                "If you already did, you can ignore this message, or delete this log file:\n" + logPath)
            raise BadLogException("log file collision")
        self.log.read()
        self.compileRegex()
            
    def readLog(self):
        logData = self.log.read()
        return super().readLog(logData)
    
    def catchup(self):
        self.log.read()
    
class BadLogException(Exception):
    pass

def ProcessCharacterLine(characterLine):
    for language, regex in _logLanguageRegex.items():
        character = re.search(regex['character'], characterLine)
        if character:
            return character.group(0), language
    raise BadLogException("not character log")