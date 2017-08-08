"""
DPSGraph:
    This does everything relating to the actual graph and DPS calculations.
    
    matplotlib is used for all graphing
    
    The function of interest here is "animate".  It gets run every
    self.interval, which defaults to 100ms, so a balance must be struck
    between how much we can do in that function with how often it is run.
    If the interval is too high, the graph is choppy and less accurate.
    If the interval is too low, the CPU usage spikes (mostly from redrwaing
    the graph).
    
    Blitting the graph (only rewriting parts that changed) has almost no
    effect on performance in my testing (and the ticks don't redraw, so we have
    to redraw that every frame anyways).
    
    This class does NOT follow the principle of 'don't repeat yourself'
    It doesn't really work well with how many class variables we are using.
    It would probably be a good idea to switch all our different trackers to a
    dict, and iterate on that list for all of these.  But that is a lot of
    refactoring for little benefit (readability)
"""

import matplotlib
from matplotlib.animation import FuncAnimation
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure, Axes

import numpy as np
import tkinter as tk
import logreader
import decimal
import settings
import simulator

class DPSGraph(tk.Frame):
    categories = {
        "dpsIn": { "zorder": 90 },
        "dpsOut": { "zorder": 100 },
        "logiOut": { "zorder": 80 }, 
        "logiIn": { "zorder": 70 },
        "capTransfered": { "zorder": 60 },
        "capRecieved": { "zorder": 50 },
        "capDamageOut": { "zorder": 40 }, 
        "capDamageIn": { "zorder": 30 }
        }
    def __init__(self, parent, characterDetector, settings, labelHandler, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        
        self.labelHandler = labelHandler
        self.settings = settings
        self.simulationEnabled = False
        
        self.degree = 5
        #We should be able to remove this, along with the initial adjust, but since animate would need to be moved
        self.windowWidth = self.settings.getWindowWidth()

        self.highestAverage = 0
        self.slowDown = False
        
        self.characterDetector = characterDetector
        self.characterDetector.setGraphInstance(self)
        
        self.graphFigure = Figure(figsize=(4,2), dpi=100, facecolor="black")
        
        self.subplot = self.graphFigure.add_subplot(1,1,1, facecolor=(0.3, 0.3, 0.3))
        self.subplot.tick_params(axis="y", colors="grey", direction="in")
        self.subplot.tick_params(axis="x", colors="grey", labelbottom="off", bottom="off")
        
        self.ani = None
        
        self.changeSettings()
        
        self.graphFigure.axes[0].get_xaxis().set_ticklabels([])
        self.graphFigure.subplots_adjust(left=(30/self.windowWidth), bottom=(15/self.windowWidth), 
                                         right=1, top=(1-15/self.windowWidth), wspace=0, hspace=0)

        self.canvas = FigureCanvasTkAgg(self.graphFigure, self)
        self.canvas.get_tk_widget().configure(bg="black")
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.ani = FuncAnimation(self.graphFigure, self.animate, interval=self.interval, blit=False, init_func=self.init_animation)
        
        self.canvas.show()
        
    def changeSettings(self):
        """This function is called when a user changes settings after the settings are verified"""
        if self.ani:
            self.ani.event_source.stop()
        self.subplot.clear()
        
        self.seconds = self.settings.getSeconds()
        self.interval = self.settings.getInterval()
        self.categories["dpsOut"]["settings"] = self.settings.getDpsOutSettings()
        self.categories["dpsIn"]["settings"] = self.settings.getDpsInSettings()
        self.categories["logiOut"]["settings"] = self.settings.getLogiOutSettings()
        self.categories["logiIn"]["settings"] = self.settings.getLogiInSettings()
        self.categories["capTransfered"]["settings"] = self.settings.getCapTransferedSettings()
        self.categories["capRecieved"]["settings"] = self.settings.getCapRecievedSettings()
        self.categories["capDamageOut"]["settings"] = self.settings.getCapDamageOutSettings()
        self.categories["capDamageIn"]["settings"] = self.settings.getCapDamageInSettings()
        
        if self.settings.getGraphDisabled():
            self.grid_remove()
        else:
            self.grid()
        
        self.labelHandler.redoLabels()
        
        for category, items in self.categories.items():
            if items["settings"]:
                self.labelHandler.enableLabel(category, True)
                items["historical"] = [0] * int((self.seconds*1000)/self.interval)
                items["yValues"] = np.array([0] * int((self.seconds*1000)/self.interval))
                ySmooth = self.smoothListGaussian(items["yValues"], self.degree)
                try:
                    items["labelOnly"] = items["settings"][0]["labelOnly"]
                except KeyError:
                    items["settings"][0]["labelOnly"] = False
                    items["labelOnly"] = items["settings"][0]["labelOnly"]
                if not items["labelOnly"]:
                    plotLine, = self.subplot.plot(ySmooth, zorder=items["zorder"])
                    items["lines"] = [plotLine]
            else:
                self.labelHandler.enableLabel(category, False)
        
        self.subplot.margins(0,0)
        
        if self.ani:
            self.slowDown = False
            #self.ani.event_source.interval = interval
            self.ani.event_source.start(self.interval)
        
    def simulationSettings(self, enable=False, values=None):
        if enable:
            self.simulationEnabled = True
            self.simulator = simulator.Simulator(values, self.interval)
        if not enable:
            self.simulator = None
            self.simulationEnabled = False
                
    def catchup(self):
        """This is just to 'clear' the graph"""
        self.changeSettings()
        
    def readjust(self, windowWidth):
        """
        This is for when a user resizes the window, we must change how much room we have to draw numbers
        on the left-hand side.
        Annoyingly, we have to use a %, not a number of pixels
        """
        self.windowWidth = windowWidth
        if (self.highestAverage < 900):
            self.graphFigure.subplots_adjust(left=(33/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        elif (self.highestAverage < 9000):
            self.graphFigure.subplots_adjust(left=(44/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        else:
            self.graphFigure.subplots_adjust(left=(55/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        
    def init_animation(self):
        """
        This runs before the first tic of the animation so the users don't experience a 'flash' when the
        graph changes for the first time
        """
        self.animate(0)
        return
    
    def animate(self, i):
        if self.simulationEnabled:
            damageOut,damageIn,logiOut,logiIn,capTransfered,capRecieved,capDamageOut,capDamageIn = self.simulator.simulate()
        else:
            damageOut,damageIn,logiOut,logiIn,capTransfered,capRecieved,capDamageOut,capDamageIn = self.characterDetector.readLog()
        
        self.categories["dpsOut"]["newEntry"] = damageOut
        self.categories["dpsIn"]["newEntry"] = damageIn
        self.categories["logiOut"]["newEntry"] = logiOut
        self.categories["logiIn"]["newEntry"] = logiIn
        self.categories["capTransfered"]["newEntry"] = capTransfered
        self.categories["capRecieved"]["newEntry"] = capRecieved
        self.categories["capDamageOut"]["newEntry"] = capDamageOut
        self.categories["capDamageIn"]["newEntry"] = capDamageIn
        
        for category, items in self.categories.items():
            if items["settings"]:
                items["historical"].pop(0)
                items["historical"].insert(len(items["historical"]), items["newEntry"])
                items["yValues"] = items["yValues"][1:]
                average = (np.sum(items["historical"])*(1000/self.interval))/len(items["historical"])
                items["yValues"] = np.append(items["yValues"], average)
                if not items["labelOnly"]:
                    ySmooth = self.smoothListGaussian(items["yValues"], self.degree)
                    self.animateLine(ySmooth, items["settings"], items["lines"], zorder=items["zorder"])
                    self.labelHandler.updateLabel(category, average, matplotlib.colors.to_hex(items["lines"][-1].get_color()))
                else:
                    for index, item in enumerate(items["settings"]):
                        if index == (len(items["settings"])-1):
                            if average >= item["transitionValue"]:
                                self.labelHandler.updateLabel(category, average, item["color"])
                        elif average >= item["transitionValue"] and average < items["settings"][index+1]["transitionValue"]:
                            self.labelHandler.updateLabel(category, average, item["color"])
                            break
        
        #Find highest average for the y-axis scaling
        self.highestAverage = 0
        self.highestLabelAverage = 0
        for i in range(int((self.seconds*1000)/self.interval)):
            for category, items in self.categories.items():
                if items["settings"] and not items["labelOnly"]:
                    if (items["yValues"][i] > self.highestAverage):
                        self.highestAverage = items["yValues"][i]
                elif items["settings"]:
                    if (items["yValues"][i] > self.highestAverage):
                        self.highestLabelAverage = items["yValues"][i]
        
        if (self.highestAverage < 100):
            self.graphFigure.axes[0].set_ylim(bottom=0, top=100)
        else:
            self.graphFigure.axes[0].set_ylim(bottom=0, top=(self.highestAverage+self.highestAverage*0.1))
        self.graphFigure.axes[0].get_yaxis().grid(True, linestyle="-", color="grey", alpha=0.2)
        self.readjust(self.windowWidth)
        
        if (self.highestAverage == 0 and self.highestLabelAverage == 0):
            if not self.slowDown:
                self.slowDown = True
                self.ani.event_source._set_interval(500)
        else:
            if self.slowDown:
                self.slowDown = False
                self.ani.event_source._set_interval(self.interval)
        
    def animateLine(self, smoothed, categories, lines, zorder):
        """
        Magic to make many lines with colors work.
        
        This code isn't pretty, but we HAVE to avoid calling subplot.clear and
         also making new lines unless we have to in order to save CPU cycles.
         
        Yes this mess is more efficient.
        It could be split up into some functions for greater readability.
        """
        
        lineCategoryTracker = 0
        lastValue = smoothed[0]
        currentLine = []
        lineNumber = 0
        for index, value in enumerate(smoothed):
            for categoryIndex, lineCategory in enumerate(categories):
                if categoryIndex == (len(categories)-1):
                    if value >= lineCategory["transitionValue"]:
                        if lineCategoryTracker == categoryIndex:
                            currentLine.append(value)
                        else:
                            if (lineNumber < len(lines)):
                                lines[lineNumber].set_data(range(index-len(currentLine), index), currentLine)
                                lines[lineNumber].set_color(categories[lineCategoryTracker]["color"])
                            else:
                                newLine, = self.subplot.plot(range(index-len(currentLine), index), currentLine, 
                                                            categories[lineCategoryTracker]["color"], zorder=zorder)
                                lines.append(newLine)
                            lineNumber += 1
                            lineCategoryTracker = categoryIndex
                            currentLine = []
                            currentLine.append(lastValue)
                            currentLine.append(value)
                elif value >= lineCategory["transitionValue"] and value < categories[categoryIndex+1]["transitionValue"]:
                    if lineCategoryTracker == categoryIndex:
                        currentLine.append(value)
                    else:
                        if (lineNumber < len(lines)):
                            lines[lineNumber].set_data(range(index-len(currentLine), index), currentLine)
                            lines[lineNumber].set_color(categories[lineCategoryTracker]["color"])
                        else:
                            newLine, = self.subplot.plot(range(index-len(currentLine), index), currentLine, 
                                                        categories[lineCategoryTracker]["color"], zorder=zorder)
                            lines.append(newLine)
                        lineNumber += 1
                        lineCategoryTracker = categoryIndex
                        currentLine = []
                        currentLine.append(lastValue)
                        currentLine.append(value)
            lastValue = value
        if (lineNumber < len(lines)):
            lines[lineNumber].set_data(range(len(smoothed)-len(currentLine), len(smoothed)), currentLine)
            lines[lineNumber].set_color(categories[lineCategoryTracker]["color"])
        else:
            newLine, = self.subplot.plot(range(len(smoothed)-len(currentLine), len(smoothed)), currentLine, 
                                         categories[lineCategoryTracker]["color"], zorder=zorder)
            lines.append(newLine)
            
        lineNumber += 1
        while lineNumber < len(lines):
            self.subplot.lines.remove(lines[lineNumber])
            lines.pop(lineNumber)
            lineNumber += 1
        
    def smoothListGaussian(self, list, degree=5):
        """Standard Gaussian (1D) function to smooth out out line
        It's not great computationally that we have to do this every time,
        but it makes the graph look soooo much better.
        Degree of 5 is choosen to strike a balance between prettiness and
        accuracy/granularity of data"""
        window=degree*2-1  
        weight=np.array([1.0]*window)  
        weightGauss=[]  

        for i in range(window):  
            i=i-degree+1  
            frac=i/float(window)  
            gauss=1/(np.exp((4*(frac))**2))  
            weightGauss.append(gauss)  

        weight=np.array(weightGauss)*weight  
        smoothed=[0.0]*(len(list)-window) 

        for i in range(len(smoothed)):  
            smoothed[i]=sum(np.array(list[i:i+window])*weight)/sum(weight)  

        return smoothed  
