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
    def __init__(self, parent, labels=None, labelSettings=None, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.columnconfigure(9, weight="1")

        self.labels = labels or self.labels
        self.labelSettings = labelSettings or settings.getLabels()
        self.labelColumns = [1] if labels else settings.getLabelColumns()
        
        tk.Frame(self, width="1", height="1", background="black").grid(row="0", column="9", rowspan="10")
        
        self.initializeLabels()
        
    def initializeLabels(self):
        for index in self.labels:
            self.labels[index]["label"] = Label(self, text=self.labels[index]["text"], 
                                                settings=self.labelSettings[index], background="black")
            textLabel = tk.Label(self.labels[index]["label"], text=self.labels[index]["text"], fg="white", background="black")
            if self.labelSettings[index]["column"] >= self.labelColumns[0]:
                column = self.labelSettings[index]["column"] + 10
            else:
                column = self.labelSettings[index]["column"]
            self.labels[index]["label"].grid(row=self.labelSettings[index]["row"], column=column, sticky="n")
            self.labels[index]["label"].grid_remove()
            
    def redoLabels(self):
        self.labelSettings = settings.getLabels()
        self.labelColumns = settings.getLabelColumns()
        for item in self.labels:
            self.labels[item]["label"].destroy()
        self.initializeLabels()
        
    def enableLabel(self, labelName="", enable=True):
        if enable:
            self.labels[labelName]["label"].grid()
        else:
            self.labels[labelName]["label"].grid_remove()
        
    def enablePeak(self, labelName="", enable=True):
        self.labels[labelName]["label"].enablePeak(enable)
        
    def enableTotal(self, labelName, findColor, enable=True):
        self.labels[labelName]["label"].enableTotal(findColor, enable)
            
    def updateTotal(self, labelName, number):
        self.labels[labelName]["label"].updateTotal(number)
            
    def updateLabel(self, labelName, number, color):
        self.labels[labelName]["label"].updateLabel(number, color)
    
    def clearValues(self, findColor):
        for item in self.labels:
            self.labels[item]["label"].clearValues(findColor(item, 0))
        
class Label(tk.Frame):
    def __init__(self, parent, text, settings, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.decimalPlaces = settings["decimalPlaces"]
        self.inThousands = settings["inThousands"]
        self.columnconfigure(0, weight="1")
        self.columnconfigure(3, weight="1")
        
        tk.Frame(self, width="1", height="1", background="black").grid(row="0", column="0", rowspan="2", sticky="n")
        tk.Frame(self, width="1", height="1", background="black").grid(row="0", column="3", rowspan="2", sticky="n")
        
        tk.Label(self, text=text, fg="white", background="black").grid(row="0", column="1")
        self.numberLabel = tk.Label(self, text="0.0", fg="white", background="black")
        self.numberLabel.grid(row="0", column="2")

        self.showPeak = False
        self.peakValue = 0.0
        self.peakLabel = tk.Label(self, text="Peak:", fg="white", background="black")
        self.peakLabel.grid(row="1", column="1")
        self.peakLabel.grid_remove()
        self.peakNumberLabel = tk.Label(self, text="0.0", fg="white", background="black")
        self.peakNumberLabel.grid(row="1", column="2")
        self.peakNumberLabel.grid_remove()

        self.showTotal = False
        self.totalValue = 0.0
        self.totalLabel = tk.Label(self, text="Total:", fg="white", background="black")
        self.totalLabel.grid(row="2", column="1")
        self.totalLabel.grid_remove()
        self.totalNumberLabel = tk.Label(self, text="0.0", fg="white", background="black")
        self.totalNumberLabel.grid(row="2", column="2")
        self.totalNumberLabel.grid_remove()

        self.findColor = None

    def enablePeak(self, enable=True):
        self.showPeak = enable
        if enable:
            self.peakLabel.grid()
            self.peakNumberLabel.grid()
        else:
            self.peakLabel.grid_remove()
            self.peakNumberLabel.grid_remove()

    def enableTotal(self, findColor, enable=True):
        self.showTotal = enable
        self.findColor = findColor
        if enable:
            color = self.findColor(self.totalValue)
            self.totalNumberLabel.configure(fg=color)
            self.totalLabel.grid()
            self.totalNumberLabel.grid()
        else:
            self.totalLabel.grid_remove()
            self.totalNumberLabel.grid_remove()

    def convertNumberToStr(self, number):
        decimals = int(self.decimalPlaces)
        formatString = '{:,.'+str(decimals)+'f}'
        if self.inThousands:
            number = number/1000
            return formatString.format(round(number, decimals)) + "K"
        else:
            return formatString.format(round(number, decimals))

    def updateTotal(self, number):
        self.totalValue += number
        color = self.findColor(self.totalValue)
        self.totalNumberLabel["text"] = self.convertNumberToStr(self.totalValue)
        self.totalNumberLabel.configure(fg=color)
        
    def updateLabel(self, number, color):
        self.numberLabel["text"] = self.convertNumberToStr(number)
        self.numberLabel.configure(fg=color)
        if self.showPeak and number >= self.peakValue:
            self.peakValue = number
            self.peakNumberLabel["text"] = self.convertNumberToStr(number)
            self.peakNumberLabel.configure(fg=color)
    
    def clearValues(self, color):
        if self.totalValue:
            self.totalValue = 0
            self.totalNumberLabel["text"] = self.convertNumberToStr(0)
            self.totalNumberLabel.configure(fg=color)
        if self.peakValue:
            self.peakValue = 0
            self.peakNumberLabel["text"] = self.convertNumberToStr(0)
            self.peakNumberLabel.configure(fg=color)
        