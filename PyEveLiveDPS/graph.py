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

class DPSGraph(tk.Frame):

    def __init__(self, dpsOutLabel, dpsInLabel, logiLabelOut, logiLabelIn,
                 capTransferedLabel, capRecievedLabel, capDamageOutLabel, capDamageInLabel,
                 characterDetector, settings, **kwargs):
        tk.Frame.__init__(self, **kwargs)
        self.dpsOutLabel = dpsOutLabel
        self.dpsInLabel = dpsInLabel
        self.logiLabelOut = logiLabelOut
        self.logiLabelIn = logiLabelIn
        self.capTransferedLabel = capTransferedLabel
        self.capRecievedLabel = capRecievedLabel
        self.capDamageOutLabel = capDamageOutLabel
        self.capDamageInLabel = capDamageInLabel
        
        self.settings = settings
        
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
        
        self.changeSettings(self.settings.getSeconds(), self.settings.getInterval(), 
                            self.settings.getLogiInSettings(), self.settings.getLogiOutSettings(),
                            self.settings.getDpsInSettings(), self.settings.getDpsOutSettings(),
                            self.settings.getCapDamageInSettings(), self.settings.getCapDamageOutSettings(),
                            self.settings.getCapRecievedSettings(), self.settings.getCapTransferedSettings())
        
        self.graphFigure.axes[0].get_xaxis().set_ticklabels([])
        self.graphFigure.subplots_adjust(left=(30/self.windowWidth), bottom=(15/self.windowWidth), 
                                         right=1, top=(1-15/self.windowWidth), wspace=0, hspace=0)

        self.canvas = FigureCanvasTkAgg(self.graphFigure, self)
        self.canvas.get_tk_widget().configure(bg="black")
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.ani = FuncAnimation(self.graphFigure, self.animate, interval=self.interval, blit=False, init_func=self.init_animation)
        
        self.canvas.show()
        
    def changeSettings(self, seconds=None, interval=None,
                       logiInSettings=None, logiOutSettings=None, inSettings=None, outSettings=None,
                       capDamageIn=None, capDamageOut=None, capRecieved=None, capTransfered=None):
        """This function is called when a user changes settings AFTER the settings are verified in window.py"""
        if self.ani:
            self.ani.event_source.stop()
        self.subplot.clear()
        
        self.seconds = seconds
        self.interval = interval
        self.capDamageInCategories = capDamageIn
        self.capDamageOutCategories = capDamageOut
        self.capRecievedCategories = capRecieved
        self.capTransferedCategories = capTransfered
        self.logiInLinesCategories = logiInSettings
        self.logiOutLinesCategories = logiOutSettings
        self.damageInLinesCategories = inSettings
        self.damageOutLinesCategories = outSettings
        
        if self.capDamageOutCategories:
            self.capDamageOutLabel.grid()
            self.historicalCapDamageOut = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesCapDamageOut = np.array([0] * int((self.seconds*1000)/self.interval))
            ySmooth = self.smoothListGaussian(self.yValuesCapDamageOut, self.degree)
            plotLine, = self.subplot.plot(ySmooth, zorder=30)
            self.capDamageOutLines = [plotLine]
        else:
            self.capDamageOutLabel.grid_remove()
        
        if self.capDamageInCategories:
            self.capDamageInLabel.grid()
            self.historicalCapDamageIn = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesCapDamageIn = np.array([0] * int((self.seconds*1000)/self.interval))
            ySmooth = self.smoothListGaussian(self.yValuesCapDamageIn, self.degree)
            plotLine, = self.subplot.plot(ySmooth, zorder=40)
            self.capDamageInLines = [plotLine]
        else:
            self.capDamageInLabel.grid_remove()
            
        if self.capTransferedCategories:
            self.capTransferedLabel.grid()
            self.historicalCapTransfered = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesCapTransfered = np.array([0] * int((self.seconds*1000)/self.interval))
            ySmooth = self.smoothListGaussian(self.yValuesCapTransfered, self.degree)
            plotLine, = self.subplot.plot(ySmooth, zorder=50)
            self.capTransferedLines = [plotLine]
        else:
            self.capTransferedLabel.grid_remove()
            
        if self.capRecievedCategories:
            self.capRecievedLabel.grid()
            self.historicalCapRecieved = [0] * int((self.seconds*1000)/self.interval)
            self.yValuesCapRecieved = np.array([0] * int((self.seconds*1000)/self.interval))
            ySmooth = self.smoothListGaussian(self.yValuesCapRecieved, self.degree)
            plotLine, = self.subplot.plot(ySmooth, zorder=60)
            self.capRecievedLines = [plotLine]
        else:
            self.capRecievedLabel.grid_remove()
        
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
            self.slowDown = False
            #self.ani.event_source.interval = interval
            self.ani.event_source.start(interval)
        
    def catchup(self):
        """This is just to 'clear' the graph"""
        self.changeSettings(self.seconds, self.interval, self.logiInLinesCategories, self.logiOutLinesCategories,
                            self.damageInLinesCategories, self.damageOutLinesCategories,
                            self.capDamageInCategories, self.capDamageOutCategories, 
                            self.capRecievedCategories, self.capTransferedCategories)
        
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
        damageOut,damageIn,logiOut,logiIn,capTransfered,capRecieved,capDamageOut,capDamageIn = self.characterDetector.readLog()
        
        #This section should really be split up into helper functions
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
            
        if self.capRecievedCategories:
            self.historicalCapRecieved.pop(0)
            self.historicalCapRecieved.insert(len(self.historicalCapRecieved), capRecieved)
            self.yValuesCapRecieved = self.yValuesCapRecieved[1:]
            average = (np.sum(self.historicalCapRecieved)*(1000/self.interval))/len(self.historicalCapRecieved)
            self.yValuesCapRecieved = np.append(self.yValuesCapRecieved, average)
            labelString = str(decimal.Decimal(average).quantize(decimal.Decimal('.01')))
            if firstInSection:
                self.capRecievedLabel.configure(text="Cap In: " + labelString)
                firstInSection = False
            else:
                self.capRecievedLabel.configure(text="Cap In: " + labelString + " |")
            ySmooth = self.smoothListGaussian(self.yValuesCapRecieved, self.degree)
            self.animateLine(ySmooth, self.capRecievedCategories, self.capRecievedLines, zorder=60)
            
        if self.capTransferedCategories:
            self.historicalCapTransfered.pop(0)
            self.historicalCapTransfered.insert(len(self.historicalCapTransfered), capTransfered)
            self.yValuesCapTransfered = self.yValuesCapTransfered[1:]
            average = (np.sum(self.historicalCapTransfered)*(1000/self.interval))/len(self.historicalCapTransfered)
            self.yValuesCapTransfered = np.append(self.yValuesCapTransfered, average)
            labelString = str(decimal.Decimal(average).quantize(decimal.Decimal('.01')))
            if firstOutSection:
                self.capTransferedLabel.configure(text="Cap Out: " + labelString)
                firstOutSection = False
            else:
                self.capTransferedLabel.configure(text="| Cap Out: " + labelString)
            ySmooth = self.smoothListGaussian(self.yValuesCapTransfered, self.degree)
            self.animateLine(ySmooth, self.capTransferedCategories, self.capTransferedLines, zorder=50)
            
        if self.capDamageInCategories:
            self.historicalCapDamageIn.pop(0)
            self.historicalCapDamageIn.insert(len(self.historicalCapDamageIn), capDamageIn)
            self.yValuesCapDamageIn = self.yValuesCapDamageIn[1:]
            average = (np.sum(self.historicalCapDamageIn)*(1000/self.interval))/len(self.historicalCapDamageIn)
            self.yValuesCapDamageIn = np.append(self.yValuesCapDamageIn, average)
            labelString = str(decimal.Decimal(average).quantize(decimal.Decimal('.01')))
            if firstInSection:
                self.capDamageInLabel.configure(text="Cap Dmg In: " + labelString)
                firstInSection = False
            else:
                self.capDamageInLabel.configure(text="Cap Dmg In: " + labelString + " |")
            ySmooth = self.smoothListGaussian(self.yValuesCapDamageIn, self.degree)
            self.animateLine(ySmooth, self.capDamageInCategories, self.capDamageInLines, zorder=40)
            
        if self.capDamageOutCategories:
            self.historicalCapDamageOut.pop(0)
            self.historicalCapDamageOut.insert(len(self.historicalCapDamageOut), capDamageOut)
            self.yValuesCapDamageOut = self.yValuesCapDamageOut[1:]
            average = (np.sum(self.historicalCapDamageOut)*(1000/self.interval))/len(self.historicalCapDamageOut)
            self.yValuesCapDamageOut = np.append(self.yValuesCapDamageOut, average)
            labelString = str(decimal.Decimal(average).quantize(decimal.Decimal('.01')))
            if firstOutSection:
                self.capDamageOutLabel.configure(text="Cap Dmg Out: " + labelString)
                firstOutSection = False
            else:
                self.capDamageOutLabel.configure(text="| Cap Dmg Out: " + labelString)
            ySmooth = self.smoothListGaussian(self.yValuesCapDamageOut, self.degree)
            self.animateLine(ySmooth, self.capDamageOutCategories, self.capDamageOutLines, zorder=30)
        
        #Find highest average for the y-axis scaling
        self.highestAverage = 0
        for i in range(int((self.seconds*1000)/self.interval)):
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
            if self.capRecievedCategories:
                if (self.yValuesCapRecieved[i] > self.highestAverage):
                    self.highestAverage = self.yValuesCapRecieved[i]
            if self.capTransferedCategories:
                if (self.yValuesCapTransfered[i] > self.highestAverage):
                    self.highestAverage = self.yValuesCapTransfered[i]
            if self.capDamageInCategories:
                if (self.yValuesCapDamageIn[i] > self.highestAverage):
                    self.highestAverage = self.yValuesCapDamageIn[i]
            if self.capDamageOutCategories:
                if (self.yValuesCapDamageOut[i] > self.highestAverage):
                    self.highestAverage = self.yValuesCapDamageOut[i]
        
        if (self.highestAverage < 100):
            self.graphFigure.axes[0].set_ylim(bottom=0, top=100)
        else:
            self.graphFigure.axes[0].set_ylim(bottom=0, top=(self.highestAverage+self.highestAverage*0.1))
        self.graphFigure.axes[0].get_yaxis().grid(True, linestyle="-", color="grey", alpha=0.2)
        self.readjust(self.windowWidth)
        
        if (self.highestAverage == 0):
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
