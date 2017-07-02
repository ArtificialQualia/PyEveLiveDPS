"""
In order to create the type of window that will work well while running EVE,
 we must perform many customizations on the window.
 
By detatching it from the window manager with overrideredirect(true), one
 must manually implement traditional window manager functions that users expect.
 For instance resizing the window along borders.
"""

import tkinter as tk
from tkinter import ttk
import graph

class BorderlessWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.columnconfigure(10, weight=1)
        self.rowconfigure(10, weight=1)
                
        self.mainFrame = tk.Frame(width=400, height=200, background="black")
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
        
        self.topLeftResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="size_nw_se")
        self.topLeftResizeFrame.grid(row="0", column="0")
        self.topLeftResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.topLeftResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.topLeftResizeFrame.bind("<B1-Motion>", self.OnMotionResizeNw)
        
        self.topRightResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="size_ne_sw")
        self.topRightResizeFrame.grid(row="0", column="20")
        self.topRightResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.topRightResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.topRightResizeFrame.bind("<B1-Motion>", self.OnMotionResizeNe)
        
        self.bottomLeftResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="size_ne_sw")
        self.bottomLeftResizeFrame.grid(row="20", column="0")
        self.bottomLeftResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.bottomLeftResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.bottomLeftResizeFrame.bind("<B1-Motion>", self.OnMotionResizeSw)
        
        self.bottomRightResizeFrame = tk.Frame(width=5, height=5, background="black", cursor="size_nw_se")
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
        self.mainMenu.menu.add_command(label="Quit", command=self.quit)
        
        self.characterMenu = tk.Menubutton(text="Character...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.characterMenu.grid(row="5", column="2")
        self.characterMenu.menu = tk.Menu(self.characterMenu, tearoff=False)
        self.characterMenu["menu"] = self.characterMenu.menu
        self.characterMenu.menu.add_checkbutton(label="Char1")
        
        self.dpsFrame = tk.Frame(height="10", borderwidth="1", background="black")
        self.dpsFrame.grid(row="6", column="1", columnspan="19", sticky="ew")
        self.makeDraggable(self.dpsFrame)
        
        self.dpsOutLabel = tk.Label(self.dpsFrame, text="DPS Out: 100", fg="white", background="black")
        self.dpsOutLabel.pack(side=tk.LEFT)
        self.makeDraggable(self.dpsOutLabel)
        
        self.dpsInLabel = tk.Label(self.dpsFrame, text="DPS In: 100", fg="white", background="black")
        self.dpsInLabel.pack(side=tk.RIGHT)
        self.makeDraggable(self.dpsInLabel)
        
        self.graphFrame = graph.DPSGraph()
        self.graphFrame.configure(background="black", borderwidth="0")
        self.graphFrame.grid(row="7", column="1", rowspan="13", columnspan="19", sticky="nesw")
        self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
        
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
            self.quit()
    
    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

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
        
        
        #self.bQuit = tk.Button(text="Quit", command=self.quit)
        #self.bQuit.pack(pady=20)
        

    