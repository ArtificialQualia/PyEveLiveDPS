import platform
import os
import json

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
        return self.currentProfile["capDamageIn"]
    
    def getCapDamageOutSettings(self):
        return self.currentProfile["capDamageOut"]
    
    def getCapRecievedSettings(self):
        return self.currentProfile["capRecieved"]
    
    def getCapTransferedSettings(self):
        return self.currentProfile["capTransfered"]
    
    def getDpsInSettings(self):
        return self.currentProfile["dpsIn"]
    
    def getDpsOutSettings(self):
        return self.currentProfile["dpsOut"]
    
    def getLogiInSettings(self):
        return self.currentProfile["logiIn"]
    
    def getLogiOutSettings(self):
        return self.currentProfile["logiOut"]
    
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
        if capDamageIn:
            self.currentProfile["capDamageIn"] = capDamageIn
        if capDamageOut:
            self.currentProfile["capDamageOut"] = capDamageOut
        if capRecieved:
            self.currentProfile["capRecieved"] = capRecieved
        if capTransfered:
            self.currentProfile["capTransfered"] = capTransfered
        if dpsIn:
            self.currentProfile["dpsIn"] = dpsIn
        if dpsOut:
            self.currentProfile["dpsOut"] = dpsOut
        if logiIn:
            self.currentProfile["logiIn"] = logiIn
        if logiOut:
            self.currentProfile["logiOut"] = logiOut
        if interval:
            self.currentProfile["interval"] = interval
        if seconds:
            self.currentProfile["seconds"] = seconds
        if windowHeight:
            self.currentProfile["windowHeight"] = windowHeight
        if windowWidth:
            self.currentProfile["windowWidth"] = windowWidth
        if windowX:
            self.currentProfile["windowX"] = windowX
        if windowY:
            self.currentProfile["windowY"] = windowY
        self.writeSettings()
    
    def switchProfile(self):
        pass
    
    def writeSettings(self):
        settingsFile = open(self.fullPath, 'w')
        json.dump(self.allSettings, settingsFile, indent=4)
        settingsFile.close()
    