"""
Makes a Settings window
which acceps user input, and validates it in 'doSettings'
"""

import tkinter as tk
import tkinter.font as tkFont
import tkinter.colorchooser as colorchooser
import sys
import copy
import os
from settings.generalSettingsFrame import GeneralSettingsFrame
from settings.lineSettingsFrame import LineSettingsFrame
from settings.labelSettingsFrame import LabelSettingsFrame
from settings.detailSettingsFrame import DetailSettingsFrame
from settings.fleetSettingsFrame import FleetSettingsFrame
from peld import settings

class SideBar(tk.Frame):
    images = {"Tracking": "lines.png",
              "Labels": "labels.png",
              "Pilot Breakdown": "pilotDetails.png",
              "Fleet Window": "fleet.png"
             }
    
    def __init__(self, parent, mainWindow, **kwargs):
        """
        Initialize window

        Args:
            self: (todo): write your description
            parent: (todo): write your description
            mainWindow: (int): write your description
        """
        tk.Frame.__init__(self, parent, **kwargs)
        self.mainWindow = mainWindow
        self.update_idletasks()
        tk.Frame(self, height="0", width=self.winfo_reqwidth()).grid(row="0", column="0")
        
        self.counter = 0
        
    def addOption(self, title, function):
        """
        Add a new widget

        Args:
            self: (todo): write your description
            title: (str): write your description
            function: (todo): write your description
        """
        button = tk.Radiobutton(self, text=title, command=lambda:function(title), 
                                indicatoron=0, value=self.counter,
                                selectcolor="#00FFFF", bg="#FFFFFF",
                                compound="top")
        font = tkFont.Font(font=button['font'])
        font.config(weight='bold')
        button['font'] = font
        button.grid(row=self.counter, column="0", sticky="ew")
        if self.counter == 0:
            button.select()
            
        try:
            chosenImage = self.images[title]
        except KeyError:
            chosenImage = "gear.png"
            
        try:
            image = tk.PhotoImage(file=sys._MEIPASS + '\\images\\' + chosenImage)
            button.configure(image=image)
            button.image = image
        except Exception:
            try:
                path = os.path.join('PyEveLiveDPS', 'images', chosenImage)
                image = tk.PhotoImage(file=path)
                button.configure(image=image)
                button.image = image
            except Exception as e:
                pass
                
        self.counter += 1

class SettingsWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        """
        Initialize main window

        Args:
            self: (todo): write your description
            mainWindow: (todo): write your description
        """
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
        self.geometry("550x600")
        self.update_idletasks()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        generalFrame = GeneralSettingsFrame(self, self.mainWindow, relief="groove", borderwidth=1)
        generalFrame.grid(row="0", column="1", columnspan="10", rowspan="90", sticky="wens")
        
        linesFrame = LineSettingsFrame(self, self.mainWindow, relief="groove", borderwidth=1)
        linesFrame.grid(row="0", column="1", columnspan="10", rowspan="90", sticky="wens")
        linesFrame.grid_remove()
        
        labelsFrame = LabelSettingsFrame(self, self.mainWindow, relief="groove", borderwidth=1)
        labelsFrame.grid(row="0", column="1", columnspan="10", rowspan="90", sticky="wens")
        labelsFrame.grid_remove()
        
        detailsFrame = DetailSettingsFrame(self, self.mainWindow, relief="groove", borderwidth=1)
        detailsFrame.grid(row="0", column="1", columnspan="10", rowspan="90", sticky="wens")
        detailsFrame.grid_remove()
        
        fleetFrame = FleetSettingsFrame(self, self.mainWindow, relief="groove", borderwidth=1)
        fleetFrame.grid(row="0", column="1", columnspan="10", rowspan="90", sticky="wens")
        fleetFrame.grid_remove()
        
        self.options = [["General", generalFrame], ["Tracking", linesFrame], ["Labels", labelsFrame],
                        ["Pilot Breakdown", detailsFrame], ["Fleet Window", fleetFrame]]
        
        self.sideBar = SideBar(self, self.mainWindow, bg="white", width="125", relief="groove", borderwidth=1)
        self.sideBar.grid(row="0", column="0", rowspan="90", sticky="nsew", padx="1", pady="1")
        for option,frame in self.options:
            self.sideBar.addOption(option, self.switchTab)
        
        tk.Frame(self, height="20", width="10").grid(row="99", column="1", columnspan="5")
        
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row="100", column="0", columnspan="5")
        okButton = tk.Button(buttonFrame, text="  Apply All  ", command=self.doSettings)
        okButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame, text="  Cancel  ", command=self.destroy)
        cancelButton.grid(row="0", column="2")
        
        tk.Frame(self, height="20", width="10").grid(row="101", column="1", columnspan="5")
        
    def switchTab(self, title):
        """
        Switch the grid to the given title.

        Args:
            self: (todo): write your description
            title: (str): write your description
        """
        for option, frame in self.options:
            if option == title:
                frame.grid()
                if option == "Labels":
                    self.geometry("1100x600")
                elif option == "Tracking":
                    self.geometry("600x600")
                else:
                    self.geometry("550x600")
            else:
                frame.grid_remove()
            
            
        
    def doSettings(self):
        """
        Closes the current settings.

        Args:
            self: (todo): write your description
        """
        if settings.lowCPUMode:
            if not tk.messagebox.askokcancel("Are you sure?", "Applying settings while in 'Low CPU Fleet Mode'" + 
                                         " will not apply until after you end Fleet Mode.\n\n" + 
                                         "It will also remove most of your settings."):
                return
        settingsToApply = {}
        for option, frame in self.options:
            returnValue = frame.doSettings()
            if returnValue == None:
                return
            settingsToApply.update(returnValue)
        
        settings.setSettings(**settingsToApply)
        
        self.mainWindow.animator.changeSettings()
        
        self.destroy()