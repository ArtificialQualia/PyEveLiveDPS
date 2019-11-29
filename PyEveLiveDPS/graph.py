"""
DPSGraph:
    This does everything relating to the actual graph and DPS calculations.
    
    matplotlib is used for all graphing
    
    Blitting the graph (only rewriting parts that changed) has almost no
    effect on performance in my testing (and the ticks don't redraw, so we have
    to redraw that every frame anyways).
    
"""

from PySide2 import QtCore

import pyqtgraph

import numpy as np
import logreader
import decimal
from peld import settings
import simulator
from legend import LegendItem, ItemSample

class DPSGraph(pyqtgraph.PlotWidget):
    def __init__(self, **kwargs):
        pyqtgraph.PlotWidget.__init__(self)
        self.hideButtons()
        self.hideAxis('bottom')
        self.viewBox = self.getPlotItem().getViewBox()
        self.viewBox.enableAutoRange(enable=False)
        self.viewBox.setAutoVisible(x=False, y=False)
        self.viewBox.setBackgroundColor('333333')
        self.viewBox.setZValue(0)
        self.viewBox.setBorder(pyqtgraph.mkPen(color='333333'))
        #self.viewBox.setLimits(yMin=0, xMin=0)
        self.axis = self.getPlotItem().getAxis('left')
        self.axis.setPen(pyqtgraph.mkPen(color='5F5F5F'))
        self.axis.setZValue(10)

        self.getPlotItem().setContentsMargins(0,4,0,4)

        
        #self.viewBox.setXRange(0,10)
        #self.viewBox.setYRange(0,10)
        #self.getPlotItem().getViewBox().setMouseEnabled(x=False,y=False)
        self.showGrid(y=True, alpha=1.0)

        x = np.linspace(0, 2*np.pi, num=1000, endpoint=False)
        y = np.sin(x)+1
        self.pen = pyqtgraph.mkPen(color='FF0000', width=2)
        self.line1 = self.plot(x, y, pen=self.pen, name='line1', antialias=True)
        self.pen = pyqtgraph.mkPen(color='00FF0050', width=2, style=QtCore.Qt.DotLine)
        self.line2 = self.plot(y, x, pen=self.pen, name='line2', antialias=True)
        self.legend = LegendItem(offset=(40,10), brush=pyqtgraph.mkBrush(100,100,100,50))
        self.legend.setParentItem(self.getPlotItem())
        self.legend.addItem(self.line1, 'linex')
        self.legend.addItem(self.line2, 'line2')

        self.highestAverage = 0
        self.viewBox.setRange(xRange=(0,100), yRange=(0,100), padding=0.0)
        self.axis.setWidth(25)
        """
        tk.Frame.__init__(self, parent, **kwargs)
        
        self.parent = parent
        self.degree = 5
        
        self.graphFigure = Figure(figsize=(4,2), dpi=100, facecolor="black")
        
        self.subplot = self.graphFigure.add_subplot(1,1,1, facecolor=(0.3, 0.3, 0.3))
        self.subplot.tick_params(axis="y", colors="grey", direction="in")
        self.subplot.tick_params(axis="x", colors="grey", labelbottom="off", bottom="off")
        
        self.graphFigure.axes[0].get_xaxis().set_ticklabels([])
        self.graphFigure.subplots_adjust(left=(30/100), bottom=(15/100), 
                                         right=1, top=(1-15/100), wspace=0, hspace=0)

        self.canvas = FigureCanvasTkAgg(self.graphFigure, self)
        self.canvas.get_tk_widget().configure(bg="black")
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.canvas.show()"""

    def update(self):
        import random
        x = np.linspace(0, 30*np.pi, num=1000, endpoint=False)
        y = np.sin(x)+1+random.random() * 50
        self.line1.setData(x,y)

    def mousePressEvent(self, event):
        event.setAccepted(False)

    def mouseMoveEvent(self, event):
        event.setAccepted(False)

    def mouseReleaseEvent(self, event):
        event.setAccepted(False)

    def wheelEvent(self, event):
        event.setAccepted(False)
        
    def readjust(self, highestAverage):
        """
        This is for use during the animation cycle, or when a user resizes the window. 
        We must change how much room we have to draw numbers on the left-hand side,
          as well as adjust the y-axis scaling.
        """
        if self.highestAverage == highestAverage:
            return

        if (highestAverage < 100):
            self.viewBox.setRange(xRange=(0,100), yRange=(0,100), padding=0.0)
            self.axis.setWidth(25)
        else:
            self.viewBox.setRange(xRange=(0,100), yRange=(0,highestAverage), padding=0.0)
        if (highestAverage < 1000):
            self.axis.setWidth(35)
        elif (highestAverage < 10000):
            self.axis.setWidth(45)
        else:
            self.axis.setWidth(55)
        
        self.highestAverage = highestAverage
        
    def animateLine(self, yValues, categories, lines, zorder):
        """
        Magic to make many lines with colors work.
        
        This code appears inefficient, but we HAVE to avoid calling subplot.clear
         and also making new lines in order to save CPU cycles.
        """
        smoothed = self.smoothListGaussian(yValues, self.degree)
        
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
        
    def basicLine(self, yValues, color, line, lineStyle='-'):
        """
        Basic single color line
        """
        smoothed = self.smoothListGaussian(yValues, self.degree)
        line.set_data(range(0, len(smoothed)), smoothed)
        line.set_color(color)
        line.set_linestyle(lineStyle)
        
    def smoothListGaussian(self, list, degree=5):
        """Standard Gaussian (1D) function to smooth out out line
        It's not great computationally that we have to do this every time,
        but it makes the graph look much better.
        Degree of 5 is chosen to strike a balance between prettiness and
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
