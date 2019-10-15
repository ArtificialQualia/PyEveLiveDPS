"""
BaseWindow:

Other 'main' windows inherit this class.

In order to create the type of window that will work well while running EVE,
 we must perform many customizations on the window.
 
By detatching it from the window manager with overrideredirect(true), one
 must manually implement traditional window manager functions that users expect.
 For instance resizing the window along borders.
"""

import tkinter as tk
import platform

# BaseWindow doesn't inhert from tkinter so that it can be used for both the main window and toplevels
# it does assume whatever is inheriting it has all the tkinter functions though
class BaseWindow():
    def __init__(self, child):
        self.childWindow = child
        self.childWindow.overrideredirect(True)
        self.childWindow.wm_attributes("-topmost", True)
        self.childWindow.columnconfigure(10, weight=1)
        self.childWindow.rowconfigure(10, weight=1)
        self.childWindow.configure(background="black")
        
        #We need to get the user's system type (Windows or non-windows) for some windows specific cursor types
        self.childWindow.platform = platform.system()
         
        #This frame takes up all the extra nooks and crannies in the window, so we can drag them like a user would expect
        self.childWindow.mainFrame = tk.Frame(self.childWindow, background="black")
        self.childWindow.mainFrame.grid(row="1", column="1", rowspan="19", columnspan="19", sticky="nesw")
        self.makeDraggable(self.childWindow.mainFrame)
        
        #Other items for setting up the window have been moved to separate functions
        self.addDraggableEdges()
        
        self.addDraggableCorners()
        
        
    def addDraggableEdges(self):
        self.childWindow.topResizeFrame = tk.Frame(self.childWindow, height=5, background="black", cursor="sb_v_double_arrow")
        self.childWindow.topResizeFrame.grid(row="0", column="1", columnspan="50", sticky="ew")
        self.childWindow.topResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.childWindow.topResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.childWindow.topResizeFrame.bind("<B1-Motion>", self.OnMotionResizeYTop)
        
        self.childWindow.bottomResizeFrame = tk.Frame(self.childWindow, height=5, background="black", cursor="sb_v_double_arrow")
        self.childWindow.bottomResizeFrame.grid(row="20", column="1", columnspan="50", sticky="ew")
        self.childWindow.bottomResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.childWindow.bottomResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.childWindow.bottomResizeFrame.bind("<B1-Motion>", self.OnMotionResizeYBottom)
        
        self.childWindow.leftResizeFrame = tk.Frame(self.childWindow, width=5, background="black", cursor="sb_h_double_arrow")
        self.childWindow.leftResizeFrame.grid(row="1", column="0", rowspan="50", sticky="ns")
        self.childWindow.leftResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.childWindow.leftResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.childWindow.leftResizeFrame.bind("<B1-Motion>", self.OnMotionResizeXLeft)
        
        self.childWindow.rightResizeFrame = tk.Frame(self.childWindow, width=5, background="black", cursor="sb_h_double_arrow")
        self.childWindow.rightResizeFrame.grid(row="1", column="20", rowspan="50", sticky="ns")
        self.childWindow.rightResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.childWindow.rightResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.childWindow.rightResizeFrame.bind("<B1-Motion>", self.OnMotionResizeXRight)
    
    def addDraggableCorners(self):
        if (self.childWindow.platform == "Windows"):
            self.childWindow.topLeftResizeFrame = tk.Frame(self.childWindow, width=5, height=5, background="black", cursor="size_nw_se")
        else:
            self.childWindow.topLeftResizeFrame = tk.Frame(self.childWindow, width=5, height=5, background="black", cursor="top_left_corner")
        self.childWindow.topLeftResizeFrame.grid(row="0", column="0")
        self.childWindow.topLeftResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.childWindow.topLeftResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.childWindow.topLeftResizeFrame.bind("<B1-Motion>", self.OnMotionResizeNw)
        
        if (self.childWindow.platform == "Windows"):
            self.childWindow.topRightResizeFrame = tk.Frame(self.childWindow, width=5, height=5, background="black", cursor="size_ne_sw")
        else:
            self.childWindow.topRightResizeFrame = tk.Frame(self.childWindow, width=5, height=5, background="black", cursor="top_right_corner")
        self.childWindow.topRightResizeFrame.grid(row="0", column="20")
        self.childWindow.topRightResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.childWindow.topRightResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.childWindow.topRightResizeFrame.bind("<B1-Motion>", self.OnMotionResizeNe)
        
        if (self.childWindow.platform == "Windows"):
            self.childWindow.bottomLeftResizeFrame = tk.Frame(self.childWindow, width=5, height=5, background="black", cursor="size_ne_sw")
        else:
            self.childWindow.bottomLeftResizeFrame = tk.Frame(self.childWindow, width=5, height=5, background="black", cursor="bottom_left_corner")
        self.childWindow.bottomLeftResizeFrame.grid(row="20", column="0")
        self.childWindow.bottomLeftResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.childWindow.bottomLeftResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.childWindow.bottomLeftResizeFrame.bind("<B1-Motion>", self.OnMotionResizeSw)
        
        if (self.childWindow.platform == "Windows"):
            self.childWindow.bottomRightResizeFrame = tk.Frame(self.childWindow, width=5, height=5, background="black", cursor="size_nw_se")
        else:
            self.childWindow.bottomRightResizeFrame = tk.Frame(self.childWindow, width=5, height=5, background="black", cursor="bottom_right_corner")
        self.childWindow.bottomRightResizeFrame.grid(row="20", column="20")
        self.childWindow.bottomRightResizeFrame.bind("<ButtonPress-1>", self.StartMove)
        self.childWindow.bottomRightResizeFrame.bind("<ButtonRelease-1>", self.StopMove)
        self.childWindow.bottomRightResizeFrame.bind("<B1-Motion>", self.OnMotionResizeSe)
    
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

    def showResizeFrames(self):
        self.childWindow.topResizeFrame.grid()
        self.childWindow.bottomResizeFrame.grid()
        self.childWindow.leftResizeFrame.grid()
        self.childWindow.rightResizeFrame.grid()
        self.childWindow.topLeftResizeFrame.grid()
        self.childWindow.topRightResizeFrame.grid()
        self.childWindow.bottomLeftResizeFrame.grid()
        self.childWindow.bottomRightResizeFrame.grid()

    def hideResizeFrames(self):
        self.childWindow.topResizeFrame.grid_remove()
        self.childWindow.bottomResizeFrame.grid_remove()
        self.childWindow.leftResizeFrame.grid_remove()
        self.childWindow.rightResizeFrame.grid_remove()
        self.childWindow.topLeftResizeFrame.grid_remove()
        self.childWindow.topRightResizeFrame.grid_remove()
        self.childWindow.bottomLeftResizeFrame.grid_remove()
        self.childWindow.bottomRightResizeFrame.grid_remove()
    
    def StartMove(self, event):
        self.childWindow.x = event.x
        self.childWindow.y = event.y

    def StopMove(self, event):
        self.childWindow.x = None
        self.childWindow.y = None
        try:
            self.childWindow.stopMove()
        except AttributeError:
            pass
        
    def OnMotionMove(self, event):
        deltax = event.x - self.childWindow.x
        deltay = event.y - self.childWindow.y
        x = self.childWindow.winfo_x() + deltax
        y = self.childWindow.winfo_y() + deltay
        self.childWindow.geometry("+%s+%s" % (x, y))
        
    def OnMotionResizeSe(self, event):
        x1 = self.childWindow.winfo_pointerx()
        y1 = self.childWindow.winfo_pointery()
        x0 = self.childWindow.winfo_rootx()
        y0 = self.childWindow.winfo_rooty()
        self.childWindow.geometry("%sx%s" % ((x1-x0),(y1-y0)))
        
    def OnMotionResizeSw(self, event):
        deltax = event.x - self.childWindow.x
        xpos = self.childWindow.winfo_x() + deltax
        xsize = self.childWindow.winfo_width() - deltax
        y1 = self.childWindow.winfo_pointery()
        y0 = self.childWindow.winfo_rooty()
        self.childWindow.geometry("%sx%s+%s+%s" % (xsize, (y1-y0), xpos, self.childWindow.winfo_y()))
        
    def OnMotionResizeNw(self, event):
        deltax = event.x - self.childWindow.x
        deltay = event.y - self.childWindow.y
        xpos = self.childWindow.winfo_x() + deltax
        ypos = self.childWindow.winfo_y() + deltay
        xsize = self.childWindow.winfo_width() - deltax
        ysize = self.childWindow.winfo_height() - deltay
        self.childWindow.geometry("%sx%s+%s+%s" % (xsize, ysize, xpos, ypos))
        
    def OnMotionResizeNe(self, event):
        deltay = event.y - self.childWindow.y
        ypos = self.childWindow.winfo_y() + deltay
        ysize = self.childWindow.winfo_height() - deltay
        x1 = self.childWindow.winfo_pointerx()
        x0 = self.childWindow.winfo_rootx()
        self.childWindow.geometry("%sx%s+%s+%s" % ((x1-x0), ysize, self.childWindow.winfo_x(), ypos))
        
    def OnMotionResizeYBottom(self, event):
        x = self.childWindow.winfo_width()
        y1 = self.childWindow.winfo_pointery()
        y0 = self.childWindow.winfo_rooty()
        self.childWindow.geometry("%sx%s" % (x,(y1-y0)))
        
    def OnMotionResizeYTop(self, event):
        deltay = event.y - self.childWindow.y
        ypos = self.childWindow.winfo_y() + deltay
        ysize = self.childWindow.winfo_height() - deltay
        self.childWindow.geometry("%sx%s+%s+%s" % (self.childWindow.winfo_width(), ysize, self.childWindow.winfo_x(), ypos))
        
    def OnMotionResizeXLeft(self, event):
        deltax = event.x - self.childWindow.x
        xpos = self.childWindow.winfo_x() + deltax
        xsize = self.childWindow.winfo_width() - deltax
        self.childWindow.geometry("%sx%s+%s+%s" % (xsize, self.childWindow.winfo_height(), xpos, self.childWindow.winfo_y()))
        
    def OnMotionResizeXRight(self, event):
        y = self.childWindow.winfo_height()
        x1 = self.childWindow.winfo_pointerx()
        x0 = self.childWindow.winfo_rootx()
        self.childWindow.geometry("%sx%s" % ((x1-x0),y))
        
    