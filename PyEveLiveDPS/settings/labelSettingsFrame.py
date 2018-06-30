"""
I really wish tkinter had native support for Drag and Drop.
But they don't.
So everything here is painfully manual.
"""

import tkinter as tk
import tkinter.font as tkFont
from peld import settings

class LabelSettingsFrame(tk.Frame):
    text = {"dpsOut": "DPS Out:",
            "dpsIn": "DPS In:",
            "logiOut": "Logi Out:",
            "logiIn": "Logi In:",
            "capTransfered": "Cap Out:",
            "capRecieved": "Cap In:",
            "capDamageOut": "Cap Dmg Out:",
            "capDamageIn": "Cap Dmg In:",
            "mining": "Mining:"}
    def __init__(self, parent, mainWindow, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.mainWindow = mainWindow
        self.columnconfigure(2, weight=1)
        
        self.gridColumns = settings.getLabelColumns()
        self.labels = settings.getLabels()
        
        tk.Label(self, text="Labels on the left grid will be attached to the left side of the window.\n" +
                    "Labels on the right grid will be attached to the right side of the window.\n\n" + 
                    "You can drag and drop labels to move them to a different position in the grid."
                    ).grid(row="0", column="1", columnspan="5", pady=10)
        tk.Label(self, text="Use the arrows to move columns from one side of the window to another."
                    ).grid(row="3", column="1", columnspan="5")
        tk.Label(self, text="The number box represents how many decimal places the label will use. 0 is no decimal places.\n" +
                    "The checkbox is to represent the number in thousands.\n\n" +
                    "For instance, if you choose '3' decimals, and check the box, the number 1,234 will show as 1.234K"
                    ).grid(row="100", column="1", columnspan="5", pady=10)
        
        tk.Frame(self, height="1", width="10").grid(row="1",column="2")
        
        self.makeArrowButtons()
        
        self.makeGrids()
        
    def makeGrids(self):
        self.gridFrameLeft = tk.Frame(self)
        self.gridListLeft = [[self.makeGridBlock(self.gridFrameLeft, row, i) for row in range(8)] for i in range(self.gridColumns[0])]
        self.gridFrameLeft.grid(row="5", column="1", padx="10")
        
        self.gridFrameRight = tk.Frame(self)
        self.gridListRight = [[self.makeGridBlock(self.gridFrameRight, row, i) for row in range(8)] for i in range(self.gridColumns[1])]
        self.gridFrameRight.grid(row="5", column="3", padx="10")
        
        for item, entries in self.labels.items():
            row = entries["row"]
            column = entries["column"]
            title = self.text[item]
            try:
                GridEntry(self.gridListLeft[column][row], 
                            title, entries["decimalPlaces"], entries["inThousands"])
            except IndexError:
                column = column - len(self.gridListLeft)
                GridEntry(self.gridListRight[column][row], 
                            title, entries["decimalPlaces"], entries["inThousands"])
        
    def makeArrowButtons(self):
        leftButton = tk.Canvas(self, width=15, height=15)
        leftButton.create_polygon(1,1,15,8,1,15, fill="black")
        leftButton.grid(row="4", column="1", sticky="e")
        leftButton.bind("<Button-1>", self.moveRowRight)
        
        rightButton = tk.Canvas(self, width=15, height=15)
        rightButton.create_polygon(15,15,1,8,15,1, fill="black")
        rightButton.grid(row="4", column="3", sticky="w")
        rightButton.bind("<Button-1>", self.moveRowLeft)
        
    def moveRowRight(self, event):
        if len(self.gridListLeft) == 0:
            return
        self.gridColumns[0] -= 1
        self.gridColumns[1] += 1
        self.saveLabels()
        self.gridFrameLeft.destroy()
        self.gridFrameRight.destroy()
        self.makeGrids()
        
    def moveRowLeft(self, event):
        if len(self.gridListRight) == 0:
            return
        self.gridColumns[0] += 1
        self.gridColumns[1] -= 1
        self.saveLabels()
        self.gridFrameLeft.destroy()
        self.gridFrameRight.destroy()
        self.makeGrids()
        
    def saveLabels(self):
        columnAdder = 0
        for gridFrame in [self.gridListLeft, self.gridListRight]:
            for column, gridColumn in enumerate(gridFrame):
                for row, gridBox in enumerate(gridColumn):
                    gridBoxChildren = gridBox.winfo_children()
                    if len(gridBoxChildren) > 0:
                        gridEntry = gridBoxChildren[0]
                        for name, text in self.text.items():
                            if text == gridEntry.getLabelText():
                                self.labels[name]["row"] = row
                                self.labels[name]["column"] = column + columnAdder
                                self.labels[name]["decimalPlaces"] = gridEntry.getListboxValue()
                                self.labels[name]["inThousands"] = gridEntry.getCheckboxValue()
            columnAdder += len(gridFrame)
        
    def makeGridBlock(self, parent, row, column):
        frame = tk.Frame(parent, width="100", height="25", relief="ridge", borderwidth=1)
        frame.columnconfigure(0,weight=1)
        frame.grid(row=row, column=column, sticky="news")
        return frame
        
    def moveGridEntry(self, title, decimalPlaces, inThousands, gridBox, parent):
        oldBox = self._nametowidget(parent.winfo_parent())
        if len(gridBox.winfo_children()) > 0 and not gridBox.winfo_children()[0] == parent:
            #this means we need to swap boxes
            gridEntry = gridBox.winfo_children()[0]
            parent.destroy()
            GridEntry(oldBox, gridEntry.getLabelText(), gridEntry.getListboxValue(), gridEntry.getCheckboxValue())
            gridEntry.destroy()
        else:
            parent.destroy()
        oldBox.configure(width=100)
        GridEntry(gridBox, title, decimalPlaces, inThousands)
                        
    def doSettings(self):
        self.saveLabels()
        labelColumns = [len(self.gridListLeft), len(self.gridListRight)]
        return {"labels": self.labels, "labelColumns": labelColumns}
    
class GridEntry(tk.Frame):
    def __init__(self, parent=None, title="", decimalPlaces=0, inThousands=0, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        gridFrame = self._nametowidget(parent.winfo_parent())
        self.parent = self._nametowidget(gridFrame.winfo_parent())
        
        self.grid(row="0", column="0", sticky="ew")
        self.columnconfigure(0,weight=1)
        self.singleLabel = singleLabel = tk.Label(self, text=title)
        singleLabel.grid(row="0",column="0", sticky="ew")
        self.listbox = listbox = tk.Spinbox(self, from_=0, to=9, width=1, borderwidth=1, highlightthickness=0)
        listbox.delete(0,tk.END)
        listbox.insert(0,decimalPlaces)
        listbox.grid(row="0", column="1")
        checkboxValue = tk.IntVar()
        checkboxValue.set(inThousands)
        self.checkbox = checkbox = tk.Checkbutton(self, text="K", variable=checkboxValue, borderwidth=0, highlightthickness=0)
        checkbox.var = checkboxValue
        checkbox.grid(row="0", column="2")
        singleLabel.bind("<Button-1>", lambda e:self.dragStart(e, listbox, checkbox))
        
    def dragStart(self, event, listbox, checkbox):
        event.widget.grid_remove()
        listbox.grid_remove()
        checkbox.grid_remove()
        x = self.winfo_pointerx()-event.x
        y = self.winfo_pointery()-event.y
        self.floatingWindow = FloatingWindow(self, width=self.winfo_width())
        self.floatingWindow.geometry("+%s+%s" % (x, y))
        self.x = event.x
        self.y = event.y
        self.floatingWindow.StartMove(event)
        event.widget.bind("<ButtonRelease-1>", lambda e:self.dragStop(e, listbox, checkbox))
        event.widget.bind("<Motion>", self.dragMove)
    
    def dragStop(self, event, listbox, checkbox):
        self.floatingWindow.StopMove(event)
        self.x = None
        self.y = None
        event.widget.unbind("<ButtonRelease-1>")
        event.widget.unbind("<Motion>")
        
        pointerx = self.winfo_pointerx()
        pointery = self.winfo_pointery()
        for gridSection in [self.parent.gridListLeft, self.parent.gridListRight]:
            for gridRow in gridSection:
                for gridBox in gridRow:
                    if (pointerx >= gridBox.winfo_rootx() and pointerx <= gridBox.winfo_rootx()+gridBox.winfo_width() and 
                         pointery >= gridBox.winfo_rooty() and pointery <= gridBox.winfo_rooty()+gridBox.winfo_height()):
                        parentName = event.widget.winfo_parent()
                        parent = event.widget._nametowidget(parentName)
                        self.parent.moveGridEntry(title=event.widget["text"], decimalPlaces=listbox.get(), inThousands=checkbox.var.get(),
                                                   gridBox=gridBox, parent=parent)
                        return
        event.widget.grid()
        listbox.grid()
        checkbox.grid()
        
    def dragMove(self, event):
        event.x = event.x - self.x
        event.y = event.y - self.y
        self.x += event.x
        self.y += event.y
        self.floatingWindow.OnMotion(event)
        
    def getLabelText(self):
        return self.singleLabel["text"]
    
    def getListboxValue(self):
        return self.listbox.get()
    
    def getCheckboxValue(self):
        return self.checkbox.var.get()
    
class FloatingWindow(tk.Toplevel):
    def __init__(self, gridEntry=None, width=100, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.columnconfigure(0, weight=1)
        
        GridEntry(self, gridEntry.getLabelText(), gridEntry.getListboxValue(), gridEntry.getCheckboxValue()).grid(row="0", column="0")
        
        self.update_idletasks()
        self.geometry("%sx%s" % (width, self.winfo_height()))

    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None
        self.destroy()

    def OnMotion(self, event):
        x = self.winfo_x() + event.x
        y = self.winfo_y() + event.y
        self.geometry("+%s+%s" % (x, y))