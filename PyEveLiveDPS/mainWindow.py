"""
BorderlessWindow:

In order to create the type of window that will work well while running EVE,
 we must perform many customizations on the window.
 
By detatching it from the window manager with overrideredirect(true), one
 must manually implement traditional window manager functions that users expect.
 For instance resizing the window along borders.
"""

import tkinter as tk
import idlelib.ToolTip
from ctypes import windll
import platform
import sys
import graph
import logreader
import settingsWindow
import settings


class BorderlessWindow(tk.Tk):
    def __init__(self):
        """This function probably does too much.
        It certainly could be separated out into multiple functions,
        but I could see no real benefit of doing so"""
        tk.Tk.__init__(self)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.columnconfigure(10, weight=1)
        self.rowconfigure(10, weight=1)
        self.configure(background="black")
        self.minsize(175,100)
        
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
        
        #Other items for setting up the window have been moved to separate functions
        self.addDraggableEdges()
        
        self.addDraggableCorners()
        
        self.addQuitButton()
        
        self.addCollapseButton()
        
        self.addMenus()
        
        #Container for our "dps labels"
        self.dpsFrame = tk.Frame(height="10", borderwidth="0", background="black")
        self.dpsFrame.grid(row="6", column="1", columnspan="19", sticky="ew")
        self.makeDraggable(self.dpsFrame)
        self.dpsFrame.grid_columnconfigure(3, weight="1")
        
        self.dpsOutLabel = tk.Label(self.dpsFrame, text="DPS Out: 0.0", fg="white", background="black")
        self.dpsOutLabel.grid(row="0", column="0", sticky="W")
        self.makeDraggable(self.dpsOutLabel)
        self.dpsOutLabel.grid_remove()
        
        self.logiLabelOut = tk.Label(self.dpsFrame, text="Logi Out: 0.0", fg="white", background="black")
        self.logiLabelOut.grid(row="0", column="1", sticky="W")
        self.makeDraggable(self.logiLabelOut)
        self.logiLabelOut.grid_remove()
        
        self.capTransferedLabel = tk.Label(self.dpsFrame, text="Cap Out: 0.0", fg="white", background="black")
        self.capTransferedLabel.grid(row="0", column="2", sticky="W")
        self.makeDraggable(self.capTransferedLabel)
        self.capTransferedLabel.grid_remove()
        
        self.capDamageOutLabel = tk.Label(self.dpsFrame, text="Cap Dmg Out: 0.0", fg="white", background="black")
        self.capDamageOutLabel.grid(row="0", column="3", sticky="W")
        self.makeDraggable(self.capDamageOutLabel)
        self.capDamageOutLabel.grid_remove()
        
        self.capDamageInLabel = tk.Label(self.dpsFrame, text="Cap Dmg In: 0.0", fg="white", background="black")
        self.capDamageInLabel.grid(row="0", column="3", sticky="E")
        self.makeDraggable(self.capDamageInLabel)
        self.capDamageInLabel.grid_remove()
        
        self.capRecievedLabel = tk.Label(self.dpsFrame, text="Cap In: 0.0", fg="white", background="black")
        self.capRecievedLabel.grid(row="0", column="4", sticky="E")
        self.makeDraggable(self.capRecievedLabel)
        self.capRecievedLabel.grid_remove()
        
        self.logiLabelIn = tk.Label(self.dpsFrame, text="Logi In: 0.0", fg="white", background="black")
        self.logiLabelIn.grid(row="0", column="5", sticky="E")
        self.makeDraggable(self.logiLabelIn)
        self.logiLabelIn.grid_remove()
        
        self.dpsInLabel = tk.Label(self.dpsFrame, text="DPS In: 0.0", fg="white", background="black")
        self.dpsInLabel.grid(row="0", column="6", sticky="E")
        self.makeDraggable(self.dpsInLabel)
        self.dpsInLabel.grid_remove()
        
        self.geometry("%sx%s+%s+%s" % (self.settings.getWindowWidth(), self.settings.getWindowHeight(), 
                                       self.settings.getWindowX(), self.settings.getWindowY()))
        self.update_idletasks()
        
        #The hero of our app
        self.graphFrame = graph.DPSGraph(self.dpsOutLabel, self.dpsInLabel, self.logiLabelOut, self.logiLabelIn,
                                         self.capTransferedLabel, self.capRecievedLabel,
                                         self.capDamageOutLabel, self.capDamageInLabel,
                                         self.characterDetector, self.settings, background="black", borderwidth="0")
        self.graphFrame.grid(row="7", column="1", rowspan="13", columnspan="19", sticky="nesw")
        self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
        
        self.graphFrame.readjust(self.winfo_width())
        
    def addMenus(self):
        #Set up menu options
        self.mainMenu = tk.Menubutton(text="File...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.mainMenu.grid(row="5", column="1")
        self.mainMenu.menu = tk.Menu(self.mainMenu, tearoff=False)
        self.mainMenu["menu"] = self.mainMenu.menu
        self.mainMenu.menu.add_command(label="Edit Settings", command=lambda: settingsWindow.SettingsWindow(self))
        
        self.profileMenu = tk.Menu(self.mainMenu, tearoff=False)
        self.settings.initializeMenu(self)
        
        self.mainMenu.menu.add_cascade(label="Profile", menu=self.profileMenu)
        self.mainMenu.menu.add_separator()
        self.mainMenu.menu.add_command(label="Quit", command=self.quitEvent)
        
        #character menu options are added dynamically by CharacterDetector, so we pass this into that
        self.characterMenu = tk.Menubutton(text="Character...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.characterMenu.grid(row="5", column="2")
        self.characterMenu.menu = tk.Menu(self.characterMenu, tearoff=False)
        self.characterMenu["menu"] = self.characterMenu.menu
        self.characterDetector = logreader.CharacterDetector(self.characterMenu)
        
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
        
    def addCollapseButton(self):
        tk.Frame(self, height=1, width=5, background="black").grid(row="5", column="18")
        
        self.collapsed = False
        self.collapseButton = tk.Canvas(width=15, height=15, background="black",
                                    highlightbackground="white", highlightthickness="1")
        #Boxception
        self.collapseButton.create_line(5,5,12,5,fill="white")
        self.collapseButton.create_line(5,5,5,12,fill="white")
        self.collapseButton.create_line(11,11,11,5,fill="white")
        self.collapseButton.create_line(11,11,5,11,fill="white")
        
        self.rightSpacerFrame = tk.Frame(width=5, height=5, background="black")
        self.rightSpacerFrame.grid(row="0", column="100", rowspan="50")
        self.rightSpacerFrame.grid_remove()
        
        self.collapseButton.grid(row="5", column="17", sticky="n")
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
            self.makeDraggable(self.dpsFrame)
            self.makeDraggable(self.dpsOutLabel)
            self.makeDraggable(self.logiLabelOut)
            self.makeDraggable(self.capTransferedLabel)
            self.makeDraggable(self.capDamageOutLabel)
            self.makeDraggable(self.capDamageInLabel)
            self.makeDraggable(self.capRecievedLabel)
            self.makeDraggable(self.logiLabelIn)
            self.makeDraggable(self.dpsInLabel)
            self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
            self.mainMenu.grid()
            self.characterMenu.grid()
            self.quitButton.grid()
            self.dpsFrame.grid(row="6", column="1", columnspan="19", sticky="ew")
            self.collapseButton.grid(row="5", column="17", sticky="n")
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
            self.unmakeDraggable(self.dpsFrame)
            self.unmakeDraggable(self.dpsOutLabel)
            self.unmakeDraggable(self.logiLabelOut)
            self.unmakeDraggable(self.capTransferedLabel)
            self.unmakeDraggable(self.capDamageOutLabel)
            self.unmakeDraggable(self.capDamageInLabel)
            self.unmakeDraggable(self.capRecievedLabel)
            self.unmakeDraggable(self.logiLabelIn)
            self.unmakeDraggable(self.dpsInLabel)
            self.unmakeDraggable(self.graphFrame.canvas.get_tk_widget())
            self.mainMenu.grid_remove()
            self.characterMenu.grid_remove()
            self.quitButton.grid_remove()
            self.dpsFrame.grid(row="6", column="1", columnspan="18", sticky="ew")
            self.collapseButton.grid(row="6", column="19", sticky="e")
            self.collapsed = True
    
    def getGraph(self):
        return self.graphFrame
    
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
            self.quit()
        if event and (event.x >= 0 and event.x <= 16 and event.y >= 0 and event.y <= 16):
            self.saveWindowGeometry()
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
            self.graphFrame.readjust(self.winfo_width())
        
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
        
    