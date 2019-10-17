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

class MainWindow(BaseWindow): #add base window
    def __init__(self):
        loader = QUiLoader()
        self.window = loader.load(UI_PATH + 'main.ui')
        BaseWindow.__init__(self)
        #self.window2 = loader.load(UI_PATH + 'main.ui')
        #self.window2.setWindowFlags(Qt.SubWindow | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        #self.window2.show()
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        try:
            iconPath = os.path.join(sys._MEIPASS, 'app.ico')
        except AttributeError:
            iconPath = ('app.ico')
        self.window.setWindowIcon(QIcon(iconPath))

        self.window.actionQuit.triggered.connect(self.quitEvent)
        self.addWindowButtons()

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
            self.window.setWindowOpacity(0.5)
            self.collapsed = True
        
    def quitEvent(self):
        self.window.close()
        """ quitEvent is run when either the menu quit option is clicked or the quit button is clicked 
        # if the event came from the menu, event will be 'None', otherwise the event location is checked
        # to make sure the user finished their click inside the quit button
        if not event or (event.x >= 0 and event.x <= 16 and event.y >= 0 and event.y <= 16):
            logging.info('quit event received, saving window geometry and stopping threads')
            self.saveWindowGeometry()
            self.animator.stop()
            if hasattr(self, "caracterDetector"):
                self.characterDetector.stop()
            logging.info('bye')
            self.quit()"""
    