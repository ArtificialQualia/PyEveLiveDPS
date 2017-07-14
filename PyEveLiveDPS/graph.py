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
import copy

class DPSGraph(tk.Frame):

    def __init__(self, dpsOutLabel, dpsInLabel, logiLabel, characterDetector, **kwargs):
        tk.Frame.__init__(self, **kwargs)
        self.dpsOutLabel = dpsOutLabel
        self.dpsInLabel = dpsInLabel
        self.logiLabel = logiLabel
        
        self.degree = 5
        self.seconds = 10
        self.interval = 100
        self.windowWidth = 410

        self.historicalDamageOut = [0] * int((self.seconds*1000)/self.interval)
        self.historicalDamageIn = [0] * int((self.seconds*1000)/self.interval)
        self.yValuesOut = np.array([0] * int((self.seconds*1000)/self.interval))
        self.yValuesIn = np.array([0] * int((self.seconds*1000)/self.interval))
        self.highestAverage = 0
        self.showLogi = False
        
        self.characterDetector = characterDetector
        self.characterDetector.setGraphInstance(self)
        
        self.graphFigure = Figure(figsize=(4,2), dpi=100, facecolor="black")
        
        self.subplot = self.graphFigure.add_subplot(1,1,1, facecolor=(0.3, 0.3, 0.3))
        self.subplot.tick_params(axis="y", colors="grey", direction="in")
        self.subplot.tick_params(axis="x", colors="grey", labelbottom="off", bottom="off")
        
        self.ySmoothIn = self.smoothListGaussian(self.yValuesIn, self.degree)
        self.ySmoothOut = self.smoothListGaussian(self.yValuesOut, self.degree)
        self.plotLineIn, = self.subplot.plot(self.ySmoothIn, 'r')
        self.plotLineOut, = self.subplot.plot(self.ySmoothOut, 'c')
        self.subplot.margins(0,0)
        
        self.yInLines = [self.plotLineIn]
        self.yInLinesCategories = [{"color": "#FF0000", "transitionValue": 0}]
        
        self.yOutLines = [self.plotLineOut]
        self.yOutLinesCategories = [{"color": "#00FFFF", "transitionValue": 0}]
        
        self.graphFigure.axes[0].get_xaxis().set_ticklabels([])
        self.graphFigure.subplots_adjust(left=(30/self.windowWidth), bottom=(15/self.windowWidth), 
                                         right=1, top=(1-15/self.windowWidth), wspace=0, hspace=0)

        self.canvas = FigureCanvasTkAgg(self.graphFigure, self)
        self.canvas.get_tk_widget().configure(bg="black")
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.ani = FuncAnimation(self.graphFigure, self.animate, interval=self.interval, blit=False, init_func=self.init_animation)
        
        self.canvas.show()
        
    def changeSettings(self, seconds, interval, logiSetting, inSettings, outSettings):
        """This function is called when a user changes settings AFTER the settings are verified in window.py"""
        self.ani.event_source.stop()
        self.subplot.clear()
        
        self.seconds = seconds
        self.interval = interval
        self.showLogi = logiSetting
        
        self.historicalDamageOut = [0] * int((self.seconds*1000)/self.interval)
        self.historicalDamageIn = [0] * int((self.seconds*1000)/self.interval)
        self.yValuesOut = np.array([0] * int((self.seconds*1000)/self.interval))
        self.yValuesIn = np.array([0] * int((self.seconds*1000)/self.interval))
        if (self.showLogi):
            self.historicalLogi = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesLogi = np.array([0] * int((self.seconds*1000)/self.interval))
            self.logiLabel.grid()
        else:
            self.logiLabel.grid_remove()
        
        if self.showLogi:
            self.ySmoothLogi = self.smoothListGaussian(self.yValuesLogi, self.degree)
            self.plotLineLogi, = self.subplot.plot(self.ySmoothLogi, 'y')
        
        self.ySmoothIn = self.smoothListGaussian(self.yValuesIn, self.degree)
        self.ySmoothOut = self.smoothListGaussian(self.yValuesOut, self.degree)
        
        self.plotLineIn, = self.subplot.plot(self.ySmoothIn, 'r')
        self.plotLineOut, = self.subplot.plot(self.ySmoothOut, 'c')
        
        self.subplot.margins(0,0)
        
        self.yInLines = [self.plotLineIn]
        self.yInLinesCategories = inSettings
        
        self.yOutLines = [self.plotLineOut]
        self.yOutLinesCategories = outSettings
        
        self.ani.event_source.interval = interval
        
        self.ani.event_source.start()
        
    def getSeconds(self):
        return self.seconds
    
    def getInterval(self):
        return self.interval
    
    def getShowLogi(self):
        return self.showLogi
    
    def getInCategories(self):
        return copy.deepcopy(self.yInLinesCategories)
    
    def getOutCategories(self):
        return copy.deepcopy(self.yOutLinesCategories)
        
    def catchup(self):
        """This is just to 'clear' the graph"""
        self.changeSettings(self.seconds, self.interval)
        
    def readjust(self, windowWidth):
        """This is for when a user resizes the window, we must change how much room we have to draw numbers
        on the left-hand side.
        Annoyingly, we have to use a %, not a number of pixels"""
        self.windowWidth = windowWidth
        if (self.highestAverage < 900):
            self.graphFigure.subplots_adjust(left=(30/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        elif (self.highestAverage < 9000):
            self.graphFigure.subplots_adjust(left=(40/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        else:
            self.graphFigure.subplots_adjust(left=(50/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        
    def init_animation(self):
        """when blitting we need this, but as of now we do not"""
        return
    
    def animate(self, i):
        damageOut,damageIn,logistics = self.characterDetector.readLog()
        
        self.historicalDamageOut.pop(0)
        self.historicalDamageOut.insert(len(self.historicalDamageOut), damageOut)
        
        self.yValuesOut = self.yValuesOut[1:]
        damageOutAverage = (np.sum(self.historicalDamageOut)*(1000/self.interval))/len(self.historicalDamageOut)
        self.yValuesOut = np.append(self.yValuesOut, damageOutAverage)
        dpsOutString = str(decimal.Decimal(damageOutAverage).quantize(decimal.Decimal('.01')))
        self.dpsOutLabel.configure(text="DPS Out: " + dpsOutString)
        
        self.historicalDamageIn.pop(0)
        self.historicalDamageIn.insert(len(self.historicalDamageIn), damageIn)
        
        self.yValuesIn = self.yValuesIn[1:]
        damageInAverage = (np.sum(self.historicalDamageIn)*(1000/self.interval))/len(self.historicalDamageIn)
        self.yValuesIn = np.append(self.yValuesIn, damageInAverage)
        dpsInString = str(decimal.Decimal(damageInAverage).quantize(decimal.Decimal('.01')))
        self.dpsInLabel.configure(text="DPS In: " + dpsInString)
        
        if self.showLogi:
            self.historicalLogi.pop(0)
            self.historicalLogi.insert(len(self.historicalLogi), logistics)
            self.yValuesLogi = self.yValuesLogi[1:]
            logiAverage = (np.sum(self.historicalLogi)*(1000/self.interval))/len(self.historicalLogi)
            self.yValuesLogi = np.append(self.yValuesLogi, logiAverage)
            logiString = str(decimal.Decimal(logiAverage).quantize(decimal.Decimal('.01')))
            self.logiLabel.configure(text="Logi: " + logiString)
        
        self.highestAverage = 0
        for i in range(len(self.yValuesOut)):
            if (self.yValuesOut[i] > self.highestAverage):
                self.highestAverage = self.yValuesOut[i]
            if (self.yValuesIn[i] > self.highestAverage):
                self.highestAverage = self.yValuesIn[i]
            if self.showLogi:
                if (self.yValuesLogi[i] > self.highestAverage):
                    self.highestAverage = self.yValuesLogi[i]
        
        
        if self.showLogi:
            self.ySmoothLogi = self.smoothListGaussian(self.yValuesLogi, self.degree)
            self.plotLineLogi.set_data(range(0, len(self.ySmoothLogi)), self.ySmoothLogi)
        
        self.ySmoothIn = self.smoothListGaussian(self.yValuesIn, self.degree)
        self.ySmoothOut = self.smoothListGaussian(self.yValuesOut, self.degree)
        
        self.animateLines()
        
        if (self.highestAverage < 100):
            self.graphFigure.axes[0].set_ylim(bottom=0, top=100)
        else:
            self.graphFigure.axes[0].set_ylim(bottom=0, top=(self.highestAverage+self.highestAverage*0.1))
        self.graphFigure.axes[0].get_yaxis().grid(True, linestyle="-", color="grey", alpha=0.2)
        self.readjust(self.windowWidth)
        
    def animateLines(self):
        """
        Magic to make many lines with colors work.
        
        This code isn't pretty, but we HAVE to avoid calling subplot.clear and
         also making new lines unless we have to in order to save CPU cycles.
         
        Yes this mess is more efficient.
        It could be split up into some functions for greater readability.
        """      
        
        ###In graph section
        
        lineCategoryTracker = 0
        lastValue = self.ySmoothIn[0]
        currentLine = []
        lineNumber = 0
        for index, value in enumerate(self.ySmoothIn):
            for categoryIndex, lineCategory in enumerate(self.yInLinesCategories):
                if categoryIndex == (len(self.yInLinesCategories)-1):
                    if value >= lineCategory["transitionValue"]:
                        if lineCategoryTracker == categoryIndex:
                            currentLine.append(value)
                        else:
                            if (lineNumber < len(self.yInLines)):
                                self.yInLines[lineNumber].set_data(range(index-len(currentLine), index), currentLine)
                                self.yInLines[lineNumber].set_color(self.yInLinesCategories[lineCategoryTracker]["color"])
                            else:
                                newLine, = self.subplot.plot(range(index-len(currentLine), index), currentLine, 
                                                            self.yInLinesCategories[lineCategoryTracker]["color"])
                                self.yInLines.append(newLine)
                            lineNumber += 1
                            lineCategoryTracker = categoryIndex
                            currentLine = []
                            currentLine.append(lastValue)
                            currentLine.append(value)
                elif value >= lineCategory["transitionValue"] and value < self.yInLinesCategories[categoryIndex+1]["transitionValue"]:
                    if lineCategoryTracker == categoryIndex:
                        currentLine.append(value)
                    else:
                        if (lineNumber < len(self.yInLines)):
                            self.yInLines[lineNumber].set_data(range(index-len(currentLine), index), currentLine)
                            self.yInLines[lineNumber].set_color(self.yInLinesCategories[lineCategoryTracker]["color"])
                        else:
                            newLine, = self.subplot.plot(range(index-len(currentLine), index), currentLine, 
                                                        self.yInLinesCategories[lineCategoryTracker]["color"])
                            self.yInLines.append(newLine)
                        lineNumber += 1
                        lineCategoryTracker = categoryIndex
                        currentLine = []
                        currentLine.append(lastValue)
                        currentLine.append(value)
            lastValue = value
        if (lineNumber < len(self.yInLines)):
            self.yInLines[lineNumber].set_data(range(len(self.ySmoothIn)-len(currentLine), len(self.ySmoothIn)), currentLine)
            self.yInLines[lineNumber].set_color(self.yInLinesCategories[lineCategoryTracker]["color"])
        else:
            newLine, = self.subplot.plot(range(len(self.ySmoothIn)-len(currentLine), len(self.ySmoothIn)), currentLine, 
                                         self.yInLinesCategories[lineCategoryTracker]["color"])
            self.yInLines.append(newLine)
            
        lineNumber += 1
        while lineNumber < len(self.yInLines):
            self.subplot.lines.remove(self.yInLines[lineNumber])
            self.yInLines.pop(lineNumber)
            lineNumber += 1
            
        ###Out graph section
        
        lineCategoryTracker = 0
        lastValue = self.ySmoothOut[0]
        currentLine = []
        lineNumber = 0
        for index, value in enumerate(self.ySmoothOut):
            for categoryIndex, lineCategory in enumerate(self.yOutLinesCategories):
                if categoryIndex == (len(self.yOutLinesCategories)-1):
                    if value >= lineCategory["transitionValue"]:
                        if lineCategoryTracker == categoryIndex:
                            currentLine.append(value)
                        else:
                            if (lineNumber < len(self.yOutLines)):
                                self.yOutLines[lineNumber].set_data(range(index-len(currentLine), index), currentLine)
                                self.yOutLines[lineNumber].set_color(self.yOutLinesCategories[lineCategoryTracker]["color"])
                            else:
                                newLine, = self.subplot.plot(range(index-len(currentLine), index), currentLine, 
                                                            self.yOutLinesCategories[lineCategoryTracker]["color"])
                                self.yOutLines.append(newLine)
                            lineNumber += 1
                            lineCategoryTracker = categoryIndex
                            currentLine = []
                            currentLine.append(lastValue)
                            currentLine.append(value)
                elif value >= lineCategory["transitionValue"] and value < self.yOutLinesCategories[categoryIndex+1]["transitionValue"]:
                    if lineCategoryTracker == categoryIndex:
                        currentLine.append(value)
                    else:
                        if (lineNumber < len(self.yOutLines)):
                            self.yOutLines[lineNumber].set_data(range(index-len(currentLine), index), currentLine)
                            self.yOutLines[lineNumber].set_color(self.yOutLinesCategories[lineCategoryTracker]["color"])
                        else:
                            newLine, = self.subplot.plot(range(index-len(currentLine), index), currentLine, 
                                                        self.yOutLinesCategories[lineCategoryTracker]["color"])
                            self.yOutLines.append(newLine)
                        lineNumber += 1
                        lineCategoryTracker = categoryIndex
                        currentLine = []
                        currentLine.append(lastValue)
                        currentLine.append(value)
            lastValue = value
        if (lineNumber < len(self.yOutLines)):
            self.yOutLines[lineNumber].set_data(range(len(self.ySmoothOut)-len(currentLine), len(self.ySmoothOut)), currentLine)
            self.yOutLines[lineNumber].set_color(self.yOutLinesCategories[lineCategoryTracker]["color"])
        else:
            newLine, = self.subplot.plot(range(len(self.ySmoothOut)-len(currentLine), len(self.ySmoothOut)), currentLine, 
                                         self.yOutLinesCategories[lineCategoryTracker]["color"])
            self.yOutLines.append(newLine)
            
        lineNumber += 1
        while lineNumber < len(self.yOutLines):
            self.subplot.lines.remove(self.yOutLines[lineNumber])
            self.yOutLines.pop(lineNumber)
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
