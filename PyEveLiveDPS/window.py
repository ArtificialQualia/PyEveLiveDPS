"""
In order to create the type of window that will work well while running EVE,
 we must perform many customizations on the window.
 
By detatching it from the window manager with overrideredirect(true), one
 must manually implement traditional window manager functions that users expect.
 For instance resizing the window along borders.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import platform
import graph
import logreader

class BorderlessWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.columnconfigure(10, weight=1)
        self.rowconfigure(10, weight=1)
        self.configure(background="black")
        self.minsize(220,100)
        
        self.platform = platform.system()
        
        self.secondsVar = tk.StringVar()
        self.secondsVar.set("10")
        self.intervalVar = tk.StringVar()
        self.intervalVar.set("100")
                
        self.mainFrame = tk.Frame(background="black")
        self.mainFrame.grid(row="1", column="1", rowspan="19", columnspan="19", sticky="nesw")
        self.makeDraggable(self.mainFrame)
        
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
        
        self.quitButton = tk.Canvas(width=15, height=15, background="black",
                                    highlightbackground="white", highlightthickness="1")
        self.quitButton.create_line(0,0,16,16,fill="white")
        self.quitButton.create_line(1,15,16,0,fill="white")
        self.quitButton.grid(row="5", column="19", sticky="ne")
        self.quitButton.bind("<Enter>", self.QuitButtonGray25)
        self.quitButton.bind("<Leave>", self.QuitButtonBlack)
        self.quitButton.bind("<ButtonPress-1>", self.QuitButtonDimGray)
        self.quitButton.bind("<ButtonRelease-1>", self.quitEvent)
        
    def mainWindowDecorator(self):
        self.mainMenu = tk.Menubutton(text="File...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.mainMenu.grid(row="5", column="1")
        self.mainMenu.menu = tk.Menu(self.mainMenu, tearoff=False)
        self.mainMenu["menu"] = self.mainMenu.menu
        self.mainMenu.menu.add_command(label="Settings", command=self.openSettings)
        self.mainMenu.menu.add_command(label="Quit", command=self.quit)
        
        self.characterMenu = tk.Menubutton(text="Character...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.characterMenu.grid(row="5", column="2")
        self.characterMenu.menu = tk.Menu(self.characterMenu, tearoff=False)
        self.characterMenu["menu"] = self.characterMenu.menu
        self.characterDetector = logreader.CharacterDetector(self.characterMenu)
        
        self.dpsFrame = tk.Frame(height="10", borderwidth="0", background="black")
        self.dpsFrame.grid(row="6", column="1", columnspan="19", sticky="ew")
        self.makeDraggable(self.dpsFrame)
        
        self.dpsOutLabel = tk.Label(self.dpsFrame, text="DPS Out: 0.0", fg="white", background="black")
        self.dpsOutLabel.pack(side=tk.LEFT)
        self.makeDraggable(self.dpsOutLabel)
        
        self.dpsInLabel = tk.Label(self.dpsFrame, text="DPS In: 0.0", fg="white", background="black")
        self.dpsInLabel.pack(side=tk.RIGHT)
        self.makeDraggable(self.dpsInLabel)
        
        self.graphFrame = graph.DPSGraph(self.dpsOutLabel, self.dpsInLabel, self.characterDetector,
                                          background="black", borderwidth="0")
        self.graphFrame.grid(row="7", column="1", rowspan="13", columnspan="19", sticky="nesw")
        self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
        
    def openSettings(self):
        self.settingsWindow = tk.Toplevel()
        self.settingsWindow.wm_attributes("-topmost", True)
        self.settingsWindow.geometry("360x160")
        
        secondsLabel = tk.Label(self.settingsWindow, text="Number of seconds to average DPS:")
        secondsLabel.grid(row="0", column="0")
        secondsEntry = tk.Entry(self.settingsWindow, textvariable=self.secondsVar, width=10)
        secondsEntry.grid(row="0", column="1")
        secondsDescriptor = tk.Label(self.settingsWindow, text="Recommended to set this value higher than your weapon cycle time")
        font = tkFont.Font(font=secondsDescriptor['font'])
        font.config(slant='italic')
        secondsDescriptor['font'] = font
        secondsDescriptor.grid(row="1", column="0", columnspan="5")
        
        spacer = tk.Frame(self.settingsWindow, height="20", width="10")
        spacer.grid(row="2", column="1", columnspan="5")
        
        intervalLabel = tk.Label(self.settingsWindow, text="How often to update the graph in milliseconds:")
        intervalLabel.grid(row="3", column="0")
        intervalEntry = tk.Entry(self.settingsWindow, textvariable=self.intervalVar, width=10)
        intervalEntry.grid(row="3", column="1")
        intervalDescriptor = tk.Label(self.settingsWindow, text="The lower you set this value, the higher your CPU usage will be")
        font = tkFont.Font(font=intervalDescriptor['font'])
        font.config(slant='italic')
        intervalDescriptor['font'] = font
        intervalDescriptor.grid(row="4", column="0", columnspan="5")
        
        spacer2 = tk.Frame(self.settingsWindow, height="20", width="10")
        spacer2.grid(row="5", column="1", columnspan="5")
        
        okButton = tk.Button(self.settingsWindow, text="  OK  ", command=self.doSettings)
        okButton.grid(row="6", column="0", columnspan="5")
        
    def doSettings(self):
        try:
            secondsSetting = int(self.secondsVar.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a number for number of seconds to average DPS")
            return
        if (secondsSetting < 2 or secondsSetting > 600):
            tk.messagebox.showerror("Error", "Please enter a value between 2-600 for number of seconds to average DPS")
            return  
        
        try:
            intervalSetting = int(self.intervalVar.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a number for milliseconds to update graph")
            return
        if (intervalSetting < 10 or intervalSetting > 1000):
            tk.messagebox.showerror("Error", "Please enter a value between 10-1000 for milliseconds to update graph")
            return
        
        if ((secondsSetting*1000)/intervalSetting <= 10):
            tk.messagebox.showerror("Error", "(Seconds to average DPS*1000)/(Graph update interval) must be > 10.\n" +
                                   "If it is less than 10, we won't have enough data to draw an accurate graph!")
            return
        
        if ((secondsSetting*1000)/intervalSetting < 20):
            okCancel = tk.messagebox.askokcancel("Continue?", "(Seconds to average DPS*1000)/(Graph update interval)\n is < 20\n" +
                                   "This is ok, but it is recommended to increase your (Seconds to average DPS) or \n" +
                                   "decrease your (Graph update interval) to improve your graphing experience.\n"
                                   "Would you like to keep these settings?")
            if not okCancel:
                return
            
        if (intervalSetting < 50):
            okCancel = tk.messagebox.askokcancel("Continue?", "Setting the graph update interval to less than 50ms\n" +
                                                 "Is generally a bad idea.  Your CPU won't like it."
                                                 "Would you like to keep these settings?")
            if not okCancel:
                return
            
        
        self.graphFrame.changeSettings(secondsSetting, intervalSetting)
        
        self.settingsWindow.destroy()
    
    def makeDraggable(self, widget):
        widget.bind("<ButtonPress-1>", self.StartMove)
        widget.bind("<ButtonRelease-1>", self.StopMove)
        widget.bind("<B1-Motion>", self.OnMotionMove)

    def QuitButtonGray25(self, event):
        self.quitButton.configure(background="gray25")
        
    def QuitButtonDimGray(self, event):
        self.quitButton.configure(background="dim gray")
        
    def QuitButtonBlack(self, event):
        self.quitButton.configure(background="black")
        
    def quitEvent(self, event):
        if (event.x >= 0 and event.x <= 16 and event.y >= 0 and event.y <= 16):
            if hasattr(self, "caracterDetector"):
                self.characterDetector.stop()
            self.quit()
    
    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None
        if (self.graphFrame):
            self.graphFrame.readjust(left=(40/self.winfo_width()), 
                                     top=(1-15/self.winfo_width()), bottom=(15/self.winfo_width()))
        
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
        
    