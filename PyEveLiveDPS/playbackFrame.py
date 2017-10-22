
import tkinter as tk
import datetime

class PlaybackFrame(tk.Frame):
    def __init__(self, parent, startTime, endTime, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.mainWindow = parent
        self.columnconfigure(2, weight=1)
        self.configure(background="black")
        self.startTime = startTime
        self.endTime = endTime
        self.startValue = 0
        self.endValue = (endTime - startTime).seconds
        
        self.makePauseButton()
        
        self.startTimeLabel = tk.Label(self, background="black", foreground="white", text=self.startTime.strftime("%H:%M:%S"))
        self.startTimeLabel.grid(row="1", column="1")
        
        self.makeTimeLabel()
        self.makeTimeSlider()
        
        self.endTimeLabel = tk.Label(self, background="black", foreground="white", text=self.endTime.strftime("%H:%M:%S"))
        self.endTimeLabel.grid(row="1", column="3")
        
        self.makeStopButton()
        
    def makeTimeSlider(self):
        self.timeSlider = tk.Scale(self, from_=self.startValue, to=self.endValue, orient=tk.constants.HORIZONTAL, 
                                   showvalue=0, command=self.timeChanged, bigincrement=60)
        self.timeSlider.configure(background="black", foreground="white", sliderrelief=tk.constants.FLAT, troughcolor="white", 
                                  activebackground="grey", relief=tk.constants.FLAT, highlightthickness=0, sliderlength=15)
        self.timeSlider.grid(row="1", column="2", sticky="we")
        self.timeSlider.bind("<Button>", lambda e: self.pauseButtonRelease(e) if not self.mainWindow.characterDetector.playbackLogReader.paused else False)
        self.timeSlider.bind("<Key>", lambda e: self.pauseButtonRelease(e) if not self.mainWindow.characterDetector.playbackLogReader.paused else False)
        self.timeSlider.focus_set()
        #self.timeSlider.bind("<ButtonRelease-1>", lambda e: True if not self.mainWindow.characterDetector.playbackLogReader.paused else self.pauseButtonRelease(e))
        
    def timeChanged(self, newValue):
        self.logtime = self.startTime + datetime.timedelta(seconds=int(newValue))
        self.timeVariable.set(self.logtime.strftime("%H:%M:%S"))
        
    def makeTimeLabel(self):
        self.timeVariable = tk.StringVar()
        self.timeVariable.set("00:00:00")
        self.timeLabel = tk.Label(self, textvariable=self.timeVariable)
        self.timeLabel.configure(foreground="white", background="black")
        self.timeLabel.grid(row="0", column="0", columnspan="5", sticky="news")
        
    def makePauseButton(self):
        self.pauseButton = tk.Canvas(self, width=17, height=16, background="black", borderwidth=2,
                                    highlightthickness="0", relief=tk.constants.RAISED, selectbackground="black")
        self.pauseRectLeft = self.pauseButton.create_rectangle(4,2,9,16, fill="yellow")
        self.pauseRectRight = self.pauseButton.create_rectangle(10,2,15,16, fill="yellow")
        self.pauseButton.bind("<ButtonPress-1>", self.pauseButtonPress)
        self.pauseButton.bind("<ButtonRelease-1>", self.pauseButtonRelease)
        self.pauseButton.bind("<Enter>", self.pauseButtonEnter)
        self.pauseButton.bind("<Leave>", self.pauseButtonLeave)
        
        self.pauseButton.grid(row="1", column="0")
        
    def pauseButtonPress(self, e):
        self.pauseButton.configure(relief=tk.constants.SUNKEN)
        
    def pauseButtonRelease(self, e):
        self.pauseButton.configure(relief=tk.constants.RAISED)
        if self.mainWindow.characterDetector.playbackLogReader.paused:
            self.pauseButton.delete(self.playTriangle)
            self.pauseRectLeft = self.pauseButton.create_rectangle(4,2,9,16, fill="yellow")
            self.pauseRectRight = self.pauseButton.create_rectangle(10,2,15,16, fill="yellow")
            self.mainWindow.characterDetector.playbackLogReader.newStartTime(self.logtime)
            self.mainWindow.characterDetector.playbackLogReader.paused = False
        else:
            self.pauseButton.delete(self.pauseRectLeft, self.pauseRectRight)
            self.playTriangle = self.pauseButton.create_polygon(4,2,16,9,4,16, fill="green")
            self.mainWindow.characterDetector.playbackLogReader.paused = True
            self.mainWindow.animator.catchup()
        
    def pauseButtonEnter(self, e):
        self.pauseButton.configure(background="gray25")
        
    def pauseButtonLeave(self, e):
        self.pauseButton.configure(background="black")
        
    def makeStopButton(self):
        self.stopButton = tk.Canvas(self, width=13, height=13, background="red", borderwidth=3,
                                    highlightthickness="0", relief=tk.constants.RAISED)
        self.stopButton.create_rectangle(0,0,16,16, fill="red", activefill="orange red")
        self.stopButton.bind("<ButtonPress-1>", self.stopButtonPress)
        self.stopButton.bind("<ButtonRelease-1>", self.stopButtonRelease)
        self.stopButton.bind("<Leave>", self.stopButtonLeave)
        
        self.stopButton.grid(row="1", column="4")
        
    def stopButtonPress(self, e):
        self.stopButton.configure(relief=tk.constants.SUNKEN)
        
    def stopButtonRelease(self, e):
        self.stopButton.configure(relief=tk.constants.RAISED)
        self.mainWindow.characterDetector.stopPlayback()
    
    def stopButtonLeave(self, e):
        self.stopButton.configure(relief=tk.constants.RAISED)