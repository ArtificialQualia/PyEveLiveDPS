"""

"""

import tkinter as tk
import tkinter.font as tkFont
from peld import settings

class FleetSettingsFrame(tk.Frame):
    def __init__(self, parent, mainWindow, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.mainWindow = mainWindow
        self.columnconfigure(1, weight=1)
        
        tk.Frame(self, height="20", width="10").grid(row="0", column="1", columnspan="2")

        self.row = 1
        
        self.windowDisabled = self.makeCheckbox(settings.fleetWindowShow, "Show Fleet Window", "Fleet Window is only available when PELD is in Fleet Mode")
        self.aggregateGraph = self.makeCheckbox(settings.fleetWindowShowAggregate, "Show Aggregate Stats Graph")
        self.dpsOutGraph = self.makeCheckbox(settings.fleetWindowShowDpsOut, "Show Top 3 DPS Out Graph")
        self.dpsInGrpah = self.makeCheckbox(settings.fleetWindowShowDpsIn, "Show Top 3 DPS In Graph")
        self.logiOutGraph = self.makeCheckbox(settings.fleetWindowShowLogiOut, "Show Top 3 Logi Out Graph")

    def makeCheckbox(self, initValue, boxText, description=None):
        checkboxValue = tk.BooleanVar()
        checkboxValue.set(initValue)
        checkbox = tk.Checkbutton(self, text=boxText, variable=checkboxValue)
        checkbox.var = checkboxValue
        checkbox.grid(row=self.row, column="1", columnspan="2")
        self.row += 1
        if description:
            descriptor = tk.Label(self, text=description)
            font = tkFont.Font(font=descriptor['font'])
            font.config(slant='italic')
            descriptor['font'] = font
            descriptor.grid(row=self.row, column="1", columnspan="2")
            self.row += 1
        return checkbox
                        
    def doSettings(self):
        settings.fleetWindowShow = self.windowDisabled.var.get()
        settings.fleetWindowShowAggregate = self.aggregateGraph.var.get()
        settings.fleetWindowShowDpsOut = self.dpsOutGraph.var.get()
        settings.fleetWindowShowDpsIn = self.dpsInGrpah.var.get()
        settings.fleetWindowShowLogiOut = self.logiOutGraph.var.get()
        return {}
