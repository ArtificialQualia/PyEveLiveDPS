"""
Makes a Settings window
which acceps user input, and validates it in 'doSettings'
"""

import tkinter as tk
import tkinter.font as tkFont
import tkinter.colorchooser as colorchooser
import sys


class SettingsWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        tk.Toplevel.__init__(self)
        
        self.mainWindow = mainWindow
        self.graph = mainWindow.getGraph()
        
        self.wm_attributes("-topmost", True)
        self.wm_title("PyEveLiveDPS Settings")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        self.geometry("410x600")
        self.update_idletasks()
        
        
        self.secondsVar = tk.StringVar()
        self.secondsVar.set(self.graph.getSeconds())
        secondsLabel = tk.Label(self, text="Number of seconds to average values:")
        secondsLabel.grid(row="0", column="1", sticky="e")
        secondsEntry = tk.Entry(self, textvariable=self.secondsVar, width=10)
        secondsEntry.grid(row="0", column="2")
        secondsDescriptor = tk.Label(self, text="Recommended to set this value higher than your weapon cycle time")
        font = tkFont.Font(font=secondsDescriptor['font'])
        font.config(slant='italic')
        secondsDescriptor['font'] = font
        secondsDescriptor.grid(row="1", column="1", columnspan="5")
        
        tk.Frame(self, height="20", width="395").grid(row="2", column="0", columnspan="5")
        
        self.intervalVar = tk.StringVar()
        self.intervalVar.set(self.graph.getInterval())
        intervalLabel = tk.Label(self, text="How often to update the graph in milliseconds:")
        intervalLabel.grid(row="3", column="1", sticky="e")
        intervalEntry = tk.Entry(self, textvariable=self.intervalVar, width=10)
        intervalEntry.grid(row="3", column="2")
        intervalDescriptor = tk.Label(self, text="The lower you set this value, the higher your CPU usage will be")
        intervalDescriptor['font'] = font
        intervalDescriptor.grid(row="4", column="1", columnspan="5")
        
        tk.Frame(self, height="20", width="10").grid(row="5", column="1", columnspan="5")
        tk.Frame(self, height="1", width="5").grid(row="6", column="0")
        
        linesFrame = tk.Frame(self, relief="groove", borderwidth=1)
        linesFrame.grid(row="6", column="1", columnspan="3")
        self.scrollableCanvas = tk.Canvas(linesFrame, borderwidth=0, height="400")
        canvasFrame = tk.Frame(self.scrollableCanvas)
        scrollbar = tk.Scrollbar(linesFrame, orient="vertical", command=self.scrollableCanvas.yview)
        self.scrollableCanvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.scrollableCanvas.pack(side="left", fill="both", expand=True)
        self.scrollableCanvas.create_window((0,0), window=canvasFrame, anchor="nw")
        canvasFrame.bind("<Configure>", self.onLineFrameConfigure)
        
        dpsOutFrame = tk.Frame(canvasFrame)
        dpsOutFrame.grid(row="6", column="0", columnspan="5", padx="5")
        self.dpsOutSettings = self.graph.getDpsOutCategories()
        self.addLineSection(dpsOutFrame, "DPS OUT", self.dpsOutSettings)
        
        tk.Frame(canvasFrame, height="20", width="380").grid(row="7", column="0", columnspan="5")
        
        dpsInFrame = tk.Frame(canvasFrame)
        dpsInFrame.grid(row="8", column="0", columnspan="5", padx="5")
        self.dpsInSettings = self.graph.getDpsInCategories()
        self.addLineSection(dpsInFrame, "DPS IN", self.dpsInSettings)
        
        tk.Frame(canvasFrame, height="20", width="10").grid(row="9", column="1", columnspan="5")
        
        logiOutFrame = tk.Frame(canvasFrame)
        logiOutFrame.grid(row="10", column="0", columnspan="5", padx="5")
        self.logiOutSettings = self.graph.getLogiOutCategories()
        self.addLineSection(logiOutFrame, "logistics OUT", self.logiOutSettings)
        
        tk.Frame(canvasFrame, height="20", width="10").grid(row="11", column="1", columnspan="5")
        
        logiInFrame = tk.Frame(canvasFrame)
        logiInFrame.grid(row="12", column="0", columnspan="5", padx="5")
        self.logiInSettings = self.graph.getLogiInCategories()
        self.addLineSection(logiInFrame, "logistics IN", self.logiInSettings)
        
        tk.Frame(canvasFrame, height="20", width="10").grid(row="13", column="1", columnspan="5")
        
        capTransferedFrame = tk.Frame(canvasFrame)
        capTransferedFrame.grid(row="14", column="0", columnspan="5", padx="5")
        self.capTransferedSettings = []
        self.addLineSection(capTransferedFrame, "capacitor xfer OUT", self.capTransferedSettings)
        
        tk.Frame(canvasFrame, height="20", width="10").grid(row="15", column="1", columnspan="5")
        
        capRecievedFrame = tk.Frame(canvasFrame)
        capRecievedFrame.grid(row="16", column="0", columnspan="5", padx="5")
        self.capRecievedSettings = []
        self.addLineSection(capRecievedFrame, "capacitor xfer (including +nos) IN", self.capRecievedSettings)
        
        tk.Frame(canvasFrame, height="20", width="10").grid(row="17", column="1", columnspan="5")
        
        capDamageOutFrame = tk.Frame(canvasFrame)
        capDamageOutFrame.grid(row="18", column="0", columnspan="5", padx="5")
        self.capDamageOutSettings = []
        self.addLineSection(capDamageOutFrame, "capacitor drain OUT", self.capDamageOutSettings)
        
        tk.Frame(canvasFrame, height="20", width="10").grid(row="19", column="1", columnspan="5")
        
        capDamageInFrame = tk.Frame(canvasFrame)
        capDamageInFrame.grid(row="20", column="0", columnspan="5", padx="5")
        self.capDamageInSettings = []
        self.addLineSection(capDamageInFrame, "capacitor drain IN", self.capDamageInSettings)
        
        tk.Frame(self, height="20", width="10").grid(row="99", column="1", columnspan="5")
        
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row="100", column="0", columnspan="5")
        okButton = tk.Button(buttonFrame, text="  Apply  ", command=self.doSettings)
        okButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame, text="  Cancel  ", command=self.destroy)
        cancelButton.grid(row="0", column="2")
        
    def onLineFrameConfigure(self, event):
        self.scrollableCanvas.configure(scrollregion=self.scrollableCanvas.bbox("all"))
        
    def addLineSection(self, frame, text, settingsList):
        sectionLabel = tk.Label(frame, text="Enable " + text + " tracking?")
        sectionLabel.grid(row="0", column="0", sticky="e")
        font = tkFont.Font(font=sectionLabel['font'])
        font.config(weight='bold')
        sectionLabel['font'] = font
        innerFrame = tk.Frame(frame, borderwidth=1, relief="sunken", padx="5")
        innerFrame.grid(row="1", column="0", columnspan="2")
        checkboxValue = tk.BooleanVar()
        if len(settingsList) == 0:
            checkboxValue.set(False)
        else:
            checkboxValue.set(True)
            self.addLineCustomizationSection(innerFrame, text, checkboxValue, settingsList)
        sectionCheckbox = tk.Checkbutton(frame, variable=checkboxValue, 
                                         command=lambda:self.addLineCustomizationSection(innerFrame, text, checkboxValue, settingsList))
        sectionCheckbox.grid(row="0", column="1", sticky="w")
    
    def addLineCustomizationSection(self, frame, text, checkboxValue, settingsList):
        if checkboxValue.get():
            frame.grid()
            innerLabel = tk.Label(frame, text="Color and threshold (when to change colors) for " + text + " line:")
            innerLabel.grid(row="0", column="0")
            font = tkFont.Font(font=innerLabel['font'])
            font.config(slant='italic')
            innerLabel['font'] = font
            if len(settingsList) == 0:
                settingsList.append({"transitionValue": 0, "color": "#FFFFFF"})
            for setting in settingsList:
                valueHolder = setting["transitionValue"]
                setting["transitionValue"] = tk.StringVar()
                setting["transitionValue"].set(valueHolder)
            innerFrame = tk.Frame(frame)
            innerFrame.grid(row="1", column="0", columnspan="5")
            self.expandCustomizationSettings(innerFrame, settingsList)
        else:
            for child in frame.winfo_children():
                child.destroy()
            frame.grid_remove()
            settingsList.clear()
        
    def expandCustomizationSettings(self, frame, settingsList):
        index = 0
        for setting in settingsList:
            removeButton = tk.Button(frame, text="X", command=lambda i=index:self.removeLine(i, settingsList, frame))
            font = tkFont.Font(font=removeButton['font'])
            font.config(weight='bold')
            removeButton['font'] = font
            removeButton.grid(row=index, column="0")
            initialLabel = tk.Label(frame, text="Threshold when the line changes color:")
            initialLabel.grid(row=index, column="1")
            initialThreshold = tk.Entry(frame, textvariable=settingsList[index]["transitionValue"], width=10)
            if (index == 0):
                initialThreshold.configure(state="disabled")
                removeButton.configure(state="disabled", borderwidth="0", text=" X ")
            initialThreshold.grid(row=index, column="2")
            initialLabel = tk.Label(frame, text="Color:")
            initialLabel.grid(row=index, column="3")
            colorButton = tk.Button(frame, text="    ", 
                                    command=lambda i=index:self.colorWindow(settingsList[i], colorButton), 
                                    bg=settingsList[index]["color"])
            colorButton.grid(row=index, column="4")
            index += 1
        
        addLineButton = tk.Button(frame, text="Add Another Threshold",
                                  command=lambda:self.addLine(settingsList, frame))
        addLineButton.grid(row="100", column="1")
            
    def addLine(self, settingsList, dpsFrame):
        lineNumber = len(settingsList)
        settingsList.append({"transitionValue": "", "color": "#FFFFFF"})
        settingsList[lineNumber]["transitionValue"] = tk.StringVar()
        settingsList[lineNumber]["transitionValue"].set(str(100*lineNumber))
        
        
        removeButton = tk.Button(dpsFrame, text="X", command=lambda:self.removeLine(lineNumber, settingsList, dpsFrame))
        font = tkFont.Font(font=removeButton['font'])
        font.config(weight='bold')
        removeButton['font'] = font
        removeButton.grid(row=lineNumber, column="0")
        lineLabel = tk.Label(dpsFrame, text="Threshold when the line changes color:")
        lineLabel.grid(row=lineNumber, column="1")
        initialThreshold = tk.Entry(dpsFrame, textvariable=settingsList[lineNumber]["transitionValue"], width=10)
        initialThreshold.grid(row=lineNumber, column="2")
        initialLabel = tk.Label(dpsFrame, text="Color:")
        initialLabel.grid(row=lineNumber, column="3")
        colorButton = tk.Button(dpsFrame, text="    ", 
                                command=lambda:self.colorWindow(settingsList[lineNumber], colorButton), 
                                bg=settingsList[lineNumber]["color"])
        colorButton.grid(row=lineNumber, column="4")
        
    def removeLine(self, index, settingsList, dpsFrame):
        settingsList.pop(index)
        for child in dpsFrame.winfo_children():
            child.destroy()
        self.expandCustomizationSettings(dpsFrame, settingsList)
        
    def colorWindow(self, settingsListValue, button):
        x,settingsListValue["color"] = colorchooser.askcolor()
        button.configure(bg=settingsListValue["color"])
        
    def doSettings(self):
        try:
            secondsSetting = int(self.secondsVar.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a number for number of seconds to average DPS")
            return
        if (secondsSetting < 2 or secondsSetting > 600):
            tk.messagebox.showerror("Error", "Please enter a value between 2-600 for number of seconds to average DPS")
            return  
        
        try:
            intervalSetting = int(self.intervalVar.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a number for milliseconds to update graph")
            return
        if (intervalSetting < 10 or intervalSetting > 1000):
            tk.messagebox.showerror("Error", "Please enter a value between 10-1000 for milliseconds to update graph")
            return
        
        if ((secondsSetting*1000)/intervalSetting <= 10):
            tk.messagebox.showerror("Error", "(Seconds to average DPS*1000)/(Graph update interval) must be > 10.\n" +
                                   "If it is less than 10, we won't have enough data to draw an accurate graph!")
            return
        
        if ((secondsSetting*1000)/intervalSetting < 20):
            okCancel = tk.messagebox.askokcancel("Continue?", "(Seconds to average DPS*1000)/(Graph update interval)\n is < 20\n" +
                                   "This is ok, but it is recommended to increase your (Seconds to average DPS) or \n" +
                                   "decrease your (Graph update interval) to improve your graphing experience.\n"
                                   "Would you like to keep these settings?")
            if not okCancel:
                return
            
        if (intervalSetting < 50):
            okCancel = tk.messagebox.askokcancel("Continue?", "Setting the graph update interval to less than 50ms\n" +
                                                 "Is generally a bad idea.  Your CPU won't like it."
                                                 "Would you like to keep these settings?")
            if not okCancel:
                return
            
        self.convertBackValues(self.dpsInSettings)
        self.convertBackValues(self.dpsOutSettings)
        self.convertBackValues(self.logiInSettings)
        self.convertBackValues(self.logiOutSettings)
            
        #Isn't python the coolest language? Look how easy this is:
        self.dpsInSettings = sorted(self.dpsInSettings, key=lambda setting: setting["transitionValue"])
        self.dpsOutSettings = sorted(self.dpsOutSettings, key=lambda setting: setting["transitionValue"])
        self.logiInSettings = sorted(self.logiInSettings, key=lambda setting: setting["transitionValue"])
        self.logiOutSettings = sorted(self.logiOutSettings, key=lambda setting: setting["transitionValue"])
        
        self.graph.changeSettings(secondsSetting, intervalSetting, 
                                     self.logiInSettings, self.logiOutSettings,
                                     self.dpsInSettings, self.dpsOutSettings)
        
        self.destroy()
        
    def convertBackValues(self, settingsList):
        for setting in settingsList:
            try:
                int(setting["transitionValue"].get())
            except ValueError:
                tk.messagebox.showerror("Error", "Please enter a number for all line color threshold values")
                return
        for setting in settingsList:
            setting["transitionValue"] = int(setting["transitionValue"].get())