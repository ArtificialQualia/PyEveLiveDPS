"""
MainWindow:

Some of the styling for this window comes from BaseWindow,
 but as this is the main window in the app some additional
 customizations are layered on.
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
from peld import logger
from peld import settings
from baseWindow import BaseWindow
from detailsWindow import DetailsWindow
if (platform.system() == "Windows"):
    from ctypes import windll


class MainWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.baseWindow = BaseWindow(self)
        self.minsize(175,50)
        
        #Set title and icon for alt+tab and taskbar
        self.wm_title("PyEveLiveDPS")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        
        #Magic to make the window appear on the windows taskbar
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
            logger.exception("Error adding PELD to Windows taskbar.  This should never happen, but execution can continue normally.")
            logger.exception(e)
        
        self.topLabel = tk.Label(self, text="Simulation Mode", fg="white", background="black")
        font = tkFont.Font(font=self.topLabel['font'])
        font.config(slant='italic')
        self.topLabel['font'] = font
        self.topLabel.grid(row="5", column="5", columnspan="10")
        self.topLabel.grid_remove()
        self.makeDraggable(self.topLabel)
        
        #Other items for setting up the window have been moved to separate functions
        self.addQuitButton()
        
        self.addCollapseButton(self, row="5", column="17")
        
        self.addMenus()
        
        #Container for our "dps labels" and graph
        self.middleFrame = tk.Frame(self, background="black")
        self.middleFrame.columnconfigure(0, weight=1)
        self.middleFrame.rowconfigure(1, weight=1)
        self.middleFrame.grid(row="10", column="1", columnspan="19", sticky="news")
        self.makeDraggable(self.middleFrame)
        
        self.labelHandler = labelHandler.LabelHandler(self.middleFrame, lambda c:self.makeAllChildrenDraggable(c),
                                                       height="10", borderwidth="0", background="black")
        self.labelHandler.grid(row="0", column="0", sticky="news")
        self.makeDraggable(self.labelHandler)
        
        self.geometry("%sx%s+%s+%s" % (settings.getWindowWidth(), settings.getWindowHeight(), 
                                       settings.getWindowX(), settings.getWindowY()))
        self.update_idletasks()
        
        #The hero of our app
        self.graphFrame = graph.DPSGraph(self.middleFrame, self.labelHandler, background="black", borderwidth="0")
        self.graphFrame.grid(row="1", column="0", columnspan="3", sticky="nesw")
        self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
        
        self.detailsWindow = DetailsWindow(self)
        
        self.animator = animate.Animator(self)
        
        self.graphFrame.readjust(self.winfo_width(), 0)
        if settings.getGraphDisabled():
            self.graphFrame.grid_remove()
        else:
            self.graphFrame.grid()
            
        self.labelHandler.lift(self.graphFrame)
        
        logger.info('main window (and subcomponents) initialized')
        
    def __getattr__(self, attr):
        return getattr(self.baseWindow, attr)
        
    def addMenus(self):
        #character menu options are added dynamically by CharacterDetector, so we pass this into that
        self.characterMenu = tk.Menubutton(text="Character...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.characterMenu.grid(row="5", column="2")
        self.characterMenu.menu = tk.Menu(self.characterMenu, tearoff=False)
        self.characterMenu["menu"] = self.characterMenu.menu
        self.characterDetector = logreader.CharacterDetector(self, self.characterMenu)
        
        #Set up file menu options
        self.mainMenu = tk.Menubutton(text="File...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.mainMenu.grid(row="5", column="1")
        self.mainMenu.menu = tk.Menu(self.mainMenu, tearoff=False)
        self.mainMenu["menu"] = self.mainMenu.menu
        self.mainMenu.menu.add_command(label="Edit Profile Settings", command=lambda: settingsWindow.SettingsWindow(self))
        
        self.profileMenu = tk.Menu(self.mainMenu, tearoff=False)
        settings.initializeMenu(self)
        
        self.mainMenu.menu.add_cascade(label="Profile", menu=self.profileMenu)
        self.mainMenu.menu.add_separator()
        self.mainMenu.menu.add_command(label="Simulate Input", command=lambda: simulationWindow.SimulationWindow(self))
        getLogFilePath = lambda: tk.filedialog.askopenfilename(initialdir=self.characterDetector.path, title="Select log file")
        self.mainMenu.menu.add_command(label="Playback Log", command=lambda: self.characterDetector.playbackLog(getLogFilePath()))
        self.mainMenu.menu.add_separator()
        self.mainMenu.menu.add_command(label="Quit", command=self.quitEvent)
    
    def addQuitButton(self):
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
        logger.debug('window collapse event occured')
        self.detailsWindow.collapseHandler(self.collapsed)
        if self.collapsed:
            self.wm_attributes("-alpha", 1.0)
            self.rightSpacerFrame.grid_remove()
            self.topResizeFrame.grid()
            self.bottomResizeFrame.grid()
            self.leftResizeFrame.grid()
            self.rightResizeFrame.grid()
            self.topLeftResizeFrame.grid()
            self.topRightResizeFrame.grid()
            self.bottomLeftResizeFrame.grid()
            self.bottomRightResizeFrame.grid()
            self.makeDraggable(self.topLabel)
            self.makeDraggable(self.mainFrame)
            self.makeDraggable(self.middleFrame)
            self.makeDraggable(self.labelHandler)
            self.makeAllChildrenDraggable(self.labelHandler)
            self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
            self.mainMenu.grid()
            self.characterMenu.grid()
            self.quitButton.grid()
            self.collapseButton.destroy()
            self.addCollapseButton(self, row="5", column="17")
            self.collapsed = False
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
            self.collapseButton.destroy()
            self.addCollapseButton(self.middleFrame, row="0", column="1")
            self.collapsed = True
    
    def addPlaybackFrame(self, startTime, endTime):
        self.mainMenu.menu.delete(4)
        self.mainMenu.menu.insert_command(4, label="Stop Log Playback", command=self.characterDetector.stopPlayback)
        self.topLabel.configure(text="Playback Mode")
        self.topLabel.grid()
        self.playbackFrame = playbackFrame.PlaybackFrame(self, startTime, endTime)
        self.playbackFrame.grid(row="11", column="1", columnspan="19", sticky="news")
    
    def removePlaybackFrame(self):
        getLogFilePath = lambda: tk.filedialog.askopenfilename(initialdir=self.characterDetector.path, title="Select log file")
        self.mainMenu.menu.delete(4)
        self.mainMenu.menu.insert_command(4, label="Playback Log", command=lambda: self.characterDetector.playbackLog(getLogFilePath()))
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
        if not event or (event.x >= 0 and event.x <= 16 and event.y >= 0 and event.y <= 16):
            logger.info('quit event received, saving window geometry and stopping threads')
            self.saveWindowGeometry()
            self.animator.stop()
            if hasattr(self, "caracterDetector"):
                self.characterDetector.stop()
            self.quit()
            
    def saveWindowGeometry(self):
        self.detailsWindow.saveWindowGeometry()
        settings.setSettings(windowX=self.winfo_x(), windowY=self.winfo_y(),
                                   windowWidth=self.winfo_width(), windowHeight=self.winfo_height())
    