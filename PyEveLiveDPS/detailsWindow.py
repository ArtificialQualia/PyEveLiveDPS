"""
DetailsWindow:

Some of the styling for this window comes from BaseWindow,
"""

import tkinter as tk
from baseWindow import BaseWindow
from peld import settings

class DetailsWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        tk.Toplevel.__init__(self)
        self.baseWindow = BaseWindow(self)
        self.mainWindow = mainWindow
        
        if settings.detailsWindowShow:
            self.deiconify()
        else:
            self.withdraw()
        
        self.minsize(150,150)
        
        #Container for our "dps labels" and graph
        self.middleFrame = tk.Frame(self, background="black")
        self.middleFrame.columnconfigure(0, weight=1)
        self.middleFrame.rowconfigure(1, weight=1)
        self.middleFrame.grid(row="10", column="1", columnspan="19", sticky="news")
        self.makeDraggable(self.middleFrame)
        
        self.geometry("%sx%s+%s+%s" % (settings.detailsWindowWidth, settings.detailsWindowHeight, 
                               settings.detailsWindowX, settings.detailsWindowY))
        self.update_idletasks()
        
        self.topLabel = tk.Label(self, text="Pilot Breakdown", fg="white", background="black")
        self.topLabel.grid(row="5", column="5", columnspan="10")
        self.makeDraggable(self.topLabel)

    def __getattr__(self, attr):
        return getattr(self.baseWindow, attr)
    
    def saveWindowGeometry(self):
        settings.detailsWindowX = self.winfo_x()
        settings.detailsWindowY = self.winfo_y()
        settings.detailsWindowWidth = self.winfo_width()
        settings.detailsWindowHeight = self.winfo_height()
        
    def collapseHandler(self, collapsed):
        if collapsed:
            self.wm_attributes("-alpha", 1.0)
            self.topResizeFrame.grid()
            self.bottomResizeFrame.grid()
            self.leftResizeFrame.grid()
            self.rightResizeFrame.grid()
            self.topLeftResizeFrame.grid()
            self.topRightResizeFrame.grid()
            self.bottomLeftResizeFrame.grid()
            self.bottomRightResizeFrame.grid()
            self.makeDraggable(self.mainFrame)
            self.makeDraggable(self.middleFrame)
            self.makeDraggable(self.topLabel)
        else:
            self.wm_attributes("-alpha", settings.getCompactTransparency()/100)
            self.topResizeFrame.grid_remove()
            self.bottomResizeFrame.grid_remove()
            self.leftResizeFrame.grid_remove()
            self.rightResizeFrame.grid_remove()
            self.topLeftResizeFrame.grid_remove()
            self.topRightResizeFrame.grid_remove()
            self.bottomLeftResizeFrame.grid_remove()
            self.bottomRightResizeFrame.grid_remove()
            self.unmakeDraggable(self.mainFrame)
            self.unmakeDraggable(self.middleFrame)
            self.unmakeDraggable(self.topLabel)