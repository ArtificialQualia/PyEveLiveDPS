"""
DPSGraph:
    This does everything relating to the actual graph and DPS calculations.
    
    matplotlib is used for all graphing
    
    Blitting the graph (only rewriting parts that changed) has almost no
    effect on performance in my testing (and the ticks don't redraw, so we have
    to redraw that every frame anyways).
    
"""

from vispy import app, scene, plot

import numpy as np
import logreader
import decimal
from peld import settings
import simulator

class DPSGraph(scene.SceneCanvas):
    def __init__(self, **kwargs):
        scene.SceneCanvas.__init__(self, keys=None)

        # Overwrite vispy native mouse handling to allow dragging the window
        self.connect(self.on_mouse_press)
        self.connect(self.on_mouse_move)

        self.create_native()

        x = np.linspace(0, 2*np.pi, num=1000, endpoint=False)
        y = np.sin(x)
        self.unfreeze()
        self.view = self.central_widget.add_view()
        #self.view.camera = scene.TurntableCamera(up='z', fov=60)
        self.view.camera = scene.PanZoomCamera()

        #xx, yy = np.arange(-1,1,.02),np.arange(-1,1,.02)
        #X,Y = np.meshgrid(xx,yy)
        #R = np.sqrt(X**2+Y**2)
        #Z = lambda t : 0.1*np.sin(10*R-2*np.pi*t)
        #surf = scene.visuals.SurfacePlot(xx, yy, Z(0), color=[0.5, 0.5, 0.5], shading='smooth', parent=self.view.scene)

        self.gridLines = scene.visuals.GridLines(scale=(0,1), color=[0.5, 0.5, 0.5, 1], parent=self.view.scene)
        self.line = scene.visuals.Line(np.array([[0,0], [0.1,0.2],[1,1],[2,2], [0.5,0.5]]), color=[1, 0, 0, 0.5], width=100, method='gl', parent=self.view.scene)
        self.axis = scene.visuals.Axis(pos=[(0.1,0), (0.1,1)], axis_width=10, axis_color=[0.5, 0.5, 0.5, 0.9], parent=self.view.scene)
        #self.freeze()
        import random
        self.timer = app.Timer(app=self.app, start=True, interval=0.05, connect=lambda e: self.line.set_data(np.array([[0, 0], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()], [random.random(), random.random()]])))

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

    def on_mouse_press(self, event):
        event.native.setAccepted(False)

    def on_mouse_move(self, event):
        event.native.setAccepted(False)
        
    def readjust(self, highestAverage):
        """
        This is for use during the animation cycle, or when a user resizes the window. 
        We must change how much room we have to draw numbers on the left-hand side,
          as well as adjust the y-axis values.
        Annoyingly, we have to use a %, not a number of pixels
        """
        self.windowWidth = self.winfo_width()
        if (highestAverage < 900):
            self.graphFigure.subplots_adjust(left=(33/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth), wspace=0, hspace=0)
        elif (highestAverage < 9000):
            self.graphFigure.subplots_adjust(left=(44/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth), wspace=0, hspace=0)
        elif (highestAverage < 90000):
            self.graphFigure.subplots_adjust(left=(55/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth), wspace=0, hspace=0)
        else:
            self.graphFigure.subplots_adjust(left=(66/self.windowWidth), top=(1-15/self.windowWidth), 
                                             bottom=(15/self.windowWidth), wspace=0, hspace=0)
        if (highestAverage < 100):
            self.graphFigure.axes[0].set_ylim(bottom=0, top=100)
        else:
            self.graphFigure.axes[0].set_ylim(bottom=0, top=(highestAverage+highestAverage*0.1))
        self.graphFigure.axes[0].get_yaxis().grid(True, linestyle="-", color="grey", alpha=0.2)
        self.canvas.draw()
        
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
