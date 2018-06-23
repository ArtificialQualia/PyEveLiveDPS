"""
DetailsWindow:

Some of the styling for this window comes from BaseWindow,
"""

import tkinter as tk
from baseWindow import BaseWindow
from peld import settings
import detailsHandler

class DetailsWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        tk.Toplevel.__init__(self)
        self.baseWindow = BaseWindow(self)
        self.mainWindow = mainWindow
        
        self.columnconfigure(5, weight=1)
        self.rowconfigure(10, weight=1)
        
        if settings.detailsWindowShow:
            self.deiconify()
        else:
            self.withdraw()
        
        self.minsize(150,200)
        
        self.detailsHandler = detailsHandler.DetailsHandler(self, lambda c:self.makeAllChildrenDraggable(c), background="black")
        self.detailsHandler.grid(row="10", column="1", columnspan="19", sticky="news")
        self.makeDraggable(self.detailsHandler)
        
        self.geometry("%sx%s+%s+%s" % (settings.detailsWindowWidth, settings.detailsWindowHeight, 
                               settings.detailsWindowX, settings.detailsWindowY))
        self.update_idletasks()
        
        self.topLabel = tk.Label(self, text="Pilot Breakdown", fg="white", background="black")
        self.topLabel.grid(row="5", column="5", columnspan="10")
        self.makeDraggable(self.topLabel)
        
        tk.Frame(self, highlightthickness="1", highlightbackground="dim gray", background="black").grid(row="6", column="5", sticky="we", columnspan="10")

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
            self.makeDraggable(self.detailsHandler)
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
            self.unmakeDraggable(self.detailsHandler)
            self.unmakeDraggable(self.topLabel)