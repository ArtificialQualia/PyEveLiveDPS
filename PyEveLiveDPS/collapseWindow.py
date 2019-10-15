"""
CollapseWindow:

A special windowsOS-only window which only contains a collapse button

This window overlays on top of the main window when PELD is in collapsed mode
  so that the rest of the window can not handle clicks (allowing the window
  underneath, i.e. EVE, to handle click events)
"""

import tkinter as tk
from peld import settings

                
class UncollapseWindow(tk.Tk):
    def __init__(self, mainWindow):
        tk.Tk.__init__(self)
        self.minsize(5,5)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-alpha", settings.getCompactTransparency()/100)
        self.columnconfigure(10, weight=1)
        self.rowconfigure(10, weight=1)
        self.configure(background="black")
        
        self.collapseButton = tk.Canvas(self, width=15, height=15, background="black",
                                    highlightbackground="white", highlightthickness="1")
        #Boxception
        self.collapseButton.create_line(5,5,12,5,fill="white")
        self.collapseButton.create_line(5,5,5,12,fill="white")
        self.collapseButton.create_line(11,11,11,5,fill="white")
        self.collapseButton.create_line(11,11,5,11,fill="white")
        
        self.collapseButton.grid(row=10, column=10, sticky="n")
        self.collapseButton.bind("<ButtonPress-1>", mainWindow.buttonDimGray)
        self.collapseButton.bind("<ButtonRelease-1>", mainWindow.collapseEvent)
        self.collapseButton.bind("<Enter>", mainWindow.buttonGray25)
        self.collapseButton.bind("<Leave>", mainWindow.buttonBlack)

        self.geometry("+%s+%s" % (mainWindow.collapseButton.winfo_rootx(), mainWindow.collapseButton.winfo_rooty()))
        self.update_idletasks()

    