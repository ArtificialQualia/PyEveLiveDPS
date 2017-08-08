import tkinter as tk
import tkinter.font as tkFont

class GeneralSettingsFrame(tk.Frame):
    def __init__(self, parent, mainWindow, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.mainWindow = mainWindow
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(4, weight=1)
        self.configure(pady=10)
        tk.Frame(self, height="0", width="1").grid(row="0", column="0")
        tk.Frame(self, height="0", width="1").grid(row="0", column="4")
        self.counter = 0
        
        checkboxValue = tk.BooleanVar()
        checkboxValue.set(self.mainWindow.settings.getGraphDisabled())
        self.graphDisabled = tk.Checkbutton(self, text="Disable graph entirely", variable=checkboxValue)
        self.graphDisabled.var = checkboxValue
        self.graphDisabled.grid(row=self.counter, column="1", columnspan="2")
        descriptor = tk.Label(self, text="Labels will still be shown")
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row=self.counter+1, column="1", columnspan="2")
        tk.Frame(self, height="20", width="10").grid(row=self.counter+2, column="1", columnspan="5")
        self.counter += 3
        
        self.secondsVar = tk.StringVar()
        self.secondsVar.set(self.mainWindow.settings.getSeconds())
        self.addSetting(self.secondsVar, "Number of seconds to average values:", 
                        "Recommended to set this value higher than your weapon cycle time")
        
        self.intervalVar = tk.StringVar()
        self.intervalVar.set(self.mainWindow.settings.getInterval())
        self.addSetting(self.intervalVar, "How often to update graph/labels in milliseconds:", 
                        "The lower you set this value, the higher your CPU usage will be")
        
        self.transparencyVar = tk.StringVar()
        self.transparencyVar.set(self.mainWindow.settings.getCompactTransparency())
        self.addSetting(self.transparencyVar, "Window transparency percentage in compact mode:", 
                        "100 is fully visible, 0 is invisible")
        
        
    def addSetting(self, var, labelText, descriptorText):
        centerFrame = tk.Frame(self)
        centerFrame.grid(row=self.counter, column="1", columnspan="2")
        label = tk.Label(centerFrame, text=labelText)
        label.grid(row=self.counter, column="1", sticky="e")
        entry = tk.Entry(centerFrame, textvariable=var, width=10)
        entry.grid(row=self.counter, column="2", sticky="w")
        descriptor = tk.Label(self, text=descriptorText)
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row=self.counter+1, column="1", columnspan="2")
        tk.Frame(self, height="20", width="10").grid(row=self.counter+2, column="1", columnspan="5")
        self.counter += 3
        
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
                                   "This is ok, but it is recommended to increase your (Seconds to average DPS) or decrease your (Graph update interval) to improve your graphing experience.\n"
                                   "Would you like to keep these settings?")
            if not okCancel:
                return
            
        if (intervalSetting < 50):
            okCancel = tk.messagebox.askokcancel("Continue?", "Setting the graph update interval to less than 50ms is generally a bad idea.  Your CPU won't like it."
                                                 "Would you like to keep these settings?")
            if not okCancel:
                return
            
        try:
            compactTransparencySetting = int(self.transparencyVar.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a number for compact transparency percentage")
            return
        if (compactTransparencySetting < 1 or compactTransparencySetting > 100):
            tk.messagebox.showerror("Error", "Please enter a value between 1-100 for compact transparency percentage")
            return  
        
        return {"seconds": secondsSetting, "interval": intervalSetting, 
                "compactTransparency": compactTransparencySetting, "graphDisabled": self.graphDisabled.var.get()}