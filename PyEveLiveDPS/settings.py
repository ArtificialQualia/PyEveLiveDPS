import platform
import os
import json

class Settings():
    defaultProfile = [ { "profile": "Default", "profileSettings": 
                        { "windowX": 0, "windowY": 0,
                         "windowHeight": 400, "windowWidth": 400,
                         "seconds": 10, "interval": 100,
                         "logiOut": [], "logiIn": [], 
                         "dpsIn": [{"color": "#FF0000", "transitionValue": 0}],
                         "dpsOut": [{"color": "#00FFFF", "transitionValue": 0}] } 
                        } ]
    def __init__(self):
        if (platform.system() == "Windows"):
            self.path = os.environ['APPDATA'] + "\\PELD"
            self.filename = "PELD.json"
        else:
            self.path = os.environ['HOME']
            self.filename = ".peld"
            
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            
        if not os.path.exists(os.path.join(self.path, self.filename)):
            #initialize file
            pass
    
    def writeSettings(self):
        pass
    
    def readSettings(self):
        pass