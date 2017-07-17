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

    def __init__(self, dpsOutLabel, dpsInLabel, logiLabelOut, logiLabelIn, characterDetector, **kwargs):
        tk.Frame.__init__(self, **kwargs)
        self.dpsOutLabel = dpsOutLabel
        self.dpsInLabel = dpsInLabel
        self.logiLabelOut = logiLabelOut
        self.logiLabelIn = logiLabelIn
        
        self.degree = 5
        self.seconds = 10
        self.interval = 100
        self.windowWidth = 410

        self.historicalDamageOut = [0] * int((self.seconds*1000)/self.interval)
        self.historicalDamageIn = [0] * int((self.seconds*1000)/self.interval)
        self.yValuesOut = np.array([0] * int((self.seconds*1000)/self.interval))
        self.yValuesIn = np.array([0] * int((self.seconds*1000)/self.interval))
        self.highestAverage = 0
        self.showLogiIn = False
        self.showLogiOut = False
        self.logiInColor = "#FFFF00"
        self.logiOutColor = "#FFFF00"
        
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
        
        self.ani = None
        
        self.changeSettings(self.seconds, self.interval, [], [], self.yInLinesCategories, self.yOutLinesCategories)
        
        self.ani = FuncAnimation(self.graphFigure, self.animate, interval=self.interval, blit=False, init_func=self.init_animation)
        
        self.canvas.show()
        
    def changeSettings(self, seconds, interval, logiOutSettings, logiInSettings, inSettings, outSettings):
        """This function is called when a user changes settings AFTER the settings are verified in window.py"""
        if self.ani:
            self.ani.event_source.stop()
        self.subplot.clear()
        
        self.seconds = seconds
        self.interval = interval
        self.logiInLinesCategories = logiInSettings
        self.logiOutLinesCategories = logiOutSettings
        self.yInLinesCategories = inSettings
        self.yOutLinesCategories = outSettings
        
        self.historicalDamageOut = [0] * int((self.seconds*1000)/self.interval)
        self.historicalDamageIn = [0] * int((self.seconds*1000)/self.interval)
        self.yValuesOut = np.array([0] * int((self.seconds*1000)/self.interval))
        self.yValuesIn = np.array([0] * int((self.seconds*1000)/self.interval))
        if self.logiOutLinesCategories:
            self.historicalLogiOut = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesLogiOut = np.array([0] * int((self.seconds*1000)/self.interval))
            self.logiLabelOut.grid()
            self.ySmoothLogiOut = self.smoothListGaussian(self.yValuesLogiOut, self.degree)
            self.plotLineLogiOut, = self.subplot.plot(self.ySmoothLogiOut, self.logiOutColor)
            self.logiOutLines = [self.plotLineLogiOut]
        else:
            self.logiLabelOut.grid_remove()
        
        if self.logiInLinesCategories:
            self.historicalLogiIn = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesLogiIn = np.array([0] * int((self.seconds*1000)/self.interval))
            self.logiLabelIn.grid()
            self.ySmoothLogiIn = self.smoothListGaussian(self.yValuesLogiIn, self.degree)
            self.plotLineLogiIn, = self.subplot.plot(self.ySmoothLogiIn, self.logiInColor)
            self.logiInLines = [self.plotLineLogiIn]
        else:
            self.logiLabelIn.grid_remove()
            
        
        self.ySmoothIn = self.smoothListGaussian(self.yValuesIn, self.degree)
        self.ySmoothOut = self.smoothListGaussian(self.yValuesOut, self.degree)
        
        self.plotLineIn, = self.subplot.plot(self.ySmoothIn, 'r')
        self.plotLineOut, = self.subplot.plot(self.ySmoothOut, 'c')
        
        self.subplot.margins(0,0)
        
        self.yInLines = [self.plotLineIn]
        self.yOutLines = [self.plotLineOut]
        
        if self.ani:
            self.ani.event_source.interval = interval
            self.ani.event_source.start()
        
    def getSeconds(self):
        return self.seconds
    
    def getInterval(self):
        return self.interval
    
    def getLogiOutCategories(self):
        return copy.deepcopy(self.logiOutLinesCategories)
    
    def getLogiInCategories(self):
        return copy.deepcopy(self.logiInLinesCategories)
    
    def getDpsInCategories(self):
        return copy.deepcopy(self.yInLinesCategories)
    
    def getDpsOutCategories(self):
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
            self.graphFigure.subplots_adjust(left=(33/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        elif (self.highestAverage < 9000):
            self.graphFigure.subplots_adjust(left=(44/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        else:
            self.graphFigure.subplots_adjust(left=(55/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth))
        
    def init_animation(self):
        """when blitting we need this, but as of now we do not"""
        return
    
    def animate(self, i):
        damageOut,damageIn,logiOut,logiIn = self.characterDetector.readLog()
        
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
        
        if self.logiOutLinesCategories:
            self.historicalLogiOut.pop(0)
            self.historicalLogiOut.insert(len(self.historicalLogiOut), logiOut)
            self.yValuesLogiOut = self.yValuesLogiOut[1:]
            logiAverage = (np.sum(self.historicalLogiOut)*(1000/self.interval))/len(self.historicalLogiOut)
            self.yValuesLogiOut = np.append(self.yValuesLogiOut, logiAverage)
            logiString = str(decimal.Decimal(logiAverage).quantize(decimal.Decimal('.01')))
            self.logiLabelOut.configure(text="| Logi Out: " + logiString)
            self.ySmoothLogiOut = self.smoothListGaussian(self.yValuesLogiOut, self.degree)
            self.animateLine(self.ySmoothLogiOut, self.logiOutLinesCategories, self.logiOutLines)
            
        if self.logiInLinesCategories:
            self.historicalLogiIn.pop(0)
            self.historicalLogiIn.insert(len(self.historicalLogiIn), logiIn)
            self.yValuesLogiIn = self.yValuesLogiIn[1:]
            logiAverage = (np.sum(self.historicalLogiIn)*(1000/self.interval))/len(self.historicalLogiIn)
            self.yValuesLogiIn = np.append(self.yValuesLogiIn, logiAverage)
            logiString = str(decimal.Decimal(logiAverage).quantize(decimal.Decimal('.01')))
            self.logiLabelIn.configure(text="Logi In: " + logiString + " |")
            self.ySmoothLogiIn = self.smoothListGaussian(self.yValuesLogiIn, self.degree)
            self.animateLine(self.ySmoothLogiIn, self.logiInLinesCategories, self.logiInLines)
        
        #Find highest average for the y-axis scaling
        self.highestAverage = 0
        for i in range(len(self.yValuesOut)):
            if (self.yValuesOut[i] > self.highestAverage):
                self.highestAverage = self.yValuesOut[i]
            if (self.yValuesIn[i] > self.highestAverage):
                self.highestAverage = self.yValuesIn[i]
            if self.logiOutLinesCategories:
                if (self.yValuesLogiOut[i] > self.highestAverage):
                    self.highestAverage = self.yValuesLogiOut[i]
            if self.logiInLinesCategories:
                if (self.yValuesLogiIn[i] > self.highestAverage):
                    self.highestAverage = self.yValuesLogiIn[i]
        
        self.ySmoothIn = self.smoothListGaussian(self.yValuesIn, self.degree)
        self.ySmoothOut = self.smoothListGaussian(self.yValuesOut, self.degree)
        
        self.animateLine(self.ySmoothIn, self.yInLinesCategories, self.yInLines)
        self.animateLine(self.ySmoothOut, self.yOutLinesCategories, self.yOutLines)
        
        if (self.highestAverage < 100):
            self.graphFigure.axes[0].set_ylim(bottom=0, top=100)
        else:
            self.graphFigure.axes[0].set_ylim(bottom=0, top=(self.highestAverage+self.highestAverage*0.1))
        self.graphFigure.axes[0].get_yaxis().grid(True, linestyle="-", color="grey", alpha=0.2)
        self.readjust(self.windowWidth)
        
    def animateLine(self, smoothed, categories, lines):
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
                                                            categories[lineCategoryTracker]["color"])
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
                                                        categories[lineCategoryTracker]["color"])
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
                                         categories[lineCategoryTracker]["color"])
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
