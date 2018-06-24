"""

"""

import tkinter as tk
import tkinter.font as tkFont
from peld import settings

class DetailSettingsFrame(tk.Frame):
    text = {"dpsOut": "DPS Out",
            "dpsIn": "DPS In",
            "logiOut": "Logi Out",
            "logiIn": "Logi In",
            "capTransfered": "Cap Out",
            "capRecieved": "Cap In",
            "capDamageOut": "Cap Dmg Out",
            "capDamageIn": "Cap Dmg In"}
    def __init__(self, parent, mainWindow, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.parent = parent
        self.mainWindow = mainWindow
        self.columnconfigure(1, weight=1)
        
        tk.Frame(self, height="20", width="10").grid(row="0", column="1", columnspan="2")
        
        checkboxValue = tk.BooleanVar()
        checkboxValue.set(settings.detailsWindowShow)
        self.windowDisabled = tk.Checkbutton(self, text="Show Pilot Breakdown window", variable=checkboxValue)
        self.windowDisabled.var = checkboxValue
        self.windowDisabled.grid(row="1", column="1", columnspan="2")
        
        tk.Frame(self, height="20", width="10").grid(row="2", column="1", columnspan="2")
        
        self.makeListBox()
        
    def makeListBox(self):
        tk.Label(self, text="Order priority for pilots and weapons in the breakdown").grid(row="3", column="1")
        descriptor = tk.Label(self, text="drag and drop entries to order them")
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row="4", column="1")
        self.displayOrder = DDList(self)
        for orderItem in settings.detailsOrder:
            self.displayOrder.insert(tk.END, self.text[orderItem])
        self.displayOrder.grid(row="5", column="1")
                        
    def doSettings(self):
        detailsOrder = []
        for orderItem in self.displayOrder.get(0, tk.END):
            for orderType in self.text:
                if orderItem == self.text[orderType]:
                    detailsOrder.append(orderType)
        return {"detailsWindowShow": self.windowDisabled.var.get(), "detailsOrder": detailsOrder}
    
class DDList(tk.Listbox):
    """
    A Tkinter listbox with drag'n'drop reordering of entries. 
    from: https://www.safaribooksonline.com/library/view/python-cookbook-2nd/0596007973/ch11s05.html
    """
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.SINGLE
        kw['activestyle'] = 'none'
        kw['height'] = '0'
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None
    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)
    def shiftSelection(self, event):
        i = self.nearest(event.y)
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i