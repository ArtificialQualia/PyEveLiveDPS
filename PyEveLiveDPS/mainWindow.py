"""

"""

import logging
import os
import sys
import platform

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLabel, QFileDialog

from peld import settings, UI_PATH, IMAGE_PATH
from baseWindow import BaseWindow
from graph import DPSGraph
from animate import Animator
from collapseWindow import UncollapseWindow
from playbackFrame import PlaybackFrame
import logreader

if (platform.system() == "Windows"):
    from ctypes import windll

class MainWindow(BaseWindow): #add base window
    def __init__(self):
        loader = QUiLoader()
        self.window = loader.load(UI_PATH + 'main.ui')
        BaseWindow.__init__(self)
        #self.window2 = loader.load(UI_PATH + 'main.ui')
        #self.window2.setWindowFlags(Qt.SubWindow | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        #self.window2.show()
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        #self.window.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.window.setGeometry(settings.windowX, settings.windowY,
                               settings.windowWidth, settings.windowHeight)

        try:
            iconPath = os.path.join(sys._MEIPASS, 'app.ico')
        except AttributeError:
            iconPath = ('app.ico')
        self.window.setWindowIcon(QIcon(iconPath))

        self.addWindowButtons()

        self.statusLabel = QLabel()
        self.window.statusbar.addWidget(self.statusLabel)
        
        self.graph = DPSGraph()
        self.window.mainGrid.addWidget(self.graph, 7, 0)
        
        #self.detailsWindow = DetailsWindow(self)
        #self.fleetWindow = FleetWindow(self)
        
        # the animator is the main 'loop' of the program
        self.animator = Animator(self)
        #self.bind('<<ChangeSettings>>', lambda e: self.animator.changeSettings())

        self.characterDetector = logreader.CharacterDetector(self, self.window.menuCharacter)
        self.setupMenuActions()
        
        #self.graphFrame.readjust(0)
        #if settings.getGraphDisabled():
        #    self.graphFrame.grid_remove()
        #else:
        #    self.graphFrame.grid()

        self.window.show()

        self.collapsed = False

        logging.info('main window (and subcomponents) initialized')

    def addWindowButtons(self):
        # move menubar to grid with window mgmt buttons
        self.window.topGrid.addWidget(self.window.menubar, 0, 0)
        self.window.buttonMinimize.setIcon(QIcon(IMAGE_PATH + 'minimize.png'))
        self.window.buttonMinimize.clicked.connect(self.minimizeEvent)
        self.window.buttonCollapse.setIcon(QIcon(IMAGE_PATH + 'collapse.png'))
        self.window.buttonCollapse.clicked.connect(self.collapseEvent)
        self.window.buttonQuit.setIcon(QIcon(IMAGE_PATH + 'close.png'))
        self.window.buttonQuit.clicked.connect(self.quitEvent)

    def setupMenuActions(self):
        self.window.actionQuit.triggered.connect(self.quitEvent)
        getLogFilePath = lambda: QFileDialog.getOpenFileName(self.window, "Select log file", self.characterDetector.path)[0]
        self.window.actionPlaybackLog.triggered.connect(lambda: self.characterDetector.playbackLog(getLogFilePath()))
    
    def minimizeEvent(self):
        self.window.showMinimized()
    
    def collapseEvent(self):
        if self.collapsed:
            self.window.setWindowOpacity(1.0)
            self.uncollapseWindow.window.close()
            self.window.hide()
            self.window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.window.show()
            self.collapsed = False
        else:
            self.window.setWindowOpacity(settings.compactTransparency/100)
            self.uncollapseWindow = UncollapseWindow(self)
            self.window.hide()
            self.window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
            self.window.show()
            self.collapsed = True
        #windowsCollapseEvent(self.detailsWindow, self.collapsed)
        #windowsCollapseEvent(self.fleetWindow, self.collapsed)

    def saveWindowGeometry(self):
        #do other windows
        geometry = self.window.geometry()
        settings.windowX = geometry.x()
        settings.windowY = geometry.y()
        settings.windowWidth = geometry.width()
        settings.windowHeight = geometry.height()
        settings.writeSettings()
        
    def quitEvent(self):
        """ quitEvent is run when either the menu quit option is clicked or the quit button is clicked """
        logging.info('quit event received, saving window geometry and stopping threads')
        if hasattr(self, "caracterDetector"):
            self.characterDetector.stop()
        self.animator.stop()
        self.saveWindowGeometry()
        del self.windowMover
        logging.info('bye')
        self.window.close()
    
    def addPlaybackFrame(self, startTime, endTime):
        """ adds the playback frame underneath the graph when in 'playback' mode """
        self.mainMenu.menu.entryconfig(3, state="disabled")
        self.mainMenu.menu.delete(6)
        self.mainMenu.menu.insert_command(6, label="Stop Log Playback", command=self.characterDetector.stopPlayback)
        self.topLabel.configure(text="Playback Mode")
        self.topLabel.grid()
        self.playbackFrame = playbackFrame.PlaybackFrame(self, startTime, endTime)
        self.playbackFrame.grid(row="11", column="1", columnspan="19", sticky="news")
    
    def removePlaybackFrame(self):
        """ removes the playback frame when we leave playback mode """
        getLogFilePath = lambda: tk.filedialog.askopenfilename(initialdir=self.characterDetector.path, title="Select log file")
        self.mainMenu.menu.entryconfig(3, state="normal")
        self.mainMenu.menu.delete(6)
        self.mainMenu.menu.insert_command(6, label="Playback Log", command=lambda: self.characterDetector.playbackLog(getLogFilePath()))
        self.topLabel.grid_remove()
        self.playbackFrame.grid_remove()
        self.animator.changeSettings()
