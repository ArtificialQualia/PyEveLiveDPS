"""
BorderlessWindow:

In order to create the type of window that will work well while running EVE,
 we must perform many customizations on the window.
 
By detatching it from the window manager with overrideredirect(true), one
 must manually implement traditional window manager functions that users expect.
 For instance resizing the window along borders.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import tkinter.colorchooser as colorchooser
import platform
import sys
import graph
import logreader

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
        self.minsize(220,100)
        
        #We need to get the user's system type (Windows or non-windows) for some windows specific cursor types
        self.platform = platform.system()
        
        #These are for the "Settings" window
        self.secondsVar = tk.StringVar()
        self.secondsVar.set("10")
        self.intervalVar = tk.StringVar()
        self.intervalVar.set("100")
                
        #This frame takes up all the extra nooks and crannies in the window, so we can drag them like a user would expect
        self.mainFrame = tk.Frame(background="black")
        self.mainFrame.grid(row="1", column="1", rowspan="19", columnspan="19", sticky="nesw")
        self.makeDraggable(self.mainFrame)
        
        #Next four sections are for setting up the draggable edges for resizing.
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
        
        #Next four sections are for setting up the resizeable corners
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
        
        #Fancy quit button...
        self.quitButton = tk.Canvas(width=15, height=15, background="black",
                                    highlightbackground="white", highlightthickness="1")
        self.quitButton.create_line(0,0,16,16,fill="white")
        self.quitButton.create_line(1,15,16,0,fill="white")
        self.quitButton.grid(row="5", column="19", sticky="ne")
        self.quitButton.bind("<Enter>", self.QuitButtonGray25)
        self.quitButton.bind("<Leave>", self.QuitButtonBlack)
        self.quitButton.bind("<ButtonPress-1>", self.QuitButtonDimGray)
        self.quitButton.bind("<ButtonRelease-1>", self.quitEvent)
        
        #Set up menu options
        self.mainMenu = tk.Menubutton(text="File...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.mainMenu.grid(row="5", column="1")
        self.mainMenu.menu = tk.Menu(self.mainMenu, tearoff=False)
        self.mainMenu["menu"] = self.mainMenu.menu
        self.mainMenu.menu.add_command(label="Settings", command=self.openSettings)
        self.mainMenu.menu.add_command(label="Quit", command=self.quit)
        
        #character menu options are added dynamically by CharacterDetector, so we pass this into that
        self.characterMenu = tk.Menubutton(text="Character...", background="black", fg="white", borderwidth="1",
                                      highlightbackground="black", highlightthickness="1",
                                      activebackground="gray25", activeforeground="white")
        self.characterMenu.grid(row="5", column="2")
        self.characterMenu.menu = tk.Menu(self.characterMenu, tearoff=False)
        self.characterMenu["menu"] = self.characterMenu.menu
        self.characterDetector = logreader.CharacterDetector(self.characterMenu)
        
        #Container for our "dps labels"
        self.dpsFrame = tk.Frame(height="10", borderwidth="0", background="black")
        self.dpsFrame.grid(row="6", column="1", columnspan="19", sticky="ew")
        self.makeDraggable(self.dpsFrame)
        self.dpsFrame.grid_columnconfigure(1, weight="1")
        
        self.dpsOutLabel = tk.Label(self.dpsFrame, text="DPS Out: 0.0", fg="white", background="black")
        self.dpsOutLabel.grid(row="0", column="0")
        self.makeDraggable(self.dpsOutLabel)
        
        self.logiLabelOut = tk.Label(self.dpsFrame, text="| Logi Out: 0.0", fg="white", background="black")
        self.logiLabelOut.grid(row="0", column="1", sticky="W")
        self.makeDraggable(self.logiLabelOut)
        self.logiLabelOut.grid_remove()
        
        self.logiLabelIn = tk.Label(self.dpsFrame, text="Logi In: 0.0 |", fg="white", background="black")
        self.logiLabelIn.grid(row="0", column="1", sticky="E")
        self.makeDraggable(self.logiLabelIn)
        self.logiLabelIn.grid_remove()
        
        self.dpsInLabel = tk.Label(self.dpsFrame, text="DPS In: 0.0", fg="white", background="black")
        self.dpsInLabel.grid(row="0", column="2", sticky="e")
        self.makeDraggable(self.dpsInLabel)
        
        #The hero of our app
        self.graphFrame = graph.DPSGraph(self.dpsOutLabel, self.dpsInLabel, self.logiLabelOut, self.logiLabelIn,
                                          self.characterDetector, background="black", borderwidth="0")
        self.graphFrame.grid(row="7", column="1", rowspan="13", columnspan="19", sticky="nesw")
        self.makeDraggable(self.graphFrame.canvas.get_tk_widget())
        
    def openSettings(self):
        """Makes a Settings window
        which acceps user input, and validates it in 'doSettings'
        """
        self.settingsWindow = tk.Toplevel()
        self.settingsWindow.wm_attributes("-topmost", True)
        self.settingsWindow.wm_title("PyEveLiveDPS Settings")
        try:
            self.settingsWindow.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.settingsWindow.iconbitmap("app.ico")
            except Exception:
                pass
        self.settingsWindow.geometry("420x375")
        self.settingsWindow.update_idletasks()
        
        self.secondsVar.set(self.graphFrame.getSeconds())
        secondsLabel = tk.Label(self.settingsWindow, text="Number of seconds to average DPS:")
        secondsLabel.grid(row="0", column="0")
        secondsEntry = tk.Entry(self.settingsWindow, textvariable=self.secondsVar, width=10)
        secondsEntry.grid(row="0", column="1")
        secondsDescriptor = tk.Label(self.settingsWindow, text="Recommended to set this value higher than your weapon cycle time")
        font = tkFont.Font(font=secondsDescriptor['font'])
        font.config(slant='italic')
        secondsDescriptor['font'] = font
        secondsDescriptor.grid(row="1", column="0", columnspan="5")
        
        tk.Frame(self.settingsWindow, height="20", width="10").grid(row="2", column="1", columnspan="5")
        
        self.intervalVar.set(self.graphFrame.getInterval())
        intervalLabel = tk.Label(self.settingsWindow, text="How often to update the graph in milliseconds:")
        intervalLabel.grid(row="3", column="0")
        intervalEntry = tk.Entry(self.settingsWindow, textvariable=self.intervalVar, width=10)
        intervalEntry.grid(row="3", column="1")
        intervalDescriptor = tk.Label(self.settingsWindow, text="The lower you set this value, the higher your CPU usage will be")
        intervalDescriptor['font'] = font
        intervalDescriptor.grid(row="4", column="0", columnspan="5")
        
        tk.Frame(self.settingsWindow, height="20", width="10").grid(row="5", column="1", columnspan="5")
        
        logiFrame = tk.Frame(self.settingsWindow)
        logiFrame.grid(row="6", column="0", columnspan="5")
        
        logiOutLabel = tk.Label(logiFrame, text="Add logistics OUT tracking?")
        logiOutLabel.grid(row="0", column="0")
        self.logiOutValue = tk.BooleanVar()
        self.logiOutValue.set(self.graphFrame.getShowLogiOut())
        self.logiOutColor = self.graphFrame.getLogiOutColor()
        logiOutCheckbox = tk.Checkbutton(logiFrame, variable=self.logiOutValue, command=self.addLogiColorButton)
        logiOutCheckbox.grid(row="0", column="1")
        self.logiOutColorLabel = tk.Label(logiFrame, text="Color:")
        self.logiOutColorLabel.grid(row="0", column="2")
        self.logiOutColorButton = tk.Button(logiFrame, text="    ", 
                                            command=lambda:self.logiColorButton("out", self.logiOutColorButton), 
                                            bg=self.logiOutColor)
        self.logiOutColorButton.grid(row="0", column="3")
        if not self.logiOutValue.get():
            self.logiOutColorButton.grid_remove()
            self.logiOutColorLabel.grid_remove()
            
        logiInLabel = tk.Label(logiFrame, text="Add logistics IN tracking?")
        logiInLabel.grid(row="1", column="0")
        self.logiInValue = tk.BooleanVar()
        self.logiInValue.set(self.graphFrame.getShowLogiIn())
        self.logiInColor = self.graphFrame.getLogiInColor()
        logiInCheckbox = tk.Checkbutton(logiFrame, variable=self.logiInValue, command=self.addLogiColorButton)
        logiInCheckbox.grid(row="1", column="1")
        self.logiInColorLabel = tk.Label(logiFrame, text="Color:")
        self.logiInColorLabel.grid(row="1", column="2")
        self.logiInColorButton = tk.Button(logiFrame, text="    ", 
                                            command=lambda:self.logiColorButton("in", self.logiInColorButton), 
                                            bg=self.logiInColor)
        self.logiInColorButton.grid(row="1", column="3")
        if not self.logiInValue.get():
            self.logiInColorButton.grid_remove()
            self.logiInColorLabel.grid_remove()
        
        tk.Frame(self.settingsWindow, height="10", width="10").grid(row="7", column="1", columnspan="5")
        
        dpsInCustomLabel = tk.Label(self.settingsWindow, text="Color and threshold (when to change colors) for DPS In line:")
        dpsInCustomLabel.grid(row="8", column="0")
        font = tkFont.Font(font=dpsInCustomLabel['font'])
        font.config(weight='bold')
        dpsInCustomLabel['font'] = font
        dpsInCustomFrame = tk.Frame(self.settingsWindow)
        dpsInCustomFrame.grid(row="9", column="0", columnspan="5")
        self.dpsInSettings = self.graphFrame.getInCategories()
        for setting in self.dpsInSettings:
            valueHolder = setting["transitionValue"]
            setting["transitionValue"] = tk.StringVar()
            setting["transitionValue"].set(valueHolder)
        self.expandDPSSettings(dpsInCustomFrame, self.dpsInSettings)
        
        tk.Frame(self.settingsWindow, height="20", width="10").grid(row="10", column="1", columnspan="5")
        
        dpsOutCustomLabel = tk.Label(self.settingsWindow, text="Color and threshold (when to change colors) for DPS Out line:")
        dpsOutCustomLabel.grid(row="11", column="0")
        dpsOutCustomLabel['font'] = font
        dpsOutCustomFrame = tk.Frame(self.settingsWindow)
        dpsOutCustomFrame.grid(row="12", column="0", columnspan="5")
        self.dpsOutSettings = self.graphFrame.getOutCategories()
        for setting in self.dpsOutSettings:
            valueHolder = setting["transitionValue"]
            setting["transitionValue"] = tk.StringVar()
            setting["transitionValue"].set(valueHolder)
        self.expandDPSSettings(dpsOutCustomFrame, self.dpsOutSettings)
        
        tk.Frame(self.settingsWindow, height="30", width="10").grid(row="99", column="1", columnspan="5")
        
        buttonFrame = tk.Frame(self.settingsWindow)
        buttonFrame.grid(row="100", column="0", columnspan="5")
        okButton = tk.Button(buttonFrame, text="  Apply  ", command=self.doSettings)
        okButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame, text="  Cancel  ", command=self.settingsWindow.destroy)
        cancelButton.grid(row="0", column="2")
        
    def addLogiColorButton(self):
        if self.logiOutValue.get():
            self.logiOutColorButton.grid()
            self.logiOutColorLabel.grid()
        else:
            self.logiOutColorButton.grid_remove()
            self.logiOutColorLabel.grid_remove()
            
        if self.logiInValue.get():
            self.logiInColorButton.grid()
            self.logiInColorLabel.grid()
        else:
            self.logiInColorButton.grid_remove()
            self.logiInColorLabel.grid_remove()
        
    def logiColorButton(self, type, button):
        if (type == "out"):
            x,self.logiOutColor = colorchooser.askcolor()
            button.configure(bg=self.logiOutColor)
        elif (type == "in"):
            x,self.logiInColor = colorchooser.askcolor()
            button.configure(bg=self.logiInColor)
        
    def expandDPSSettings(self, dpsFrame, settingsList):
        index = 0
        for setting in settingsList:
            self.settingsWindow.geometry("%sx%s" % (self.settingsWindow.winfo_width(), self.settingsWindow.winfo_height()+25))
            self.settingsWindow.update_idletasks()
            removeButton = tk.Button(dpsFrame, text="X", command=lambda i=index:self.removeLine(i, settingsList, dpsFrame))
            font = tkFont.Font(font=removeButton['font'])
            font.config(weight='bold')
            removeButton['font'] = font
            removeButton.grid(row=index, column="0")
            initialLabel = tk.Label(dpsFrame, text="DPS threshold at which the line changes color:")
            initialLabel.grid(row=index, column="1")
            initialThreshold = tk.Entry(dpsFrame, textvariable=settingsList[index]["transitionValue"], width=10)
            if (index == 0):
                initialThreshold.configure(state="disabled")
                removeButton.grid_forget()
            initialThreshold.grid(row=index, column="2")
            initialLabel = tk.Label(dpsFrame, text="Color:")
            initialLabel.grid(row=index, column="3")
            colorButton = tk.Button(dpsFrame, text="    ", 
                                    command=lambda i=index:self.colorWindow(settingsList[i], colorButton), 
                                    bg=settingsList[index]["color"])
            colorButton.grid(row=index, column="4")
            index += 1
        
        addLineButton = tk.Button(dpsFrame, text="Add Another Threshold",
                                  command=lambda:self.addLine(settingsList, dpsFrame))
        addLineButton.grid(row="100", column="1")
            
    def addLine(self, settingsList, dpsFrame):
        self.settingsWindow.geometry("%sx%s" % (self.settingsWindow.winfo_width(), self.settingsWindow.winfo_height()+25))
        self.settingsWindow.update_idletasks()
        lineNumber = len(settingsList)
        settingsList.append({"transitionValue": "", "color": "#FFFFFF"})
        settingsList[lineNumber]["transitionValue"] = tk.StringVar()
        settingsList[lineNumber]["transitionValue"].set(str(100*lineNumber))
        
        
        removeButton = tk.Button(dpsFrame, text="X", command=lambda:self.removeLine(lineNumber, settingsList, dpsFrame))
        font = tkFont.Font(font=removeButton['font'])
        font.config(weight='bold')
        removeButton['font'] = font
        removeButton.grid(row=lineNumber, column="0")
        lineLabel = tk.Label(dpsFrame, text="DPS threshold at which the line changes color:")
        lineLabel.grid(row=lineNumber, column="1")
        initialThreshold = tk.Entry(dpsFrame, textvariable=settingsList[lineNumber]["transitionValue"], width=10)
        initialThreshold.grid(row=lineNumber, column="2")
        initialLabel = tk.Label(dpsFrame, text="Color:")
        initialLabel.grid(row=lineNumber, column="3")
        colorButton = tk.Button(dpsFrame, text="    ", 
                                command=lambda:self.colorWindow(settingsList[lineNumber], colorButton), 
                                bg=settingsList[lineNumber]["color"])
        colorButton.grid(row=lineNumber, column="4")
        
    def removeLine(self, index, settingsList, dpsFrame):
        self.settingsWindow.geometry("%sx%s" % (self.settingsWindow.winfo_width(), self.settingsWindow.winfo_height()-(25*len(settingsList))))
        self.settingsWindow.update_idletasks()
        settingsList.pop(index)
        for child in dpsFrame.winfo_children():
            child.destroy()
        self.expandDPSSettings(dpsFrame, settingsList)
        
    def colorWindow(self, settingsListValue, button):
        x,settingsListValue["color"] = colorchooser.askcolor()
        button.configure(bg=settingsListValue["color"])
        
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
            
        for setting in self.dpsInSettings:
            try:
                int(setting["transitionValue"].get())
            except ValueError:
                tk.messagebox.showerror("Error", "Please enter a number for all line color threshold values")
                return
        for setting in self.dpsOutSettings:
            try:
                int(setting["transitionValue"].get())
            except ValueError:
                tk.messagebox.showerror("Error", "Please enter a number for all line color threshold values")
                return
        for setting in self.dpsInSettings:
            setting["transitionValue"] = int(setting["transitionValue"].get())
        for setting in self.dpsOutSettings:
            setting["transitionValue"] = int(setting["transitionValue"].get())
            
        #Isn't python the coolest language? Look how easy this is:
        self.dpsInSettings = sorted(self.dpsInSettings, key=lambda setting: setting["transitionValue"])
        self.dpsOutSettings = sorted(self.dpsOutSettings, key=lambda setting: setting["transitionValue"])
        
        self.graphFrame.changeSettings(secondsSetting, intervalSetting, 
                                       self.logiOutValue.get(), self.logiOutColor,
                                       self.logiInValue.get(), self.logiInColor,
                                       self.dpsInSettings, self.dpsOutSettings)
        
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
        
    