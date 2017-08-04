import tkinter as tk
import tkinter.font as tkFont

class LabelSettingsFrame(tk.Frame):
    def __init__(self, parent, mainWindow, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.mainWindow = mainWindow
        self.columnconfigure(1, weight="1")
        
        infoLabel = tk.Label(self, text="Shit is complicated yo")
        infoLabel.grid(row="0", column="1", pady=10)
        
        gridFrame = tk.Frame(self)
        grisList = [[self.makeGridBlock(gridFrame, row, i) for row in range(8)] for i in range(8)]
        gridFrame.grid(row="1", column="1")
        
        #singleFrame = tk.Frame(self, relief="ridge", borderwidth=1)
        #singleFrame.grid(row="0", column="0", padx="5", pady="5")
        #tk.Label(singleFrame, text="DPS etc: ").grid(row="0",column="0")
        #tk.Entry(singleFrame, width=5).grid(row="0",column="1")
        
    def makeGridBlock(self, parent, row, column):
        frame = tk.Frame(parent, width="75", height="25", relief="ridge", borderwidth=1)
        frame.grid(row=row, column=column)
        return frame
        
    def doSettings(self):
        return {}