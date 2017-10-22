"""
BorderlessWindow:

In order to create the type of window that will work well while running EVE,
 we must perform many customizations on the window.
 
By detatching it from the window manager with overrideredirect(true), one
 must manually implement traditional window manager functions that users expect.
 For instance resizing the window along borders.
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
import settings.settings as settings
import labelHandler
import animate
if (platform.system() == "Windows"):
    from ctypes import windll


class BorderlessWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.columnconfigure(10, weight=1)
        self.rowconfigure(10, weight=1)
        self.configure(background="black")
        self.minsize(175,50)
        
        #Grab settings from our settings handler
        self.settings = settings.Settings()
        
        #We need to get the user's system type (Windows or non-windows) for some windows specific cursor types
        self.platform = platform.system()
        
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
            tk.messagebox.showerror("Error", "Error adding PELD to Windows taskbar.  This should never happen, but execution can continue normally.\n" +
                                    "Internal Error: " + e)
         
        #This frame takes up all the extra nooks and crannies in the window, so we can drag them like a user would expect
        self.mainFrame = tk.Frame(background="black")
        self.mainFrame.grid(row="1", column="1", rowspan="19", columnspan="19", sticky="nesw")
        self.makeDraggable(self.mainFrame)
        
        self.topLabel = tk.Label(self, text="Simulation Mode", fg="white", background="black")
        font = tkFont.Font(font=self.topLabel['font'])
        font.config(slant='italic')
        self.topLabel['font'] = font
        self.topLabel.grid(row="5", column="5", columnspan="10")
        self.topLabel.grid_remove()
        
        #Other items for setting up the window have been moved to separate functions
        self.addDraggableEdges()
        
        self.addDraggableCorners()
        
        self.addQuitButton()
        
        self.addCollapseButton(self, row="5", column="17")
        
        self.addMenus()
        
        #Container for our "dps labels" and graph
        self.middleFrame = tk.Frame(self, background="black")
        self.middleFrame.columnconfigure(0, weight=1)
        self.middleFrame.rowconfigure(1, weight=1)
        self.middleFrame.grid(row="10", column="1", columnspan="19", sticky="news")
        self.makeDraggable(self.middleFrame)
        
        self.labelHandler = labelHandler.LabelHandler(self.middleFrame, self.settings, lambda c:self.makeAllChildrenDraggable(c),
                                                       height="10", borderwidth="0", background="black")
        self.labelHandler.grid(row="0", column="0", sticky="news")
        self.makeDraggable(self.labelHandler)
        
        self.geometry("%sx%s+%s+%s" % (self.settings.getWindowWidth(), self.settings.getWindowHeight(), 
                                       self.settings.getWindowX(), self.settings.getWindowY()))
        self.update_idletasks()
        
        #The hero of our app
        self.graphFrame = graph.DPSGraph(self.middleFrame, self.settings, self.labelHandler, background="black", borderwidth="0")
        self.graphFrame.grid(row="1", column="0", columnspan="3", sticky="nesw")
        self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
        
        self.animator = animate.Animator(self)
        
        self.graphFrame.readjust(self.winfo_width(), 0)
        if self.settings.getGraphDisabled():
            self.graphFrame.grid_remove()
        else:
            self.graphFrame.grid()
            
        self.labelHandler.lift(self.graphFrame)
        
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
        self.settings.initializeMenu(self)
        
        self.mainMenu.menu.add_cascade(label="Profile", menu=self.profileMenu)
        self.mainMenu.menu.add_separator()
        self.mainMenu.menu.add_command(label="Simulate Input", command=lambda: simulationWindow.SimulationWindow(self))
        getLogFilePath = lambda: tk.filedialog.askopenfilename(initialdir=self.characterDetector.path, title="Select log file")
        self.mainMenu.menu.add_command(label="Playback Log", command=lambda: self.characterDetector.playbackLog(getLogFilePath()))
        self.mainMenu.menu.add_separator()
        self.mainMenu.menu.add_command(label="Quit", command=self.quitEvent)
        
    def addDraggableEdges(self):
        self.topResizeFrame = tk.Frame(height=5, background="black", cursor="sb_v_double_arrow")
        self.topResizeFrame.grid(row="0", column="1", columnspan="50", sticky="ew")
        self.topResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.topResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.topResizeFrame.bind("<B1-Motion>", self.OnMotionResizeYTop)
        
        self.bottomResizeFrame = tk.Frame(height=5, background="black", cursor="sb_v_double_arrow")
        self.bottomResizeFrame.grid(row="20", column="1", columnspan="50", sticky="ew")
        self.bottomResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.bottomResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.bottomResizeFrame.bind("<B1-Motion>", self.OnMotionResizeYBottom)
        
        self.leftResizeFrame = tk.Frame(width=5, background="black", cursor="sb_h_double_arrow")
        self.leftResizeFrame.grid(row="1", column="0", rowspan="50", sticky="ns")
        self.leftResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.leftResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.leftResizeFrame.bind("<B1-Motion>", self.OnMotionResizeXLeft)
        
        self.rightResizeFrame = tk.Frame(width=5, background="black", cursor="sb_h_double_arrow")
        self.rightResizeFrame.grid(row="1", column="20", rowspan="50", sticky="ns")
        self.rightResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.rightResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.rightResizeFrame.bind("<B1-Motion>", self.OnMotionResizeXRight)
    
    def addDraggableCorners(self):
        if (self.platform == "Windows"):
            self.topLeftResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="size_nw_se")
        else:
            self.topLeftResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="top_left_corner")
        self.topLeftResizeFrame.grid(row="0", column="0")
        self.topLeftResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.topLeftResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.topLeftResizeFrame.bind("<B1-Motion>", self.OnMotionResizeNw)
        
        if (self.platform == "Windows"):
            self.topRightResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="size_ne_sw")
        else:
            self.topRightResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="top_right_corner")
        self.topRightResizeFrame.grid(row="0", column="20")
        self.topRightResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.topRightResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.topRightResizeFrame.bind("<B1-Motion>", self.OnMotionResizeNe)
        
        if (self.platform == "Windows"):
            self.bottomLeftResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="size_ne_sw")
        else:
            self.bottomLeftResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="bottom_left_corner")
        self.bottomLeftResizeFrame.grid(row="20", column="0")
        self.bottomLeftResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.bottomLeftResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.bottomLeftResizeFrame.bind("<B1-Motion>", self.OnMotionResizeSw)
        
        if (self.platform == "Windows"):
            self.bottomRightResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="size_nw_se")
        else:
            self.bottomRightResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="bottom_right_corner")
        self.bottomRightResizeFrame.grid(row="20", column="20")
        self.bottomRightResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.bottomRightResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.bottomRightResizeFrame.bind("<B1-Motion>", self.OnMotionResizeSe)
    
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
            self.wm_attributes("-alpha", self.settings.getCompactTransparency()/100)
            self.topResizeFrame.grid_remove()
            self.bottomResizeFrame.grid_remove()
            self.leftResizeFrame.grid_remove()
            self.rightResizeFrame.grid_remove()
            self.topLeftResizeFrame.grid_remove()
            self.topRightResizeFrame.grid_remove()
            self.bottomLeftResizeFrame.grid_remove()
            self.bottomRightResizeFrame.grid_remove()
            self.rightSpacerFrame.grid()
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
        getLogFilePath = lambda: filedialog.askopenfilename(initialdir=self.characterDetector.path, title="Select log file")
        self.mainMenu.menu.delete(4)
        self.mainMenu.menu.insert_command(4, label="Playback Log", command=lambda: self.playbackLog(getLogFilePath()))
        self.topLabel.grid_remove()
        self.playbackFrame.grid_remove()
        self.animator.catchup()
    
    def getGraph(self):
        return self.graphFrame
    
    def makeAllChildrenDraggable(self, widget):
        children = widget.winfo_children()
        if len(children) > 0:
            for child in children:
                child.bind("<ButtonPress-1>", self.StartMove)
                child.bind("<ButtonRelease-1>", self.StopMove)
                child.bind("<B1-Motion>", self.OnMotionMove)
                self.makeAllChildrenDraggable(child)
                
    def unmakeAllChildrenDraggable(self, widget):
        children = widget.winfo_children()
        if len(children) > 0:
            for child in children:
                child.bind("<ButtonPress-1>", lambda e: False)
                child.bind("<ButtonRelease-1>", lambda e: False)
                child.bind("<B1-Motion>", lambda e: False)
                self.unmakeAllChildrenDraggable(child)
    
    def makeDraggable(self, widget):
        widget.bind("<ButtonPress-1>", self.StartMove)
        widget.bind("<ButtonRelease-1>", self.StopMove)
        widget.bind("<B1-Motion>", self.OnMotionMove)
        
    def unmakeDraggable(self, widget):
        widget.bind("<ButtonPress-1>", lambda e: False)
        widget.bind("<ButtonRelease-1>", lambda e: False)
        widget.bind("<B1-Motion>", lambda e: False)

    def buttonGray25(self, event):
        event.widget.configure(background="gray25")
        
    def buttonDimGray(self, event):
        event.widget.configure(background="dim gray")
        
    def buttonBlack(self, event):
        event.widget.configure(background="black")
        
    def quitEvent(self, event=None):
        if not event:
            self.saveWindowGeometry()
            self.animator.stop()
            self.quit()
        if event and (event.x >= 0 and event.x <= 16 and event.y >= 0 and event.y <= 16):
            self.saveWindowGeometry()
            self.animator.stop()
            if hasattr(self, "caracterDetector"):
                self.characterDetector.stop()
            self.quit()
            
    def saveWindowGeometry(self):
        self.settings.setSettings(windowX=self.winfo_x(), windowY=self.winfo_y(),
                                   windowWidth=self.winfo_width(), windowHeight=self.winfo_height())
    
    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None
        if (self.graphFrame):
            self.graphFrame.readjust(self.winfo_width(), 0)
        
    def OnMotionMove(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry("+%s+%s" % (x, y))
        
    def OnMotionResizeSe(self, event):
        x1 = self.winfo_pointerx()
        y1 = self.winfo_pointery()
        x0 = self.winfo_rootx()
        y0 = self.winfo_rooty()
        self.geometry("%sx%s" % ((x1-x0),(y1-y0)))
        
    def OnMotionResizeSw(self, event):
        deltax = event.x - self.x
        xpos = self.winfo_x() + deltax
        xsize = self.winfo_width() - deltax
        y1 = self.winfo_pointery()
        y0 = self.winfo_rooty()
        self.geometry("%sx%s+%s+%s" % (xsize, (y1-y0), xpos, self.winfo_y()))
        
    def OnMotionResizeNw(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        xpos = self.winfo_x() + deltax
        ypos = self.winfo_y() + deltay
        xsize = self.winfo_width() - deltax
        ysize = self.winfo_height() - deltay
        self.geometry("%sx%s+%s+%s" % (xsize, ysize, xpos, ypos))
        
    def OnMotionResizeNe(self, event):
        deltay = event.y - self.y
        ypos = self.winfo_y() + deltay
        ysize = self.winfo_height() - deltay
        x1 = self.winfo_pointerx()
        x0 = self.winfo_rootx()
        self.geometry("%sx%s+%s+%s" % ((x1-x0), ysize, self.winfo_x(), ypos))
        
    def OnMotionResizeYBottom(self, event):
        x = self.winfo_width()
        y1 = self.winfo_pointery()
        y0 = self.winfo_rooty()
        self.geometry("%sx%s" % (x,(y1-y0)))
        
    def OnMotionResizeYTop(self, event):
        deltay = event.y - self.y
        ypos = self.winfo_y() + deltay
        ysize = self.winfo_height() - deltay
        self.geometry("%sx%s+%s+%s" % (self.winfo_width(), ysize, self.winfo_x(), ypos))
        
    def OnMotionResizeXLeft(self, event):
        deltax = event.x - self.x
        xpos = self.winfo_x() + deltax
        xsize = self.winfo_width() - deltax
        self.geometry("%sx%s+%s+%s" % (xsize, self.winfo_height(), xpos, self.winfo_y()))
        
    def OnMotionResizeXRight(self, event):
        y = self.winfo_height()
        x1 = self.winfo_pointerx()
        x0 = self.winfo_rootx()
        self.geometry("%sx%s" % ((x1-x0),y))
        
    