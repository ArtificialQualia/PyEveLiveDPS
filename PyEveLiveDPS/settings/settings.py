"""
 handles settings file management and retrieval of settings

 settings retrieval is (mostly) done in a non-pythonic way,
 hard to break those java habits!

 They should all be refactored to use @property
"""

import platform
import os
import json
import copy
import tkinter as tk
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import logging
import yaml

from localization import tr


class Settings(FileSystemEventHandler):
    defaultProfile = [{
        "profile": tr("Default"),
        "logLevel": 20,
        "fleetServer": "peld-fleet.com",
        "profileSettings": {
            "windowX":
            0,
            "windowY":
            0,
            "windowHeight":
            225,
            "windowWidth":
            350,
            "compactTransparency":
            65,
            "seconds":
            10,
            "interval":
            100,
            "graphDisabled":
            0,
            "dpsIn": [{
                "color": "#FF0000",
                "transitionValue": 0,
                "labelOnly": 0,
                "showPeak": 0
            }],
            "dpsOut": [{
                "color": "#00FFFF",
                "transitionValue": 0,
                "labelOnly": 0,
                "showPeak": 0
            }],
            "logiOut": [],
            "logiIn": [],
            "capTransfered": [],
            "capRecieved": [],
            "capDamageOut": [],
            "capDamageIn": [],
            "mining": [],
            "labels": {
                "dpsIn": {
                    "row": 0,
                    "column": 7,
                    "inThousands": 0,
                    "decimalPlaces": 1
                },
                "dpsOut": {
                    "row": 0,
                    "column": 0,
                    "inThousands": 0,
                    "decimalPlaces": 1
                },
                "logiOut": {
                    "row": 1,
                    "column": 0,
                    "inThousands": 0,
                    "decimalPlaces": 1
                },
                "logiIn": {
                    "row": 1,
                    "column": 7,
                    "inThousands": 0,
                    "decimalPlaces": 1
                },
                "capTransfered": {
                    "row": 1,
                    "column": 1,
                    "inThousands": 0,
                    "decimalPlaces": 1
                },
                "capRecieved": {
                    "row": 1,
                    "column": 6,
                    "inThousands": 0,
                    "decimalPlaces": 1
                },
                "capDamageOut": {
                    "row": 0,
                    "column": 1,
                    "inThousands": 0,
                    "decimalPlaces": 1
                },
                "capDamageIn": {
                    "row": 0,
                    "column": 6,
                    "inThousands": 0,
                    "decimalPlaces": 1
                },
                "mining": {
                    "row": 2,
                    "column": 7,
                    "inThousands": 0,
                    "decimalPlaces": 1
                }
            },
            "labelColumns": [4, 4],
            "detailsOrder": [
                "dpsOut", "dpsIn", "logiOut", "logiIn", "capTransfered",
                "capRecieved", "capDamageOut", "capDamageIn"
            ],
            "detailsWindow": {
                "show": 1,
                "width": 200,
                "height": 250,
                "x": 0,
                "y": 0
            },
            "fleetWindow": {
                "show": 1,
                "width": 600,
                "height": 400,
                "x": 200,
                "y": 200,
                "showAggregate": 1,
                "showDpsOut": 1,
                "showDpsIn": 1,
                "showLogiOut": 1
            }
        }
    }]

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

        self.lowCPUMode = False

    def on_moved(self, event):
        if not event.dest_path.endswith('.json'):
            return
        try:
            currentProfileName = self.allSettings[
                self.selectedIndex.get()]["profile"]
        except AttributeError:
            return
        settingsFile = open(self.fullPath, 'r')
        self.allSettings = json.load(settingsFile)
        settingsFile.close()
        self.mainWindow.profileMenu.delete(0, tk.END)
        self.initializeMenu(self.mainWindow)

        i = 0
        for profile in self.allSettings:
            if (profile["profile"] == currentProfileName):
                self.currentProfile = profile["profileSettings"]
                self.selectedIndex.set(i)
                self.mainWindow.event_generate('<<ChangeSettings>>')
                return
            i += 1
        self.currentProfile = self.allSettings[0]["profileSettings"]
        self.selectedIndex.set(0)
        self.mainWindow.event_generate('<<ChangeSettings>>')

    def initializeMenu(self, mainWindow):
        self.mainWindow = mainWindow
        self.selectedIndex = tk.IntVar()
        i = 0
        for profile in self.allSettings:
            self.mainWindow.profileMenu.add_radiobutton(
                label=profile["profile"],
                variable=self.selectedIndex,
                value=i,
                command=self.switchProfile)
            i += 1
        self.selectedIndex.set(0)

        self.mainWindow.profileMenu.add_separator()
        self.mainWindow.profileMenu.add_command(
            label=tr("Add New Profile"),
            command=lambda: self.addProfileWindow(add=True))
        self.mainWindow.profileMenu.add_command(
            label=tr("Duplicate Current Profile"),
            command=lambda: self.addProfileWindow(duplicate=True))
        self.mainWindow.profileMenu.add_command(
            label=tr("Rename Current Profile"),
            command=lambda: self.addProfileWindow(rename=True))
        self.mainWindow.profileMenu.add_command(
            label=tr("Delete Current Profile"), command=self.deleteProfileWindow)

    def addProfileWindow(self, add=False, duplicate=False, rename=False):
        if rename and (self.allSettings[self.selectedIndex.get()]["profile"]
                       == tr("Default")):
            tk.messagebox.showerror(
                tr("Error"), tr("You can't rename the Default profile."))
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

        tk.Frame(self.newProfileWindow, height="10",
                 width="1").grid(row="0", column="0")

        profileLabel = tk.Label(self.newProfileWindow,
                                text=tr("    New Profile Name:"))
        profileLabel.grid(row="1", column="0")
        self.profileString = tk.StringVar()
        if duplicate:
            self.profileString.set(
                self.allSettings[self.selectedIndex.get()]["profile"])
        if rename:
            self.profileString.set(
                self.allSettings[self.selectedIndex.get()]["profile"])
        profileInput = tk.Entry(self.newProfileWindow,
                                textvariable=self.profileString,
                                width=30)
        profileInput.grid(row="1", column="1")
        profileInput.focus_set()
        profileInput.icursor(tk.END)

        tk.Frame(self.newProfileWindow, height="10",
                 width="1").grid(row="2", column="0")

        buttonFrame = tk.Frame(self.newProfileWindow)
        buttonFrame.grid(row="100", column="0", columnspan="5")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="0")
        if add:
            okButton = tk.Button(buttonFrame,
                                 text=tr("  Add  "),
                                 command=lambda: self.addProfile(add=True))
            profileInput.bind("<Return>", lambda e: self.addProfile(add=True))
        elif duplicate:
            okButton = tk.Button(
                buttonFrame,
                text=tr("  Add  "),
                command=lambda: self.addProfile(duplicate=True))
            profileInput.bind("<Return>",
                              lambda e: self.addProfile(duplicate=True))
        elif rename:
            okButton = tk.Button(buttonFrame,
                                 text=tr("  Rename  "),
                                 command=lambda: self.addProfile(rename=True))
            profileInput.bind("<Return>",
                              lambda e: self.addProfile(rename=True))
        okButton.grid(row="0", column="1")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="2")
        cancelButton = tk.Button(buttonFrame,
                                 text=tr("  Cancel  "),
                                 command=self.newProfileWindow.destroy)
        cancelButton.grid(row="0", column="3")

    def addProfile(self, add=False, duplicate=False, rename=False):
        if (self.profileString.get() == tr("Default")):
            tk.messagebox.showerror(
                tr("Error"),
                tr("There can only be one profile named 'Default'"))
            return
        for profile in self.allSettings:
            if self.profileString.get() == profile["profile"]:
                tk.messagebox.showerror(
                    tr("Error"),
                    tr("There is already a profile named '{0}'").format(
                        self.profileString.get()))
                return
        if add:
            newProfile = copy.deepcopy(self.defaultProfile[0])
            newProfile["profile"] = self.profileString.get()
            self.allSettings.insert(0, newProfile)
        elif duplicate:
            newProfile = copy.deepcopy(
                self.allSettings[self.selectedIndex.get()])
            newProfile["profile"] = self.profileString.get()
            self.allSettings.insert(0, newProfile)
        elif rename:
            self.allSettings[self.selectedIndex.get(
            )]["profile"] = self.profileString.get()
            self.allSettings.insert(
                0, self.allSettings.pop(self.selectedIndex.get()))
        self.mainWindow.profileMenu.delete(0, tk.END)
        self.initializeMenu(self.mainWindow)
        self.switchProfile()
        self.newProfileWindow.destroy()

    def deleteProfileWindow(self):
        if (self.allSettings[self.selectedIndex.get()]["profile"] == tr(
                "Default")):
            tk.messagebox.showerror(
                tr("Error"), tr("You can't delete the Default profile."))
            return
        okCancel = tk.messagebox.askokcancel(
            tr("Continue?"),
            tr("Are you sure you want to delete the current profile?"))
        if not okCancel:
            return
        self.allSettings.pop(self.selectedIndex.get())
        self.mainWindow.profileMenu.delete(0, tk.END)
        self.initializeMenu(self.mainWindow)
        self.switchProfile()
        self.currentProfile = self.allSettings[0]["profileSettings"]

    def getCapDamageInSettings(self):
        if self.lowCPUMode:
            return []
        return copy.deepcopy(self.currentProfile["capDamageIn"])

    def getCapDamageOutSettings(self):
        if self.lowCPUMode:
            return []
        return copy.deepcopy(self.currentProfile["capDamageOut"])

    def getCapRecievedSettings(self):
        if self.lowCPUMode:
            return []
        return copy.deepcopy(self.currentProfile["capRecieved"])

    def getCapTransferedSettings(self):
        if self.lowCPUMode:
            return []
        return copy.deepcopy(self.currentProfile["capTransfered"])

    def getDpsInSettings(self):
        if self.lowCPUMode:
            return []
        return copy.deepcopy(self.currentProfile["dpsIn"])

    def getDpsOutSettings(self):
        if self.lowCPUMode:
            return []
        return copy.deepcopy(self.currentProfile["dpsOut"])

    def getLogiInSettings(self):
        if self.lowCPUMode:
            return []
        return copy.deepcopy(self.currentProfile["logiIn"])

    def getLogiOutSettings(self):
        if self.lowCPUMode:
            return []
        return copy.deepcopy(self.currentProfile["logiOut"])

    def getMiningSettings(self):
        if self.lowCPUMode:
            return []
        try:
            return copy.deepcopy(self.currentProfile["mining"])
        except KeyError:
            self.setSettings(mining=copy.deepcopy(
                self.defaultProfile[0]["profileSettings"]["mining"]))
            return copy.deepcopy(self.currentProfile["mining"])

    def getMiningM3Setting(self):
        if self.lowCPUMode:
            return []
        try:
            return self.currentProfile["mining"][0]["showM3"]
        except KeyError:
            return False

    def getInterval(self):
        if self.lowCPUMode:
            return 100
        return self.currentProfile["interval"]

    def getSeconds(self):
        if self.lowCPUMode:
            return 2
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

    def getGraphDisabled(self):
        if self.lowCPUMode:
            return True
        try:
            return self.currentProfile["graphDisabled"]
        except KeyError:
            self.setSettings(graphDisabled=0)
            return self.currentProfile["graphDisabled"]

    def getLabels(self):
        try:
            labelsCopy = copy.deepcopy(self.currentProfile["labels"])
            if "mining" not in labelsCopy:
                placementArray = [[x, y] for x in range(8) for y in range(8)]
                for entry in labelsCopy:
                    for place in placementArray:
                        if place[0] == labelsCopy[entry]["row"] and place[
                                1] == labelsCopy[entry]["column"]:
                            placementArray.remove(place)
                labelsCopy["mining"] = {
                    "row": placementArray[0][0],
                    "column": placementArray[0][1],
                    "inThousands": 0,
                    "decimalPlaces": 1
                }
            return labelsCopy
        except KeyError:
            self.setSettings(labels=copy.deepcopy(
                self.defaultProfile[0]["profileSettings"]["labels"]))
            return copy.deepcopy(self.currentProfile["labels"])

    def getLabelColumns(self):
        try:
            return copy.deepcopy(self.currentProfile["labelColumns"])
        except KeyError:
            self.setSettings(labelColumns=[4, 4])
            return copy.deepcopy(self.currentProfile["labelColumns"])

    @property
    def detailsWindow(self):
        return self.currentProfile.get("detailsWindow") or self.defaultProfile[
            0]["profileSettings"]["detailsWindow"]

    @property
    def detailsWindowShow(self):
        if self.lowCPUMode:
            return False
        if 'detailsWindow' in self.currentProfile and 'show' in self.currentProfile[
                "detailsWindow"]:
            return self.currentProfile["detailsWindow"]["show"]
        else:
            return self.defaultProfile[0]["profileSettings"]["detailsWindow"][
                "show"]

    @detailsWindowShow.setter
    def detailsWindowShow(self, value):
        if 'detailsWindow' in self.currentProfile:
            self.currentProfile["detailsWindow"]["show"] = value
        else:
            self.currentProfile["detailsWindow"] = {}
            self.currentProfile["detailsWindow"]["show"] = value

    @property
    def detailsWindowHeight(self):
        if 'detailsWindow' in self.currentProfile and 'height' in self.currentProfile[
                "detailsWindow"]:
            return self.currentProfile["detailsWindow"]["height"]
        else:
            return self.defaultProfile[0]["profileSettings"]["detailsWindow"][
                "height"]

    @detailsWindowHeight.setter
    def detailsWindowHeight(self, value):
        if 'detailsWindow' in self.currentProfile:
            self.currentProfile["detailsWindow"]["height"] = value
        else:
            self.currentProfile["detailsWindow"] = {}
            self.currentProfile["detailsWindow"]["height"] = value

    @property
    def detailsWindowWidth(self):
        if 'detailsWindow' in self.currentProfile and 'width' in self.currentProfile[
                "detailsWindow"]:
            return self.currentProfile["detailsWindow"]["width"]
        else:
            return self.defaultProfile[0]["profileSettings"]["detailsWindow"][
                "width"]

    @detailsWindowWidth.setter
    def detailsWindowWidth(self, value):
        if 'detailsWindow' in self.currentProfile:
            self.currentProfile["detailsWindow"]["width"] = value
        else:
            self.currentProfile["detailsWindow"] = {}
            self.currentProfile["detailsWindow"]["width"] = value

    @property
    def detailsWindowX(self):
        if 'detailsWindow' in self.currentProfile and 'x' in self.currentProfile[
                "detailsWindow"]:
            return self.currentProfile["detailsWindow"]["x"]
        else:
            return self.defaultProfile[0]["profileSettings"]["detailsWindow"][
                "x"]

    @detailsWindowX.setter
    def detailsWindowX(self, value):
        if 'detailsWindow' in self.currentProfile:
            self.currentProfile["detailsWindow"]["x"] = value
        else:
            self.currentProfile["detailsWindow"] = {}
            self.currentProfile["detailsWindow"]["x"] = value

    @property
    def detailsWindowY(self):
        if 'detailsWindow' in self.currentProfile and 'y' in self.currentProfile[
                "detailsWindow"]:
            return self.currentProfile["detailsWindow"]["y"]
        else:
            return self.defaultProfile[0]["profileSettings"]["detailsWindow"][
                "y"]

    @detailsWindowY.setter
    def detailsWindowY(self, value):
        if 'detailsWindow' in self.currentProfile:
            self.currentProfile["detailsWindow"]["y"] = value
        else:
            self.currentProfile["detailsWindow"] = {}
            self.currentProfile["detailsWindow"]["y"] = value

    @property
    def disableUpdateReminderFor(self):
        for profile in self.allSettings:
            if (profile["profile"] == tr("Default")):
                return profile.get("disableUpdateReminderFor")

    @disableUpdateReminderFor.setter
    def disableUpdateReminderFor(self, value):
        for profile in self.allSettings:
            if (profile["profile"] == tr("Default")):
                profile["disableUpdateReminderFor"] = value
        self.writeSettings()

    @property
    def logLevel(self):
        for profile in self.allSettings:
            print(f">>>>>profile['profile']={profile['profile']}")
            if (profile["profile"] == tr("Default")):
                if not profile.get("logLevel"):
                    profile["logLevel"] = self.defaultProfile[0]["logLevel"]
                    self.writeSettings()
                return profile.get("logLevel")

    @logLevel.setter
    def logLevel(self, value):
        for profile in self.allSettings:
            if (profile["profile"] == tr("Default")):
                profile["logLevel"] = value
        self.writeSettings()

    @property
    def detailsOrder(self):
        if 'detailsOrder' in self.currentProfile:
            return copy.deepcopy(self.currentProfile["detailsOrder"])
        else:
            return copy.deepcopy(
                self.defaultProfile[0]["profileSettings"]["detailsOrder"])

    @detailsOrder.setter
    def detailsOrder(self, value):
        self.currentProfile["detailsOrder"] = value
        self.writeSettings()

    @property
    def fleetServer(self):
        for profile in self.allSettings:
            if (profile["profile"] == tr("Default")):
                if not profile.get("fleetServer"):
                    profile["fleetServer"] = self.defaultProfile[0][
                        "fleetServer"]
                    self.writeSettings()
                return profile.get("fleetServer")

    @fleetServer.setter
    def fleetServer(self, value):
        for profile in self.allSettings:
            if (profile["profile"] == tr("Default")):
                profile["fleetServer"] = value
        self.writeSettings()

    @property
    def fleetWindowShow(self):
        if self.lowCPUMode:
            return False
        if 'fleetWindow' in self.currentProfile and 'show' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["show"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "show"]

    @fleetWindowShow.setter
    def fleetWindowShow(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["show"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["show"] = value

    @property
    def fleetWindowWidth(self):
        if 'fleetWindow' in self.currentProfile and 'width' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["width"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "width"]

    @fleetWindowWidth.setter
    def fleetWindowWidth(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["width"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["width"] = value

    @property
    def fleetWindowHeight(self):
        if 'fleetWindow' in self.currentProfile and 'height' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["height"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "height"]

    @fleetWindowHeight.setter
    def fleetWindowHeight(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["height"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["height"] = value

    @property
    def fleetWindowX(self):
        if 'fleetWindow' in self.currentProfile and 'x' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["x"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "x"]

    @fleetWindowX.setter
    def fleetWindowX(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["x"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["x"] = value

    @property
    def fleetWindowY(self):
        if 'fleetWindow' in self.currentProfile and 'y' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["y"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "y"]

    @fleetWindowY.setter
    def fleetWindowY(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["y"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["y"] = value

    @property
    def fleetWindowShowAggregate(self):
        if 'fleetWindow' in self.currentProfile and 'showAggregate' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["showAggregate"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "showAggregate"]

    @fleetWindowShowAggregate.setter
    def fleetWindowShowAggregate(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["showAggregate"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["showAggregate"] = value

    @property
    def fleetWindowShowDpsOut(self):
        if 'fleetWindow' in self.currentProfile and 'showDpsOut' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["showDpsOut"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "showDpsOut"]

    @fleetWindowShowDpsOut.setter
    def fleetWindowShowDpsOut(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["showDpsOut"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["showDpsOut"] = value

    @property
    def fleetWindowShowDpsIn(self):
        if 'fleetWindow' in self.currentProfile and 'showDpsIn' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["showDpsIn"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "showDpsIn"]

    @fleetWindowShowDpsIn.setter
    def fleetWindowShowDpsIn(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["showDpsIn"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["showDpsIn"] = value

    @property
    def fleetWindowShowLogiOut(self):
        if 'fleetWindow' in self.currentProfile and 'showLogiOut' in self.currentProfile[
                "fleetWindow"]:
            return self.currentProfile["fleetWindow"]["showLogiOut"]
        else:
            return self.defaultProfile[0]["profileSettings"]["fleetWindow"][
                "showLogiOut"]

    @fleetWindowShowLogiOut.setter
    def fleetWindowShowLogiOut(self, value):
        if 'fleetWindow' in self.currentProfile:
            self.currentProfile["fleetWindow"]["showLogiOut"] = value
        else:
            self.currentProfile["fleetWindow"] = {}
            self.currentProfile["fleetWindow"]["showLogiOut"] = value

    def setOverviewFiles(self, characterDict):
        for profile in self.allSettings:
            if (profile["profile"] == tr("Default")):
                profile["overviewFiles"] = characterDict
                self.writeSettings()

    def getOverviewFiles(self):
        for profile in self.allSettings:
            if (profile["profile"] == tr("Default")):
                if 'overviewFiles' not in profile:
                    if not hasattr(self, 'overviewNotificaitonShown'):
                        logging.info(
                            'No overview settings set, showing overview notification for this session...'
                        )
                        self.overviewNotificaitonShown = True
                        from settings.overviewSettings import OverviewNotification
                        OverviewNotification()
                    return {}
                return profile["overviewFiles"]

    def getOverviewFile(self, characterName):
        overviewFiles = self.getOverviewFiles()
        if characterName in overviewFiles:
            return overviewFiles[characterName]
        else:
            return overviewFiles["default"] if tr(
                "default") in overviewFiles else None

    def getOverviewSettings(self, characterName):
        overviewFile = self.getOverviewFile(characterName)
        if not overviewFile:
            return None
        try:
            with open(overviewFile, encoding='utf8') as overviewFileContent:
                return yaml.safe_load(overviewFileContent.read())
        except Exception as e:
            logging.exception('Exception loading overview settings file: ' +
                              overviewFile)
            logging.exception(e)
            tk.messagebox.showerror(
                tr("Error"),
                tr("Error loading overview settings file:")+"\n" + overviewFile)
            return None

    def setSettings(self,
                    capDamageIn=None,
                    capDamageOut=None,
                    capRecieved=None,
                    capTransfered=None,
                    dpsIn=None,
                    dpsOut=None,
                    logiIn=None,
                    logiOut=None,
                    mining=None,
                    interval=None,
                    seconds=None,
                    windowHeight=None,
                    windowWidth=None,
                    windowX=None,
                    windowY=None,
                    compactTransparency=None,
                    labels=None,
                    labelColumns=None,
                    graphDisabled=None,
                    detailsOrder=None,
                    detailsWindowShow=None):
        """
        this funciton is dumb, ugly, and deprecated.
        Settings should be set through properties
        Some cleanup would be needed to remove it entirely
        """
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
        if not mining == None:
            self.currentProfile["mining"] = mining
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
        if not labels == None:
            self.currentProfile["labels"] = labels
        if not labelColumns == None:
            self.currentProfile["labelColumns"] = labelColumns
        if not graphDisabled == None:
            self.currentProfile["graphDisabled"] = graphDisabled
        if not detailsWindowShow == None:
            self.detailsWindowShow = detailsWindowShow
        if not detailsOrder == None:
            self.currentProfile["detailsOrder"] = detailsOrder

        self.writeSettings()

    def switchProfile(self):
        self.mainWindow.saveWindowGeometry()
        self.allSettings.insert(0,
                                self.allSettings.pop(self.selectedIndex.get()))
        self.currentProfile = self.allSettings[0]["profileSettings"]
        self.mainWindow.profileMenu.delete(0, tk.END)
        self.initializeMenu(self.mainWindow)
        self.mainWindow.geometry(
            "%sx%s+%s+%s" % (self.getWindowWidth(), self.getWindowHeight(),
                             self.getWindowX(), self.getWindowY()))
        self.mainWindow.detailsWindow.geometry(
            "%sx%s+%s+%s" % (self.detailsWindowWidth, self.detailsWindowHeight,
                             self.detailsWindowX, self.detailsWindowY))
        self.mainWindow.update_idletasks()
        self.mainWindow.graphFrame.readjust(0)
        self.mainWindow.animator.changeSettings()
        self.writeSettings()

    def writeSettings(self):
        logging.info('New settings:')
        logging.info(str(self.currentProfile))
        tempFile = os.path.join(self.path, "PELD_temp.json")
        settingsFile = open(tempFile, 'w')
        json.dump(self.allSettings, settingsFile, indent=4)
        settingsFile.close()
        os.remove(self.fullPath)
        self.observer.unschedule_all()
        os.rename(tempFile, self.fullPath)
        self.observer.schedule(self, self.path, recursive=False)
