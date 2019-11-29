
from PySide2.QtWidgets import QMessageBox, QStyle, QGroupBox, QGridLayout, QLabel, QPushButton, QMessageBox, QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt
from PySide2.QtGui import QMovie

from peld import settings, UI_PATH, IMAGE_PATH
import sys
import time
import platform
import os
import yaml
import logging

class OverviewNotification():
    def __init__(self, characterDetector):
        self.characterDetector = characterDetector
        loader = QUiLoader()
        self.window = loader.load(UI_PATH + 'overviewNotification.ui')
        self.window.setAttribute(Qt.WA_QuitOnClose, False)
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint)
        warningIcon = self.window.style().standardIcon(QStyle.SP_MessageBoxWarning)
        self.window.icon.setPixmap(warningIcon.pixmap(30,30))
        self.window.openSettings.pressed.connect(self.openSettings)
        self.window.useDefault.pressed.connect(self.useDefault)
        self.window.show()

    def openSettings(self):
        self.settingsWindow = OverviewSettingsWindow(self.characterDetector)
        self.window.close()

    def useDefault(self):
        settings.overviewFiles = {'default': None}
        self.window.close()


class OverviewSettingsWindow():
    def __init__(self, characterDetector):
        self.characterDetector = characterDetector
        loader = QUiLoader()
        self.window = loader.load(UI_PATH + 'overviewSettings.ui')
        self.window.setAttribute(Qt.WA_QuitOnClose, False)
        self.gif = QMovie(IMAGE_PATH + 'peld-overview-export.gif')
        self.window.gif.setMovie(self.gif)
        self.gif.setSpeed(70)
        self.gif.start()

        if (platform.system() == "Windows"):
            import win32com.client
            oShell = win32com.client.Dispatch("Wscript.Shell")
            self.overviewPath = oShell.SpecialFolders("MyDocuments") + "\\EVE\\Overview\\"
        else:
            self.overviewPath = os.environ['HOME'] + "/Documents/EVE/Overview/"

        self.frameLine = 5
        characters = []
        for logReader in self.characterDetector.getLogReaders():
            characters.append(logReader.character)
        self.overviewFiles = settings.overviewFiles
        if self.overviewFiles == {}:
            self.overviewFiles['default'] = None
            self.addSetting('default', default=True)
        else:
            if 'default' in self.overviewFiles:
                self.addSetting('default', default=True)
            for character in self.overviewFiles:
                if character != 'default':
                    if character in characters:
                        characters.remove(character)
                    self.addSetting(character)
        for character in characters:
            self.addSetting(character)
        
        self.window.applyButton.pressed.connect(self.doSettings)
        self.window.cancelButton.pressed.connect(self.window.close)

        self.window.show()
            
    def addSetting(self, characterName, default=None):
        if characterName in self.overviewFiles:
            overviewFile = self.overviewFiles[characterName]
        else:
            overviewFile = 'Using PELD default overview setting'
        fileString = overviewFile or 'Using default EVE overview settings'

        if default:
            characterName += ' (this is the overview setting applied to new characters)'
        frame = QGroupBox(characterName, self.window.scrollAreaContent)
        self.window.scrollAreaContent.layout().addWidget(frame, self.frameLine, 0)
        self.frameLine += 1
        frameLayout = QGridLayout()
        frame.setLayout(frameLayout)

        fileLabel = QLabel(fileString)
        frameLayout.addWidget(fileLabel, 1, 0, 1, 10)

        openOverviewFile = lambda: self.processOverviewFile(characterName, fileLabel,
                           QFileDialog.getOpenFileName(self.window, "Select overview file", self.overviewPath))
        openOverviewButton = QPushButton("Select overview settings file")
        openOverviewButton.pressed.connect(openOverviewFile)
        frameLayout.addWidget(openOverviewButton, 2, 0)

        revertEVEDefaultFunc = lambda: self.revertEVEDefault(characterName, fileLabel)
        revertEVEDefaultButton = QPushButton("Use default EVE overview settings")
        revertEVEDefaultButton.pressed.connect(revertEVEDefaultFunc)
        frameLayout.addWidget(revertEVEDefaultButton, 2, 1)

        if not default:
            revertDefaultFunc = lambda: self.revertPELDDefault(characterName, fileLabel)
            revertDefaultButton = QPushButton("Use PELD default overview setting")
            revertDefaultButton.pressed.connect(revertDefaultFunc)
            frameLayout.addWidget(revertDefaultButton, 2, 2)

    def processOverviewFile(self, characterName, label, path):
        path = path[0]
        if not path:
            return
        try:
            with open(path, encoding='utf8') as overviewFileContent:
                overviewSettings = yaml.safe_load(overviewFileContent.read())
                if 'shipLabelOrder' not in overviewSettings or 'shipLabels' not in overviewSettings:
                    QMessageBox.warning(self.window, "Error", "Overview settings not in YAML file:\n"+path)
                    return
                for shipLabel in overviewSettings['shipLabels']:
                    shipLabel[1] = dict(shipLabel[1])
                    if not shipLabel[1]['state']:
                        if shipLabel[1]['type'] in ['pilot name', 'ship type']:
                            logging.warning(shipLabel[1]['type'] + " not in "+str(path))
                            QMessageBox.warning(self.window, "Error: The '"+shipLabel[1]['type']+"' is disabled in these " + \
                              "overview settings.  You need to enable the display of this label for PELD to track properly.\n\n" + \
                              "You can enable it on the 'ships' tab of your overview settings in EVE.\n\n" + \
                              "Don't forget to export your overview settings again!")
        except:
            logging.error("Error processing overview settings file: "+str(path))
            QMessageBox.warning(self.window, "Error", "Error processing overview settings file:\n"+str(path))
            return
            
        self.overviewFiles[characterName] = path
        label.setText(path)

    def revertPELDDefault(self, characterName, label):
        self.overviewFiles[characterName] = "Using PELD default overview setting"
        label.setText(self.overviewFiles[characterName])

    def revertEVEDefault(self, characterName, label):
        self.overviewFiles[characterName] = "Using default EVE overview settings"
        label.setText(self.overviewFiles[characterName])
        
    def doSettings(self):
        toDelete = []
        for characterName, settingsFile in self.overviewFiles.items():
            if settingsFile == "Using PELD default overview setting":
                toDelete.append(characterName)
            elif settingsFile == "Using default EVE overview settings":
                self.overviewFiles[characterName] = None
        for character in toDelete:
            del self.overviewFiles[character]
        
        settings.overviewFiles = self.overviewFiles

        for logReader in self.characterDetector.getLogReaders():
            logReader.compileRegex()
        
        self.window.close()