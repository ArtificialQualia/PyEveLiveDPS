
import tkinter as tk
from tkinter import ttk

class PlaybackFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.mainWindow = parent
        self.columnconfigure(1, weight=1)
        self.configure(background="black")
        
        self.pauseButton = tk.Frame(self).grid(row="0", column="0")
        
        self.makeTimeSlider()
        
        self.stopButton = tk.Frame(self).grid(row="0", column="2")
        
    def makeTimeSlider(self):
        ttk.Style().configure('Horizontal.TScale', background="black")
        self.timeSlider = ttk.Scale(self)
        self.timeSlider.grid(row="0", column="1", sticky="we")