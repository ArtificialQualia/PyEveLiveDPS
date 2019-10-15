"""
MainWindow:

Some of the styling for this window comes from BaseWindow,
 but as this is the main window in the app some additional
 customizations are layered on.
 
It also holds many of the main components for the app, like animator
"""

import tkinter as tk
import tkinter.font as tkFont
import platform
import sys
import graph
import logreader
import playbackFrame
import settings.settingsWindow as settingsWindow
import simulationWindow
import labelHandler
import animate
import fleetConnectionWindow
import logging
from peld import settings
from baseWindow import BaseWindow
from detailsWindow import DetailsWindow
from collapseWindow import UncollapseWindow
from fleetWindow import FleetWindow
if (platform.system() == "Windows"):
    from ctypes import windll


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.baseWindow = BaseWindow(self)
        self.minsize(175,50)
        
        # Set title and icon for alt+tab and taskbar
        self.wm_title("PyEveLiveDPS")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        
        self.addToTaskbar()
        
        # label that appears at the top of the window in special modes like simulation and playback modes
        self.topLabel = tk.Label(self, text="Simulation Mode", fg="white", background="black")
        font = tkFont.Font(font=self.topLabel['font'])
        font.config(slant='italic')
        self.topLabel['font'] = font
        self.topLabel.grid(row="5", column="5", columnspan="8")
        self.topLabel.grid_remove()
        self.makeDraggable(self.topLabel)
        
        # Other items for setting up the window
        self.addQuitButton()
        self.addCollapseButton(self, row="5", column="17")
        tk.Frame(self, height=1, width=5, background="black").grid(row="5", column="16")
        self.addMinimizeButton(self, row="5", column="15")
        
        self.addMenus()
        
        # Container for our "dps labels" and graph
        self.middleFrame = tk.Frame(self, background="black")
        self.middleFrame.columnconfigure(0, weight=1)
        self.middleFrame.rowconfigure(1, weight=1)
        self.middleFrame.grid(row="10", column="1", columnspan="19", sticky="news")
        self.makeDraggable(self.middleFrame)
        self.middleFrame.bind("<Map>", self.showEvent)
        self.protocol("WM_TAKE_FOCUS", lambda: self.showEvent(None))
        
        self.labelHandler = labelHandler.LabelHandler(self.middleFrame, background="black")
        self.labelHandler.grid(row="0", column="0", sticky="news")
        self.makeDraggable(self.labelHandler)
        
        # set the window size and position from the settings
        self.geometry("%sx%s+%s+%s" % (settings.getWindowWidth(), settings.getWindowHeight(), 
                                       settings.getWindowX(), settings.getWindowY()))
        self.update_idletasks()
        
        # The hero of our app
        self.graphFrame = graph.DPSGraph(self.middleFrame, background="black", borderwidth="0")
        self.graphFrame.grid(row="1", column="0", columnspan="3", sticky="nesw")
        self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
        
        # details window is a child of the main window, but the window will be hidden based on the profile settings
        self.detailsWindow = DetailsWindow(self)

        self.fleetWindow = FleetWindow(self)
        
        # the animator is the main 'loop' of the program
        self.animator = animate.Animator(self)
        self.bind('<<ChangeSettings>>', lambda e: self.animator.changeSettings())
        
        self.graphFrame.readjust(0)
        if settings.getGraphDisabled():
            self.graphFrame.grid_remove()
        else:
            self.graphFrame.grid()
            
        self.labelHandler.lift(self.graphFrame)
        self.makeAllChildrenDraggable(self.labelHandler)
        
        logging.info('main window (and subcomponents) initialized')
        
    def __getattr__(self, attr):
        return getattr(self.baseWindow, attr)

    def addToTaskbar(self):
        # Magic to make the window appear on the windows taskbar
        try:
            if (self.platform == "Windows"):
                self.update_idletasks()
                GWL_EXSTYLE=-20
                WS_EX_APPWINDOW=0x00040000
                WS_EX_TOOLWINDOW=0x00000080
                hwnd = windll.user32.GetParent(self.winfo_id())
                try:
                    style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
                except AttributeError:
                    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                style = style & ~WS_EX_TOOLWINDOW
                style = style | WS_EX_APPWINDOW
                try:
                    res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
                except AttributeError:
                    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
                # re-assert the new window style
                self.wm_withdraw()
                self.wm_deiconify()
                self.update_idletasks()
        except Exception as e:
            logging.exception("Error adding PELD to Windows taskbar.  This should never happen, but execution can continue normally.")
            logging.exception(e)
        
    def addMenus(self):
        # character menu options are added dynamically by CharacterDetector, so we pass this into that
        self.characterMenu = tk.Menubutton(text="Character...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.characterMenu.grid(row="5", column="2")
        self.characterMenu.menu = tk.Menu(self.characterMenu, tearoff=False)
        self.characterMenu["menu"] = self.characterMenu.menu
        self.characterDetector = logreader.CharacterDetector(self, self.characterMenu)
        
        # Set up file menu options
        self.mainMenu = tk.Menubutton(text="File...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.mainMenu.grid(row="5", column="1")
        self.mainMenu.menu = tk.Menu(self.mainMenu, tearoff=False)
        self.mainMenu["menu"] = self.mainMenu.menu
        self.mainMenu.menu.add_command(label="Edit Profile Settings", command=lambda: settingsWindow.SettingsWindow(self))
        
        # add all the profiles from settings into the menu
        self.profileMenu = tk.Menu(self.mainMenu, tearoff=False)
        settings.initializeMenu(self)
        
        self.mainMenu.menu.add_cascade(label="Profile", menu=self.profileMenu)
        self.mainMenu.menu.add_separator()
        self.mainMenu.menu.add_command(label="Fleet Mode", command=lambda: fleetConnectionWindow.FleetWindow(self))
        self.mainMenu.menu.add_separator()
        self.mainMenu.menu.add_command(label="Simulate Input", command=lambda: simulationWindow.SimulationWindow(self))
        getLogFilePath = lambda: tk.filedialog.askopenfilename(initialdir=self.characterDetector.path, title="Select log file")
        self.mainMenu.menu.add_command(label="Playback Log", command=lambda: self.characterDetector.playbackLog(getLogFilePath()))
        self.mainMenu.menu.add_separator()
        self.mainMenu.menu.add_command(label="Quit", command=self.quitEvent)
    
    def addQuitButton(self):
        """ draws and places the quit icon on the main window """
        self.quitButton = tk.Canvas(width=15, height=15, background="black",
                                    highlightbackground="white", highlightthickness="1")
        self.quitButton.create_line(0,0,16,16,fill="white")
        self.quitButton.create_line(1,15,16,0,fill="white")
        self.quitButton.grid(row="5", column="19", sticky="ne")
        self.quitButton.bind("<ButtonPress-1>", self.buttonDimGray)
        self.quitButton.bind("<ButtonRelease-1>", self.quitEvent)
        self.quitButton.bind("<Enter>", self.buttonGray25)
        self.quitButton.bind("<Leave>", self.buttonBlack)
        
        tk.Frame(self, height=1, width=5, background="black").grid(row="5", column="18")
        
        self.rightSpacerFrame = tk.Frame(width=5, height=5, background="black")
        self.rightSpacerFrame.grid(row="0", column="100", rowspan="50")
        self.rightSpacerFrame.grid_remove()
        
    def addCollapseButton(self, parent, row, column):
        """ darws and places the collapse icon next to the quit button """
        self.collapsed = False
        self.collapseButton = tk.Canvas(parent, width=15, height=15, background="black",
                                    highlightbackground="white", highlightthickness="1")
        #Boxception
        self.collapseButton.create_line(5,5,12,5,fill="white")
        self.collapseButton.create_line(5,5,5,12,fill="white")
        self.collapseButton.create_line(11,11,11,5,fill="white")
        self.collapseButton.create_line(11,11,5,11,fill="white")
        
        self.collapseButton.grid(row=row, column=column, sticky="n")
        self.collapseButton.bind("<ButtonPress-1>", self.buttonDimGray)
        self.collapseButton.bind("<ButtonRelease-1>", self.collapseEvent)
        self.collapseButton.bind("<Enter>", self.buttonGray25)
        self.collapseButton.bind("<Leave>", self.buttonBlack)
    
    def collapseEvent(self, event):
        """ This is called when the collapse icon is clicked
        it also calls the same event on the details window """
        logging.debug('window collapse event occured')
        self.detailsWindow.collapseHandler(self.collapsed)
        self.fleetWindow.collapseHandler(self.collapsed)
        if self.collapsed:
            if (self.platform == "Windows"):
                self.uncollapseWindow.destroy()
                windowsCollapseEvent(self, False)
                windowsCollapseEvent(self.detailsWindow, False)
                windowsCollapseEvent(self.fleetWindow, False)
            self.wm_attributes("-alpha", 1.0)
            self.rightSpacerFrame.grid_remove()
            self.showResizeFrames()
            self.makeDraggable(self.topLabel)
            self.makeDraggable(self.mainFrame)
            self.makeDraggable(self.middleFrame)
            self.makeDraggable(self.labelHandler)
            self.makeAllChildrenDraggable(self.labelHandler)
            self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
            self.mainMenu.grid()
            self.characterMenu.grid()
            self.quitButton.grid()
            self.minimizeButton.grid()
            self.collapseButton.destroy()
            self.addCollapseButton(self, row="5", column="17")
            self.collapsed = False
        else:
            self.wm_attributes("-alpha", settings.getCompactTransparency()/100)
            self.hideResizeFrames()
            self.rightSpacerFrame.grid()
            self.unmakeDraggable(self.topLabel)
            self.unmakeDraggable(self.mainFrame)
            self.unmakeDraggable(self.middleFrame)
            self.unmakeDraggable(self.labelHandler)
            self.unmakeAllChildrenDraggable(self.labelHandler)
            self.unmakeDraggable(self.graphFrame.canvas.get_tk_widget())
            self.mainMenu.grid_remove()
            self.characterMenu.grid_remove()
            self.quitButton.grid_remove()
            self.minimizeButton.grid_remove()
            self.collapseButton.destroy()
            self.addCollapseButton(self.middleFrame, row="0", column="1")
            if (self.platform == "Windows"):
                self.update_idletasks()
                self.uncollapseWindow = UncollapseWindow(self)
                windowsCollapseEvent(self, True)
                windowsCollapseEvent(self.detailsWindow, True)
                windowsCollapseEvent(self.fleetWindow, True)
            self.collapsed = True

    def addMinimizeButton(self, parent, row, column):
        """ darws and places the minimize icon next to the collapse button """
        self.minimizeButton = tk.Canvas(parent, width=15, height=15, background="black",
                                    highlightbackground="white", highlightthickness="1")
        #Boxception
        self.minimizeButton.create_line(4,10,13,10,fill="white")
        
        self.minimizeButton.grid(row=row, column=column, sticky="n")
        self.minimizeButton.bind("<ButtonPress-1>", self.buttonDimGray)
        self.minimizeButton.bind("<ButtonRelease-1>", self.minimizeEvent)
        self.minimizeButton.bind("<Enter>", self.buttonGray25)
        self.minimizeButton.bind("<Leave>", self.buttonBlack)

    def minimizeEvent(self, event):
        """ 
        There are many workarounds here to make this work cross-platform
        That is why there are so many update()s needed, and why WM_TAKE_FOCUS is used.
        However, this still isn't perfect on linux platforms, for some reason iconify()
        takes multiple seconds to complete, and triggers WM_TAKE_FOCUS, so there is a period
        where the window manager will not respond correctly if the window is restored too quickly.
        """
        self.protocol("WM_TAKE_FOCUS", lambda: None)
        self.middleFrame.unbind("<Map>")
        self.update()
        self.overrideredirect(False)
        self.update()
        self.withdraw()
        self.update()
        self.deiconify()
        self.update()
        if settings.detailsWindowShow and hasattr(self, 'detailsWindow'):
            self.detailsWindow.withdraw()
        if settings.fleetWindowShow and hasattr(self, 'fleetWindow') and self.animator.dataQueue:
            self.fleetWindow.withdraw()
        self.iconify()
        self.update()
        self.middleFrame.bind("<Map>", self.showEvent)
        self.protocol("WM_TAKE_FOCUS", lambda: self.showEvent(None))

    def showEvent(self, event):
        """ Same as minimizeEvent, many workarounds here, almost entirely due to linux """
        if self.overrideredirect():
            return
        self.middleFrame.unbind("<Map>")
        self.update()
        self.overrideredirect(True)
        self.update()
        self.withdraw()
        self.update()
        self.after(100, self.deiconify)
        if settings.detailsWindowShow and hasattr(self, 'detailsWindow'):
            self.detailsWindow.deiconify()
        if settings.fleetWindowShow and hasattr(self, 'fleetWindow') and self.animator.dataQueue:
            self.fleetWindow.deiconify()
        self.addToTaskbar()
        self.middleFrame.bind("<Map>", self.showEvent)
    
    def addPlaybackFrame(self, startTime, endTime):
        """ adds the playback frame underneath the graph when in 'playback' mode """
        self.mainMenu.menu.entryconfig(3, state="disabled")
        self.mainMenu.menu.delete(6)
        self.mainMenu.menu.insert_command(6, label="Stop Log Playback", command=self.characterDetector.stopPlayback)
        self.topLabel.configure(text="Playback Mode")
        self.topLabel.grid()
        self.playbackFrame = playbackFrame.PlaybackFrame(self, startTime, endTime)
        self.playbackFrame.grid(row="11", column="1", columnspan="19", sticky="news")
    
    def removePlaybackFrame(self):
        """ removes the playback frame when we leave playback mode """
        getLogFilePath = lambda: tk.filedialog.askopenfilename(initialdir=self.characterDetector.path, title="Select log file")
        self.mainMenu.menu.entryconfig(3, state="normal")
        self.mainMenu.menu.delete(6)
        self.mainMenu.menu.insert_command(6, label="Playback Log", command=lambda: self.characterDetector.playbackLog(getLogFilePath()))
        self.topLabel.grid_remove()
        self.playbackFrame.grid_remove()
        self.animator.catchup()
    
    def getGraph(self):
        return self.graphFrame

    def buttonGray25(self, event):
        event.widget.configure(background="gray25")
        
    def buttonDimGray(self, event):
        event.widget.configure(background="dim gray")
        
    def buttonBlack(self, event):
        event.widget.configure(background="black")
        
    def quitEvent(self, event=None):
        """ quitEvent is run when either the menu quit option is clicked or the quit button is clicked """
        # if the event came from the menu, event will be 'None', otherwise the event location is checked
        # to make sure the user finished their click inside the quit button
        if not event or (event.x >= 0 and event.x <= 16 and event.y >= 0 and event.y <= 16):
            logging.info('quit event received, saving window geometry and stopping threads')
            self.saveWindowGeometry()
            self.animator.stop()
            if hasattr(self, "caracterDetector"):
                self.characterDetector.stop()
            logging.info('bye')
            self.quit()
            
    def saveWindowGeometry(self):
        """ saves window position and size to the settings file """
        self.detailsWindow.saveWindowGeometry()
        self.fleetWindow.saveWindowGeometry()
        settings.setSettings(windowX=self.winfo_x(), windowY=self.winfo_y(),
                                   windowWidth=self.winfo_width(), windowHeight=self.winfo_height())
                                   
    def stopMove(self):
        self.update_idletasks()
        self.graphFrame.readjust(0)

def windowsCollapseEvent(window, collapse):
    """ windowsOS api magic to allow clicks to not be handled by PELD windows """
    window.update_idletasks()
    GWL_EXSTYLE=-20
    WS_EX_TRANSPARENT=0x00000020
    hwnd = windll.user32.GetParent(window.winfo_id())
    try:
        style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    except AttributeError:
        style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if collapse:
        style = style | WS_EX_TRANSPARENT
    else:
        style = style & ~WS_EX_TRANSPARENT
    try:
        res = windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, style)
    except AttributeError:
        res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    window.update_idletasks()
    