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
import settings

class DPSGraph(tk.Frame):

    def __init__(self, dpsOutLabel, dpsInLabel, logiLabelOut, logiLabelIn, characterDetector, settings, **kwargs):
        tk.Frame.__init__(self, **kwargs)
        self.dpsOutLabel = dpsOutLabel
        self.dpsInLabel = dpsInLabel
        self.logiLabelOut = logiLabelOut
        self.logiLabelIn = logiLabelIn
        
        self.settings = settings
        
        self.degree = 5
        self.seconds = 10
        self.interval = 100
        self.windowWidth = 410

        self.highestAverage = 0
        
        self.characterDetector = characterDetector
        self.characterDetector.setGraphInstance(self)
        
        self.graphFigure = Figure(figsize=(4,2), dpi=100, facecolor="black")
        
        self.subplot = self.graphFigure.add_subplot(1,1,1, facecolor=(0.3, 0.3, 0.3))
        self.subplot.tick_params(axis="y", colors="grey", direction="in")
        self.subplot.tick_params(axis="x", colors="grey", labelbottom="off", bottom="off")
        
        self.damageInLinesCategories = [{"color": "#FF0000", "transitionValue": 0}]
        self.damageOutLinesCategories = [{"color": "#00FFFF", "transitionValue": 0}]
        
        self.ani = None
        
        self.changeSettings(self.seconds, self.interval, [], [], self.damageInLinesCategories, self.damageOutLinesCategories)
        
        self.graphFigure.axes[0].get_xaxis().set_ticklabels([])
        self.graphFigure.subplots_adjust(left=(30/self.windowWidth), bottom=(15/self.windowWidth), 
                                         right=1, top=(1-15/self.windowWidth), wspace=0, hspace=0)

        self.canvas = FigureCanvasTkAgg(self.graphFigure, self)
        self.canvas.get_tk_widget().configure(bg="black")
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.ani = FuncAnimation(self.graphFigure, self.animate, interval=self.interval, blit=False, init_func=self.init_animation)
        
        self.canvas.show()
        
    def changeSettings(self, seconds, interval, logiInSettings, logiOutSettings, inSettings, outSettings):
        """This function is called when a user changes settings AFTER the settings are verified in window.py"""
        if self.ani:
            self.ani.event_source.stop()
        self.subplot.clear()
        
        self.seconds = seconds
        self.interval = interval
        self.logiInLinesCategories = logiInSettings
        self.logiOutLinesCategories = logiOutSettings
        self.damageInLinesCategories = inSettings
        self.damageOutLinesCategories = outSettings
        
        if self.logiOutLinesCategories:
            self.logiLabelOut.grid()
            self.historicalLogiOut = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesLogiOut = np.array([0] * int((self.seconds*1000)/self.interval))
            ySmooth = self.smoothListGaussian(self.yValuesLogiOut, self.degree)
            plotLine, = self.subplot.plot(ySmooth, zorder=80)
            self.logiOutLines = [plotLine]
        else:
            self.logiLabelOut.grid_remove()
        
        if self.logiInLinesCategories:
            self.logiLabelIn.grid()
            self.historicalLogiIn = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesLogiIn = np.array([0] * int((self.seconds*1000)/self.interval))
            ySmooth = self.smoothListGaussian(self.yValuesLogiIn, self.degree)
            plotLine, = self.subplot.plot(ySmooth, zorder=70)
            self.logiInLines = [plotLine]
        else:
            self.logiLabelIn.grid_remove()
            
        if self.damageInLinesCategories:
            self.dpsInLabel.grid()
            self.historicalDamageIn = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesDamageIn = np.array([0] * int((self.seconds*1000)/self.interval))
            ySmooth = self.smoothListGaussian(self.yValuesDamageIn, self.degree)
            plotLine, = self.subplot.plot(ySmooth, zorder=90)
            self.yInLines = [plotLine]
        else:
            self.dpsInLabel.grid_remove()
            
        if self.damageOutLinesCategories:
            self.dpsOutLabel.grid()
            self.historicalDamageOut = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesDamageOut = np.array([0] * int((self.seconds*1000)/self.interval))
            ySmooth = self.smoothListGaussian(self.yValuesDamageOut, self.degree)
            plotLine, = self.subplot.plot(ySmooth, zorder=100)
            self.yOutLines = [plotLine]
        else:
            self.dpsOutLabel.grid_remove()
        
        self.subplot.margins(0,0)
        
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
        return copy.deepcopy(self.damageInLinesCategories)
    
    def getDpsOutCategories(self):
        return copy.deepcopy(self.damageOutLinesCategories)
        
    def catchup(self):
        """This is just to 'clear' the graph"""
        self.changeSettings(self.seconds, self.interval, self.logiInLinesCategories, self.logiOutLinesCategories,
                            self.damageInLinesCategories, self.damageOutLinesCategories)
        
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
        damageOut,damageIn,logiOut,logiIn,capTransfered,capRecieved,capDamageDone,capDamageRecieved = self.characterDetector.readLog()
        
        #This section could be split up into helper functions, but we'd have to pass so much back and forth
        # it hardly seems worth it.
        firstOutSection = True
        firstInSection = True
        if self.damageOutLinesCategories:
            self.historicalDamageOut.pop(0)
            self.historicalDamageOut.insert(len(self.historicalDamageOut), damageOut)
            self.yValuesDamageOut = self.yValuesDamageOut[1:]
            damageOutAverage = (np.sum(self.historicalDamageOut)*(1000/self.interval))/len(self.historicalDamageOut)
            self.yValuesDamageOut = np.append(self.yValuesDamageOut, damageOutAverage)
            dpsOutString = str(decimal.Decimal(damageOutAverage).quantize(decimal.Decimal('.01')))
            if firstOutSection:
                self.dpsOutLabel.configure(text="DPS Out: " + dpsOutString)
                firstOutSection = False
            ySmooth = self.smoothListGaussian(self.yValuesDamageOut, self.degree)
            self.animateLine(ySmooth, self.damageOutLinesCategories, self.yOutLines, zorder=100)
            
        if self.damageInLinesCategories:
            self.historicalDamageIn.pop(0)
            self.historicalDamageIn.insert(len(self.historicalDamageIn), damageIn)
            self.yValuesDamageIn = self.yValuesDamageIn[1:]
            damageInAverage = (np.sum(self.historicalDamageIn)*(1000/self.interval))/len(self.historicalDamageIn)
            self.yValuesDamageIn = np.append(self.yValuesDamageIn, damageInAverage)
            dpsInString = str(decimal.Decimal(damageInAverage).quantize(decimal.Decimal('.01')))
            if firstInSection:
                self.dpsInLabel.configure(text="DPS In: " + dpsInString)
                firstInSection = False
            ySmooth = self.smoothListGaussian(self.yValuesDamageIn, self.degree)
            self.animateLine(ySmooth, self.damageInLinesCategories, self.yInLines, zorder=90)
        
        if self.logiOutLinesCategories:
            self.historicalLogiOut.pop(0)
            self.historicalLogiOut.insert(len(self.historicalLogiOut), logiOut)
            self.yValuesLogiOut = self.yValuesLogiOut[1:]
            logiAverage = (np.sum(self.historicalLogiOut)*(1000/self.interval))/len(self.historicalLogiOut)
            self.yValuesLogiOut = np.append(self.yValuesLogiOut, logiAverage)
            logiString = str(decimal.Decimal(logiAverage).quantize(decimal.Decimal('.01')))
            if firstOutSection:
                self.logiLabelOut.configure(text="Logi Out: " + logiString)
                firstOutSection = False
            else:
                self.logiLabelOut.configure(text="| Logi Out: " + logiString)
            ySmooth = self.smoothListGaussian(self.yValuesLogiOut, self.degree)
            self.animateLine(ySmooth, self.logiOutLinesCategories, self.logiOutLines, zorder=80)
            
        if self.logiInLinesCategories:
            self.historicalLogiIn.pop(0)
            self.historicalLogiIn.insert(len(self.historicalLogiIn), logiIn)
            self.yValuesLogiIn = self.yValuesLogiIn[1:]
            logiAverage = (np.sum(self.historicalLogiIn)*(1000/self.interval))/len(self.historicalLogiIn)
            self.yValuesLogiIn = np.append(self.yValuesLogiIn, logiAverage)
            logiString = str(decimal.Decimal(logiAverage).quantize(decimal.Decimal('.01')))
            if firstInSection:
                self.logiLabelIn.configure(text="Logi In: " + logiString)
                firstInSection = False
            else:
                self.logiLabelIn.configure(text="Logi In: " + logiString + " |")
            ySmooth = self.smoothListGaussian(self.yValuesLogiIn, self.degree)
            self.animateLine(ySmooth, self.logiInLinesCategories, self.logiInLines, zorder=70)
        
        
        #Find highest average for the y-axis scaling
        self.highestAverage = 0
        for i in range(len(self.yValuesDamageOut)):
            if self.damageOutLinesCategories:
                if (self.yValuesDamageOut[i] > self.highestAverage):
                    self.highestAverage = self.yValuesDamageOut[i]
            if self.damageInLinesCategories:
                if (self.yValuesDamageIn[i] > self.highestAverage):
                    self.highestAverage = self.yValuesDamageIn[i]
            if self.logiOutLinesCategories:
                if (self.yValuesLogiOut[i] > self.highestAverage):
                    self.highestAverage = self.yValuesLogiOut[i]
            if self.logiInLinesCategories:
                if (self.yValuesLogiIn[i] > self.highestAverage):
                    self.highestAverage = self.yValuesLogiIn[i]
        
        if (self.highestAverage < 100):
            self.graphFigure.axes[0].set_ylim(bottom=0, top=100)
        else:
            self.graphFigure.axes[0].set_ylim(bottom=0, top=(self.highestAverage+self.highestAverage*0.1))
        self.graphFigure.axes[0].get_yaxis().grid(True, linestyle="-", color="grey", alpha=0.2)
        self.readjust(self.windowWidth)
        
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
