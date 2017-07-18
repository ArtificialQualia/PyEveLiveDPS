import platform
import os
import json
import copy

class Settings():
    defaultProfile = [ { "profile": "Default", "profileSettings": 
                        { "windowX": 0, "windowY": 0,
                         "windowHeight": 225, "windowWidth": 350,
                         "seconds": 10, "interval": 100,
                         "dpsIn": [{"color": "#FF0000", "transitionValue": 0}],
                         "dpsOut": [{"color": "#00FFFF", "transitionValue": 0}],
                         "logiOut": [], "logiIn": [],
                         "capTransfered": [], "capRecieved": [],
                         "capDamageOut": [], "capDamageIn": []  } 
                        } ]
    def __init__(self):
        if (platform.system() == "Windows"):
            path = os.environ['APPDATA'] + "\\PELD"
            filename = "PELD.json"
        else:
            path = os.environ['HOME']
            filename = ".peld"
            
        if not os.path.exists(path):
            os.mkdir(path)
            
        self.fullPath = os.path.join(path, filename)
            
        if not os.path.exists(self.fullPath):
            settingsFile = open(self.fullPath, 'w')
            json.dump(self.defaultProfile, settingsFile, indent=4)
            settingsFile.close()
            
        settingsFile = open(self.fullPath, 'r')
        self.allSettings = json.load(settingsFile)
        settingsFile.close()
        self.currentProfile = self.allSettings[0]["profileSettings"]
    
    def getCapDamageInSettings(self):
        return copy.deepcopy(self.currentProfile["capDamageIn"])
    
    def getCapDamageOutSettings(self):
        return copy.deepcopy(self.currentProfile["capDamageOut"])
    
    def getCapRecievedSettings(self):
        return copy.deepcopy(self.currentProfile["capRecieved"])
    
    def getCapTransferedSettings(self):
        return copy.deepcopy(self.currentProfile["capTransfered"])
    
    def getDpsInSettings(self):
        return copy.deepcopy(self.currentProfile["dpsIn"])
    
    def getDpsOutSettings(self):
        return copy.deepcopy(self.currentProfile["dpsOut"])
    
    def getLogiInSettings(self):
        return copy.deepcopy(self.currentProfile["logiIn"])
    
    def getLogiOutSettings(self):
        return copy.deepcopy(self.currentProfile["logiOut"])
    
    def getInterval(self):
        return self.currentProfile["interval"]
    
    def getSeconds(self):
        return self.currentProfile["seconds"]
    
    def getWindowHeight(self):
        return self.currentProfile["windowHeight"]
    
    def getWindowWidth(self):
        return self.currentProfile["windowWidth"]
    
    def getWindowX(self):
        return self.currentProfile["windowX"]
    
    def getWindowY(self):
        return self.currentProfile["windowY"]
    
    def setSettings(self, capDamageIn=None, capDamageOut=None, capRecieved=None, capTransfered=None,
                    dpsIn=None, dpsOut=None, logiIn=None, logiOut=None,
                    interval=None, seconds=None,
                    windowHeight=None, windowWidth=None, windowX=None, windowY=None):
        if not capDamageIn == None:
            self.currentProfile["capDamageIn"] = capDamageIn
        if not capDamageOut == None:
            self.currentProfile["capDamageOut"] = capDamageOut
        if not capRecieved == None:
            self.currentProfile["capRecieved"] = capRecieved
        if not capTransfered == None:
            self.currentProfile["capTransfered"] = capTransfered
        if not dpsIn == None:
            self.currentProfile["dpsIn"] = dpsIn
        if not dpsOut == None:
            self.currentProfile["dpsOut"] = dpsOut
        if not logiIn == None:
            self.currentProfile["logiIn"] = logiIn
        if not logiOut == None:
            self.currentProfile["logiOut"] = logiOut
        if not interval == None:
            self.currentProfile["interval"] = interval
        if not seconds == None:
            self.currentProfile["seconds"] = seconds
        if not windowHeight == None:
            self.currentProfile["windowHeight"] = windowHeight
        if not windowWidth == None:
            self.currentProfile["windowWidth"] = windowWidth
        if not windowX == None:
            self.currentProfile["windowX"] = windowX
        if not windowY == None:
            self.currentProfile["windowY"] = windowY
        self.writeSettings()
    
    def switchProfile(self):
        pass
    
    def writeSettings(self):
        settingsFile = open(self.fullPath, 'w')
        json.dump(self.allSettings, settingsFile, indent=4)
        settingsFile.close()
    