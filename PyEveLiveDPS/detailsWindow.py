"""
DetailsWindow:

Some of the styling for this window comes from BaseWindow,
"""

import tkinter as tk
from baseWindow import BaseWindow

class DetailsWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        tk.Toplevel.__init__(self)
        self.baseWindow = BaseWindow(self)
        self.mainWindow = mainWindow
        self.settings = mainWindow.settings
        
        self.minsize(150,150)
        
        #Container for our "dps labels" and graph
        self.middleFrame = tk.Frame(self, background="black")
        self.middleFrame.columnconfigure(0, weight=1)
        self.middleFrame.rowconfigure(1, weight=1)
        self.middleFrame.grid(row="10", column="1", columnspan="19", sticky="news")
        self.makeDraggable(self.middleFrame)
        
        self.geometry("%sx%s+%s+%s" % (self.settings.detailsWindowWidth, self.settings.detailsWindowHeight, 
                               self.settings.detailsWindowX, self.settings.detailsWindowY))
        self.update_idletasks()
        
        self.topLabel = tk.Label(self, text="Pilot Breakdown", fg="white", background="black")
        self.topLabel.grid(row="5", column="5", columnspan="10")

    def __getattr__(self, attr):
        return getattr(self.baseWindow, attr)
    
    def saveWindowGeometry(self):
        self.settings.detailsWindowX = self.winfo_x()
        self.settings.detailsWindowY = self.winfo_y()
        self.settings.detailsWindowWidth = self.winfo_width()
        self.settings.detailsWindowHeight = self.winfo_height()