"""

"""

import logging
import os
import sys

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton

from peld import settings, UI_PATH, IMAGE_PATH
from baseWindow import BaseWindow
from graph import DPSGraph
from animate import Animator
import logreader

class MainWindow(BaseWindow): #add base window
    def __init__(self):
        loader = QUiLoader()
        self.window = loader.load(UI_PATH + 'main.ui')
        BaseWindow.__init__(self)
        #self.window2 = loader.load(UI_PATH + 'main.ui')
        #self.window2.setWindowFlags(Qt.SubWindow | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        #self.window2.show()
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.window.setGeometry(settings.windowX, settings.windowY,
                               settings.windowWidth, settings.windowHeight)

        try:
            iconPath = os.path.join(sys._MEIPASS, 'app.ico')
        except AttributeError:
            iconPath = ('app.ico')
        self.window.setWindowIcon(QIcon(iconPath))

        self.window.actionQuit.triggered.connect(self.quitEvent)
        self.addWindowButtons()
        
        self.graph = DPSGraph()
        self.window.mainGrid.addWidget(self.graph, 7, 0)

        self.characterDetector = logreader.CharacterDetector(self, self.window.menuCharacter)
        
        #self.detailsWindow = DetailsWindow(self)
        #self.fleetWindow = FleetWindow(self)
        
        # the animator is the main 'loop' of the program
        self.animator = Animator(self)
        #self.bind('<<ChangeSettings>>', lambda e: self.animator.changeSettings())
        
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
    
    def minimizeEvent(self):
        self.window.showMinimized()
    
    def collapseEvent(self):
        if self.collapsed:
            self.window.setWindowOpacity(1.0)
            self.collapsed = False
        else:
            self.window.setWindowOpacity(settings.compactTransparency/100)
            self.collapsed = True

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
        self.animator.quit()
        self.saveWindowGeometry()
        logging.info('bye')
        self.window.close()
    