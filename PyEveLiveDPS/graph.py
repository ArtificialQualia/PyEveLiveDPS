import matplotlib
from matplotlib.animation import FuncAnimation
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure, Axes

import numpy as np
import tkinter as tk
import logreader

class DPSGraph(tk.Frame):

    def __init__(self, dpsOutLabel, dpsInLabel, characterDetector, **kwargs):
        tk.Frame.__init__(self, **kwargs)
        self.dpsOutLabel = dpsOutLabel
        self.dpsInLabel = dpsInLabel
        
        self.degree = 5
        self.historicalDamageOut = [0] * 100
        self.historicalDamageIn = [0] * 100
        self.yValuesOut = np.array([0] * 100)
        self.yValuesIn = np.array([0] * 100)
        
        self.characterDetector = characterDetector
        
        self.graphFigure = Figure(figsize=(4,2), dpi=100, facecolor="black")
        
        self.subplot = self.graphFigure.add_subplot(1,1,1, facecolor=(0.3, 0.3, 0.3))
        self.subplot.tick_params(axis="y", colors="grey", direction="in")
        self.subplot.tick_params(axis="x", colors="grey", labelbottom="off", bottom="off")
        
        initSize = 90-(self.degree*2-1)
        self.plotLineIn, = self.subplot.plot(range(5, initSize+5),[0] * initSize, 'r')
        self.plotLineOut, = self.subplot.plot(range(5, initSize+5),[0] * initSize, 'c')
        
        self.graphFigure.axes[0].get_xaxis().set_ticklabels([])
        self.graphFigure.subplots_adjust(left=(40/410), bottom=(15/410), right=1, top=(1-15/410), wspace=0, hspace=0)

        self.canvas = FigureCanvasTkAgg(self.graphFigure, self)
        self.canvas.get_tk_widget().configure(bg="black")
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.ani = FuncAnimation(self.graphFigure, self.animate, interval=100, blit=False, init_func=self.init_animation)
        
        self.canvas.show()
        
    def changeSettings(self, seconds, interval):
        self.ani.event_source.stop()
        self.subplot.clear()
        
        self.historicalDamageOut = [0] * int((seconds*1000)/interval)
        self.historicalDamageIn = [0] * int((seconds*1000)/interval)
        self.yValuesOut = np.array([0] * int((seconds*1000)/interval))
        self.yValuesIn = np.array([0] * int((seconds*1000)/interval))
        
        initSize = (((seconds*1000)/interval)*0.91)-(self.degree*2-1)
        rangeModifier = int(((seconds*1000)/interval)*0.05)
        self.plotLineIn, = self.subplot.plot(range(rangeModifier, int(initSize)+rangeModifier),[0] * int(initSize), 'r')
        self.plotLineOut, = self.subplot.plot(range(rangeModifier, int(initSize)+rangeModifier),[0] * int(initSize), 'c')
        
        self.ani.event_source.interval = interval
        
        self.ani.event_source.start()
        
    def readjust(self, **kwargs):
        self.graphFigure.subplots_adjust(**kwargs)
        self.canvas.draw()
        
    def init_animation(self):
        return self.animate(0)
    
    def animate(self, i):
        damageOut, damageIn = self.characterDetector.readLog()
        
        self.historicalDamageOut.pop(0)
        self.historicalDamageOut.insert(len(self.historicalDamageOut), damageOut)
        
        self.yValuesOut = self.yValuesOut[1:]
        damageOutAverage = (np.sum(self.historicalDamageOut)*10)/len(self.historicalDamageOut)
        self.yValuesOut = np.append(self.yValuesOut, damageOutAverage)
        self.dpsOutLabel.configure(text="DPS Out: " + str(damageOutAverage))
        
        self.historicalDamageIn.pop(0)
        self.historicalDamageIn.insert(len(self.historicalDamageIn), damageIn)
        
        self.yValuesIn = self.yValuesIn[1:]
        damageInAverage = (np.sum(self.historicalDamageIn)*10)/len(self.historicalDamageIn)
        self.yValuesIn = np.append(self.yValuesIn, damageInAverage)
        self.dpsInLabel.configure(text="DPS In: " + str(damageInAverage))
        
        highestAverage = 0
        for i in range(len(self.yValuesOut)):
            if (self.yValuesOut[i] > highestAverage):
                highestAverage = self.yValuesOut[i]
            if (self.yValuesIn[i] > highestAverage):
                highestAverage = self.yValuesIn[i]
        
        self.ySmoothIn = self.smoothListGaussian(self.yValuesIn, self.degree)
        self.ySmoothOut = self.smoothListGaussian(self.yValuesOut, self.degree)
        
        self.plotLineOut.set_data(range(1, len(self.ySmoothOut)+1), self.ySmoothOut)
        self.plotLineIn.set_data(range(1, len(self.ySmoothIn)+1), self.ySmoothIn)
        
        if (highestAverage < 100):
            self.graphFigure.axes[0].set_ylim(bottom=0, top=100)
        else:
            self.graphFigure.axes[0].set_ylim(bottom=0, top=(highestAverage+highestAverage*0.1))
        self.graphFigure.axes[0].get_yaxis().grid(True, linestyle="-", color="grey", alpha=0.2)
        
        return self.plotLineOut, self.plotLineIn
        
    def smoothListGaussian(self, list, degree=5):  
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
