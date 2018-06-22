"""
Main file for PyEveLiveDPS

Initializes settings, the logger, then runs the main tkinter components
also spawns a separate thread to perform the update checker

"""

from settings import settings

import logging
from logging.handlers import RotatingFileHandler
import platform
import os

class App():
    def __init__(self):
        # imports happen in app init to prevent issues with files importing each other to get logger/settings
        import mainWindow
        import updateChecker
        graphWindow = mainWindow.MainWindow()
        updateCheckerThread = updateChecker.UpdateChecker()
        updateCheckerThread.start()
        graphWindow.mainloop()
    
def SetupLogger():
    """
    Initializes logger, starts at 'DEBUG' level until proper log level is retrieved from settings.
    The logger outputs to both the console and a log file that gets rolled over at 5MB
    """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    if (platform.system() == "Windows"):
        logFile = os.environ['APPDATA'] + "\\PELD" + "\\PELD.log"
    else:
        logFile = os.environ['HOME'] + "/.peld.log"
    fiveMegabytes = 1024*1024*5
    fi = RotatingFileHandler(logFile, maxBytes=fiveMegabytes, backupCount=1)
    fi.setFormatter(formatter)
    logger.addHandler(fi)
    logger.info('logger initialized')
    
def ApplyLoggerSettings():
    logger.info('changing log level to value in settings file...')
    logger.setLevel(settings.logLevel)
    logger.info('log level set to ' + str(settings.logLevel))
    
if __name__ == '__main__':
    try:
        App()
    except Exception as e:
        logger = logging.getLogger('peld')
        logger.exception(e)
else:
    # this gets hit on all imports from other files, which happens before the app starts
    # this allows easy sharing of the logger and settings references
    logger = logging.getLogger(__name__)
    SetupLogger()
    settings = settings.Settings()
    ApplyLoggerSettings()
    