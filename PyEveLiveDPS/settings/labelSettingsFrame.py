import tkinter as tk
import tkinter.font as tkFont

class LabelSettingsFrame(tk.Frame):
    text = {"dpsOut": "            DPS Out:",
            "dpsIn": "             DPS In:",
            "logiOut": "           Logi Out:",
            "logiIn": "           Logi In:",
            "capTransfered": "            Cap Out:",
            "capRecieved": "              Cap In:",
            "capDamageOut": "Cap Dmg Out:",
            "capDamageIn": "  Cap Dmg In:"}
    def __init__(self, parent, mainWindow, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.mainWindow = mainWindow
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        
        infoLabel = tk.Label(self, text="Shit is complicated yo")
        infoLabel.grid(row="0", column="1", columnspan="5", pady=10)
        
        gridFrameLeft = tk.Frame(self)
        self.gridListLeft = gridListLeft = [[self.makeGridBlock(gridFrameLeft, row, i) for row in range(8)] for i in range(4)]
        gridFrameLeft.grid(row="1", column="1")
        
        tk.Frame(self, height="1", width="50").grid(row="1",column="2")
        
        gridFrameRight = tk.Frame(self)
        self.gridListRight = gridListRight = [[self.makeGridBlock(gridFrameRight, row, i) for row in range(8)] for i in range(4)]
        gridFrameRight.grid(row="1", column="3")
        
        
        singleFrame = tk.Frame(gridListLeft[0][0])
        singleFrame.grid(row="0", column="0")
        singleLabel = tk.Label(singleFrame, text="            DPS etc:")
        singleLabel.grid(row="0",column="0")
        singleEntry = tk.Entry(singleFrame, width=5)
        singleEntry.grid(row="0",column="1",)
        singleLabel.bind("<Button-1>", lambda e:self.dragStart(e, singleEntry))

        """
        singleFrame = tk.Frame(gridListLeft[0][0])
        singleFrame.grid(row="0", column="0")
        tk.Label(singleFrame, text="DPS etc:").grid(row="0",column="0")
        tk.Entry(singleFrame, width=5).grid(row="0",column="1")
        
        singleFrame = tk.Frame(gridListLeft[1][0])
        singleFrame.grid(row="0", column="0")
        tk.Label(singleFrame, text="Cap Dmg Out:").grid(row="0",column="0")
        tk.Entry(singleFrame, width=5).grid(row="0",column="1")
        """
        
    def makeGridBlock(self, parent, row, column):
        frame = tk.Frame(parent, width="125", height="25", relief="ridge", borderwidth=1)
        frame.grid(row=row, column=column, sticky="news")
        return frame
        
    def doSettings(self):
        return {}
    
    def dragStart(self, event, entry):
        event.widget.grid_remove()
        entry.grid_remove()
        #event.widget.bind_all("<ButtonRelease-1>", self.dragStop)
        #x = self.winfo_x()+self.winfo_rootx()+self.winfo_pointerx()+event.x
        #y = self.winfo_y()+self.winfo_rooty()+self.winfo_pointery()+event.y
        x = self.parent.winfo_pointerx()-event.x
        y = self.parent.winfo_pointery()-event.y
        self.floatingWindow = FloatingWindow()
        self.floatingWindow.geometry("+%s+%s" % (x, y))
        self.x = event.x
        self.y = event.y
        self.floatingWindow.StartMove(event)
        event.widget.bind("<ButtonRelease-1>", lambda e:self.dragStop(e, entry))
        event.widget.bind("<Motion>", self.dragMove)
    
    def dragStop(self, event, entry):
        self.floatingWindow.StopMove(event)
        self.x = None
        self.y = None
        event.widget.unbind("<ButtonRelease-1>")
        event.widget.unbind("<Motion>")
        
        pointerx = self.winfo_pointerx()
        pointery = self.winfo_pointery()
        for gridRow in self.gridListLeft:
            for gridBox in gridRow:
                if (pointerx >= gridBox.winfo_rootx() and pointerx <= gridBox.winfo_rootx()+125 and 
                    pointery >= gridBox.winfo_rooty() and pointery <= gridBox.winfo_rooty()+25):
                    singleFrame = tk.Frame(gridBox)
                    singleFrame.grid(row="0", column="0")
                    singleLabel = tk.Label(singleFrame, text=event.widget["text"])
                    singleLabel.grid(row="0",column="0")
                    singleEntry = tk.Entry(singleFrame, width=5)
                    singleEntry.grid(row="0",column="1",)
                    singleLabel.bind("<Button-1>", lambda e:self.dragStart(e, singleEntry))
                    return
        for gridRow in self.gridListRight:
            for gridBox in gridRow:
                if (pointerx >= gridBox.winfo_rootx() and pointerx <= gridBox.winfo_rootx()+125 and 
                    pointery >= gridBox.winfo_rooty() and pointery <= gridBox.winfo_rooty()+25):
                    singleFrame = tk.Frame(gridBox)
                    singleFrame.grid(row="0", column="0")
                    singleLabel = tk.Label(singleFrame, text=event.widget["text"])
                    singleLabel.grid(row="0",column="0")
                    singleEntry = tk.Entry(singleFrame, width=5)
                    singleEntry.grid(row="0",column="1",)
                    singleLabel.bind("<Button-1>", lambda e:self.dragStart(e, singleEntry))
                    return
        event.widget.grid()
        entry.grid()
        
    def dragMove(self, event):
        event.x = event.x - self.x
        event.y = event.y - self.y
        self.x += event.x
        self.y += event.y
        self.floatingWindow.OnMotion(event)
    
class FloatingWindow(tk.Toplevel):
    def __init__(self, *args, **kwargs):
        tk.Toplevel.__init__(self, *args, **kwargs)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)

        self.label = tk.Label(self, text="            DPS etc:")
        self.label.pack(side="right", fill="both", expand=True)

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