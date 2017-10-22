
import tkinter as tk

class PlaybackFrame(tk.Frame):
    def __init__(self, parent, startTime, endTime, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.mainWindow = parent
        self.columnconfigure(1, weight=1)
        self.configure(background="black")
        self.startTime = startTime
        self.endTime = endTime
        self.startValue = 0
        self.endValue = (endTime - startTime).seconds
        
        self.pauseButton = tk.Frame(self).grid(row="1", column="0")
        
        self.makeTimeLabel()
        self.makeTimeSlider()
        
        self.stopButton = tk.Frame(self).grid(row="1", column="2")
        
    def makeTimeSlider(self):
        self.timeSlider = tk.Scale(self, from_=self.startValue, to=self.endValue, orient=tk.constants.HORIZONTAL, 
                                   showvalue=0, command=self.timeChanged)
        self.timeSlider.configure(background="black", foreground="white", sliderrelief=tk.constants.FLAT, troughcolor="white", 
                                  activebackground="grey", relief=tk.constants.FLAT, highlightthickness=0, sliderlength=15)
        self.timeSlider.grid(row="1", column="1", sticky="we")
        
    def timeChanged(self, newValue):
        self.timeVariable.set(str(newValue))
        
    def makeTimeLabel(self):
        self.timeVariable = tk.StringVar()
        self.timeVariable.set("00:00:00")
        self.timeLabel = tk.Label(self, textvariable=self.timeVariable)
        self.timeLabel.configure(foreground="white", background="black")
        self.timeLabel.grid(row="0", column="0", columnspan="3", sticky="news")