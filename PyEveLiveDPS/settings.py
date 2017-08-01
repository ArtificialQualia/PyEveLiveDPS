import platform
import os
import json
import copy
import tkinter as tk
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class Settings(FileSystemEventHandler):
    defaultProfile = [ { "profile": "Default", "profileSettings": 
                        { "windowX": 0, "windowY": 0,
                         "windowHeight": 225, "windowWidth": 350,
                         "compactTransparency": 65,
                         "seconds": 10, "interval": 100,
                         "dpsIn": [{"color": "#FF0000", "transitionValue": 0}],
                         "dpsOut": [{"color": "#00FFFF", "transitionValue": 0}],
                         "logiOut": [], "logiIn": [],
                         "capTransfered": [], "capRecieved": [],
                         "capDamageOut": [], "capDamageIn": []  } 
                        } ]
    def __init__(self):
        self.observer = Observer()
        
        if (platform.system() == "Windows"):
            self.path = os.environ['APPDATA'] + "\\PELD"
            filename = "PELD.json"
        else:
            self.path = os.environ['HOME']
            filename = ".peld"
            
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            
        self.fullPath = os.path.join(self.path, filename)
            
        if not os.path.exists(self.fullPath):
            settingsFile = open(self.fullPath, 'w')
            json.dump(self.defaultProfile, settingsFile, indent=4)
            settingsFile.close()
            
        self.observer.schedule(self, self.path, recursive=False)
        self.observer.start()
            
        settingsFile = open(self.fullPath, 'r')
        self.allSettings = json.load(settingsFile)
        settingsFile.close()
        self.currentProfile = self.allSettings[0]["profileSettings"]
        
    def on_moved(self, event):
        currentProfileName = self.allSettings[self.selectedIndex.get()]["profile"]
        settingsFile = open(self.fullPath, 'r')
        self.allSettings = json.load(settingsFile)
        settingsFile.close()
        self.mainWindow.profileMenu.delete(0,tk.END) 
        self.initializeMenu(self.mainWindow)
        
        i = 0
        for profile in self.allSettings:
            if (profile["profile"] == currentProfileName):
                self.currentProfile = profile["profileSettings"]
                self.selectedIndex.set(i)
                self.mainWindow.graphFrame.changeSettings(self.getSeconds(), self.getInterval(), 
                                     self.getLogiInSettings(), self.getLogiOutSettings(),
                                     self.getDpsInSettings(), self.getDpsOutSettings(), 
                                     capDamageIn=self.getCapDamageInSettings(), capDamageOut=self.getCapDamageOutSettings(), 
                                     capRecieved=self.getCapRecievedSettings(), capTransfered=self.getCapTransferedSettings())
                return
            i += 1
        self.currentProfile = self.allSettings[0]["profileSettings"]
        self.selectedIndex.set(0)
        self.mainWindow.graphFrame.changeSettings(self.getSeconds(), self.getInterval(), 
                                     self.getLogiInSettings(), self.getLogiOutSettings(),
                                     self.getDpsInSettings(), self.getDpsOutSettings(), 
                                     capDamageIn=self.getCapDamageInSettings(), capDamageOut=self.getCapDamageOutSettings(), 
                                     capRecieved=self.getCapRecievedSettings(), capTransfered=self.getCapTransferedSettings())
        
    def initializeMenu(self, mainWindow):
        self.mainWindow = mainWindow
        self.selectedIndex = tk.IntVar()
        i = 0
        for profile in self.allSettings:
            self.mainWindow.profileMenu.add_radiobutton(label=profile["profile"], variable=self.selectedIndex, 
                                 value=i, command=self.switchProfile)
            i += 1
        self.selectedIndex.set(0)
        
        self.mainWindow.profileMenu.add_separator()
        self.mainWindow.profileMenu.add_command(label="Add New Profile", command=lambda: self.addProfileWindow(add=True))
        self.mainWindow.profileMenu.add_command(label="Duplicate Current Profile", command=lambda: self.addProfileWindow(duplicate=True))
        self.mainWindow.profileMenu.add_command(label="Rename Current Profile", command=lambda: self.addProfileWindow(rename=True))
        self.mainWindow.profileMenu.add_command(label="Delete Current Profile", command=self.deleteProfileWindow)
        
    def addProfileWindow(self, add=False, duplicate=False, rename=False):
        if rename and (self.allSettings[self.selectedIndex.get()]["profile"] == "Default"):
            tk.messagebox.showerror("Error", "You can't rename the Default profile.")
            return
        
        self.newProfileWindow = tk.Toplevel()
        self.newProfileWindow.wm_attributes("-topmost", True)
        
        if add:
            self.newProfileWindow.wm_title("New Profile")
        elif duplicate:
            self.newProfileWindow.wm_title("Duplicate Profile")
        elif rename:
            self.newProfileWindow.wm_title("Rename Profile")
            
        try:
            self.newProfileWindow.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.newProfileWindow.iconbitmap("app.ico")
            except Exception:
                pass
        self.newProfileWindow.geometry("320x80")
        self.newProfileWindow.update_idletasks()
        
        tk.Frame(self.newProfileWindow, height="10", width="1").grid(row="0", column="0")
        
        profileLabel = tk.Label(self.newProfileWindow, text="    New Profile Name:")
        profileLabel.grid(row="1", column="0")
        self.profileString = tk.StringVar()
        if duplicate:
            self.profileString.set(self.allSettings[self.selectedIndex.get()]["profile"])
        if rename:
            self.profileString.set(self.allSettings[self.selectedIndex.get()]["profile"])
        profileInput = tk.Entry(self.newProfileWindow, textvariable=self.profileString, width=30)
        profileInput.grid(row="1", column="1")
        profileInput.focus_set()
        profileInput.icursor(tk.END)
        
        tk.Frame(self.newProfileWindow, height="10", width="1").grid(row="2", column="0")
        
        buttonFrame = tk.Frame(self.newProfileWindow)
        buttonFrame.grid(row="100", column="0", columnspan="5")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="0")
        if add:
            okButton = tk.Button(buttonFrame, text="  Add  ", command=lambda: self.addProfile(add=True))
            profileInput.bind("<Return>", lambda e: self.addProfile(add=True))
        elif duplicate:
            okButton = tk.Button(buttonFrame, text="  Add  ", command=lambda: self.addProfile(duplicate=True))
            profileInput.bind("<Return>", lambda e: self.addProfile(duplicate=True))
        elif rename:
            okButton = tk.Button(buttonFrame, text="  Rename  ", command=lambda: self.addProfile(rename=True))
            profileInput.bind("<Return>", lambda e: self.addProfile(rename=True))
        okButton.grid(row="0", column="1")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="2")
        cancelButton = tk.Button(buttonFrame, text="  Cancel  ", command=self.newProfileWindow.destroy)
        cancelButton.grid(row="0", column="3")
        
    def addProfile(self, add=False, duplicate=False, rename=False):
        if (self.profileString.get() == "Default"):
            tk.messagebox.showerror("Error", "There can only be one profile named 'Default'")
            return
        for profile in self.allSettings:
            if self.profileString.get() == profile["profile"]:
                tk.messagebox.showerror("Error", "There is already a profile named '" + self.profileString.get() + "'")
                return
        if add:
            newProfile = copy.deepcopy(self.defaultProfile[0])
            newProfile["profile"] = self.profileString.get()
            self.allSettings.insert(0, newProfile)
        elif duplicate:
            newProfile = copy.deepcopy(self.allSettings[self.selectedIndex.get()])
            newProfile["profile"] = self.profileString.get()
            self.allSettings.insert(0, newProfile)
        elif rename:
            self.allSettings[self.selectedIndex.get()]["profile"] = self.profileString.get()
            self.allSettings.insert(0, self.allSettings.pop(self.selectedIndex.get()))
        self.mainWindow.profileMenu.delete(0,tk.END) 
        self.initializeMenu(self.mainWindow)
        self.switchProfile()
        self.newProfileWindow.destroy()
    
    def deleteProfileWindow(self):
        if (self.allSettings[self.selectedIndex.get()]["profile"] == "Default"):
            tk.messagebox.showerror("Error", "You can't delete the Default profile.")
            return
        okCancel = tk.messagebox.askokcancel("Continue?", "Are you sure you want to delete the current profile?")
        if not okCancel:
            return
        self.allSettings.pop(self.selectedIndex.get())
        self.mainWindow.profileMenu.delete(0,tk.END) 
        self.initializeMenu(self.mainWindow)
        self.switchProfile()
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
    
    def getCompactTransparency(self):
        try:
            return self.currentProfile["compactTransparency"]
        except KeyError:
            self.setSettings(compactTransparency=65)
            return self.currentProfile["compactTransparency"]
    
    def setSettings(self, capDamageIn=None, capDamageOut=None, capRecieved=None, capTransfered=None,
                    dpsIn=None, dpsOut=None, logiIn=None, logiOut=None,
                    interval=None, seconds=None,
                    windowHeight=None, windowWidth=None, windowX=None, windowY=None, compactTransparency=None):
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
        if not compactTransparency == None:
            self.currentProfile["compactTransparency"] = compactTransparency
        
        self.writeSettings()
    
    def switchProfile(self):
        self.mainWindow.saveWindowGeometry()
        self.allSettings.insert(0, self.allSettings.pop(self.selectedIndex.get()))
        self.currentProfile = self.allSettings[0]["profileSettings"]
        self.mainWindow.profileMenu.delete(0,tk.END) 
        self.initializeMenu(self.mainWindow)
        self.mainWindow.geometry("%sx%s+%s+%s" % (self.getWindowWidth(), self.getWindowHeight(), 
                                       self.getWindowX(), self.getWindowY()))
        self.mainWindow.update_idletasks()
        self.mainWindow.graphFrame.readjust(self.mainWindow.winfo_width())
        self.mainWindow.graphFrame.changeSettings(self.getSeconds(), self.getInterval(), 
                                     self.getLogiInSettings(), self.getLogiOutSettings(),
                                     self.getDpsInSettings(), self.getDpsOutSettings(), 
                                     capDamageIn=self.getCapDamageInSettings(), capDamageOut=self.getCapDamageOutSettings(), 
                                     capRecieved=self.getCapRecievedSettings(), capTransfered=self.getCapTransferedSettings())
        self.writeSettings()
    
    def writeSettings(self):
        tempFile = os.path.join(self.path, "PELD_temp.json")
        settingsFile = open(tempFile, 'w')
        json.dump(self.allSettings, settingsFile, indent=4)
        settingsFile.close()
        os.remove(self.fullPath)
        self.observer.stop()
        os.rename(tempFile, self.fullPath)
        self.observer = Observer()
        self.observer.schedule(self, self.path, recursive=False)
        self.observer.start()
    