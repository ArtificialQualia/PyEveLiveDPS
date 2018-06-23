import tkinter as tk
from peld import settings
import decimal

class LabelHandler(tk.Frame):
    labels = {"dpsOut": { "text": "DPS Out:" },
            "dpsIn": { "text": "DPS In:" },
            "logiOut": { "text": "Logi Out:" },
            "logiIn": { "text": "Logi In:" },
            "capTransfered": { "text": "Cap Out:" },
            "capRecieved": { "text": "Cap In:" },
            "capDamageOut": { "text": "Cap Dmg Out:" },
            "capDamageIn": { "text": "Cap Dmg In:" },
            "mining": { "text": "Mining:" }
            }
    def __init__(self, parent, makeAllChildrenDraggable, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.makeAllChildrenDraggable = makeAllChildrenDraggable
        self.columnconfigure(9, weight="1")
        
        tk.Frame(self, width="1", height="1", background="black").grid(row="0", column="9", rowspan="10")
        
        self.initializeLabels()
        
    def initializeLabels(self):
        self.labelSettings = settings.getLabels()
        self.labelColumns = settings.getLabelColumns()
        
        for index in self.labels:
            self.labels[index]["label"] = Label(self, text=self.labels[index]["text"], 
                                                settings=self.labelSettings[index], background="black")
            textLabel = tk.Label(self.labels[index]["label"], text=self.labels[index]["text"], fg="white", background="black")
            if self.labelSettings[index]["column"] >= self.labelColumns[0]:
                column = self.labelSettings[index]["column"] + 10
            else:
                column = self.labelSettings[index]["column"]
            self.labels[index]["label"].grid(row=self.labelSettings[index]["row"], column=column)
            self.labels[index]["label"].grid_remove()
            
        self.makeAllChildrenDraggable(self)
            
    def redoLabels(self):
        for item in self.labels:
            self.labels[item]["label"].destroy()
        self.initializeLabels()
        
    def enableLabel(self, labelName="", enable=True):
        if enable:
            self.labels[labelName]["label"].grid()
        else:
            self.labels[labelName]["label"].grid_remove()
            
    def updateLabel(self, labelName, number, color):
        self.labels[labelName]["label"].updateLabel(number, color)
        
class Label(tk.Frame):
    def __init__(self, parent, text, settings, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.decimalPlaces = settings["decimalPlaces"]
        self.inThousands = settings["inThousands"]
        self.columnconfigure(0, weight="1")
        self.columnconfigure(3, weight="1")
        
        tk.Frame(self, width="1", height="1", background="black").grid(row="0", column="0")
        tk.Frame(self, width="1", height="1", background="black").grid(row="0", column="3")
        
        tk.Label(self, text=text, fg="white", background="black").grid(row="0", column="1")
        self.numberLabel = tk.Label(self, text="0.0", fg="white", background="black")
        self.numberLabel.grid(row="0", column="2")
        
    def updateLabel(self, number, color):
        decimals = int(self.decimalPlaces)
        if self.inThousands:
            number = number/1000
            self.numberLabel["text"] = ('%.'+str(decimals)+'f') % (round(number, decimals),) + "K"
        else:
            self.numberLabel["text"] = ('%.'+str(decimals)+'f') % (round(number, decimals),)
        self.numberLabel.configure(fg=color)
        