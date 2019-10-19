"""
Main file for PyEveLiveDPS

Initializes settings, the logger, then runs the main tkinter components
also spawns a separate thread to perform the update checker

"""

import multiprocessing
import logging
from logging.handlers import RotatingFileHandler
import platform
import os
import sys
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from PySide2.QtWidgets import QApplication

from settings import settings

try:
    UI_PATH = os.path.join(sys._MEIPASS, 'PyEveLiveDPS', 'ui', '')
    IMAGE_PATH = os.path.join(sys._MEIPASS, 'PyEveLiveDPS', 'images', '')
except AttributeError:
    UI_PATH = os.path.join('.', 'PyEveLiveDPS', 'ui', '')
    IMAGE_PATH = os.path.join('.', 'PyEveLiveDPS', 'images', '')
settings = settings.Settings()


class App():
    def __init__(self):
        # imports happen in app init to prevent issues with files importing each other to get logger/settings
        import mainWindow
        #import updateChecker
        SetupLogger()
        #graphWindow = mainWindow.MainWindow()
        #updateCheckerThread = updateChecker.UpdateChecker()
        #updateCheckerThread.start()
        #graphWindow.mainloop()
        app = QApplication()
        main = mainWindow.MainWindow()
        app.exec_()
    
def SetupLogger():
    """
    Initializes logger, starts at 'DEBUG' level until proper log level is retrieved from settings.
    The logger outputs to both the console and a log file that gets rolled over at 5MB
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    if (platform.system() == "Windows"):
        logPath = os.environ['APPDATA'] + "\\PELD"
        logFile = logPath + "\\PELD.log"
        if not os.path.exists(logPath):
            os.mkdir(logPath)
    else:
        logFile = os.environ['HOME'] + "/.peld.log"
    
    fiveMegabytes = 1024*1024*5
    fi = RotatingFileHandler(logFile, maxBytes=fiveMegabytes, backupCount=1, encoding='utf-8')
    fi.setFormatter(formatter)
    logger.addHandler(fi)
    logger.info('logger initialized')
    logger.info('changing log level to value in settings file...')
    logger.setLevel(settings.logLevel)
    logger.info('log level set to ' + str(settings.logLevel))
    
if __name__ == '__main__':
    multiprocessing.freeze_support()
    try:
        App()
    except Exception as e:
        logging.exception(e)
    