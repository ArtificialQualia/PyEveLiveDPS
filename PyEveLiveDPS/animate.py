"""
This class handles all the animation for peld
"""
import threading
import time
import numpy as np
import matplotlib
import simulator
import simulationWindow

class Animator(threading.Thread):
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
    def __init__(self, mainWindow, **kwargs):
        threading.Thread.__init__(self, name="animator")
        self.mainWindow = mainWindow
        self.graph = mainWindow.graphFrame
        self.labelHandler = mainWindow.labelHandler
        self.settings = mainWindow.settings
        self.characterDetector = mainWindow.characterDetector
        
        self.slowDown = False
        self.simulationEnabled = False
        self.daemon = True
        
        self.changeSettings()
        self.start()
    
    def run(self):
        self.run = True
        self.paused = False
        self.time = time.time()
        while self.run:
            if not self.paused:
                self.mainWindow.after(self.interval, self.animate)
            sleepTime = (self.interval - 1)/1000 - (time.time() - self.time)
            if (sleepTime > 0):
                time.sleep(sleepTime)
            #else: print("Warning, sleep time negative")
            self.time = time.time()
            
    def stop(self):
        self.run = False
        self.mainWindow.after_cancel(self.animate)
        
    def catchup(self):
        """This is just to 'clear' the graph"""
        self.changeSettings()
        
    def simulationSettings(self, enable=False, values=None):
        if enable:
            self.simulationEnabled = True
            self.simulator = simulator.Simulator(values, self.settings.getInterval())
        if not enable:
            self.simulator = None
            self.simulationEnabled = False
            
    def animate(self):
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
        interval = self.settings.getInterval()
        
        for category, items in self.categories.items():
            if items["settings"]:
                items["historical"].pop(0)
                items["historical"].insert(len(items["historical"]), items["newEntry"])
                items["yValues"] = items["yValues"][1:]
                average = (np.sum(items["historical"])*(1000/interval))/len(items["historical"])
                items["yValues"] = np.append(items["yValues"], average)
                if not items["labelOnly"] and not self.graphDisabled:
                    self.graph.animateLine(items["yValues"], items["settings"], items["lines"], zorder=items["zorder"])
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
        #We need to track graph avg and label avg separately, since graph avg is used for y-axis scaling
        # and label average is needed for detecting when to slow down the animation
        self.highestAverage = 0
        self.highestLabelAverage = 0
        for i in range(int((self.seconds*1000)/interval)):
            for category, items in self.categories.items():
                if items["settings"] and not items["labelOnly"]:
                    if (items["yValues"][i] > self.highestAverage):
                        self.highestAverage = items["yValues"][i]
                elif items["settings"]:
                    if (items["yValues"][i] > self.highestAverage):
                        self.highestLabelAverage = items["yValues"][i]
        
        if not self.graphDisabled:
            if (self.highestAverage < 100):
                self.graph.graphFigure.axes[0].set_ylim(bottom=0, top=100)
            else:
                self.graph.graphFigure.axes[0].set_ylim(bottom=0, top=(self.highestAverage+self.highestAverage*0.1))
            self.graph.graphFigure.axes[0].get_yaxis().grid(True, linestyle="-", color="grey", alpha=0.2)
            self.graph.readjust(self.settings.getWindowWidth(), self.highestAverage)
        
        if (self.highestAverage == 0 and self.highestLabelAverage == 0):
            if not self.slowDown:
                self.slowDown = True
                self.interval = 500
        else:
            if self.slowDown:
                self.slowDown = False
                self.interval = self.settings.getInterval()

        if not self.graphDisabled:
            self.graph.graphFigure.canvas.draw()
        
    def changeSettings(self):
        """This function is called when a user changes settings after the settings are verified"""
        if self.is_alive():
            self.paused = True
            self.mainWindow.after_cancel(self.animate)
            self.graph.subplot.clear()
        if self.simulationEnabled:
            self.simulationSettings(enable=False)
            self.mainWindow.mainMenu.menu.delete(3)
            self.mainWindow.mainMenu.menu.insert_command(3, label="Simulate Input", command=lambda: simulationWindow.SimulationWindow(self.mainWindow))
            self.mainWindow.topLabel.grid_remove()
        
        self.slowDown = False
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
        self.graphDisabled = self.settings.getGraphDisabled()
        
        if self.graphDisabled:
            self.graph.grid_remove()
        else:
            self.graph.grid()
        
        self.labelHandler.redoLabels()
        
        for category, items in self.categories.items():
            if items["settings"]:
                self.labelHandler.enableLabel(category, True)
                items["historical"] = [0] * int((self.seconds*1000)/self.interval)
                items["yValues"] = np.array([0] * int((self.seconds*1000)/self.interval))
                try:
                    items["labelOnly"] = items["settings"][0]["labelOnly"]
                except KeyError:
                    items["settings"][0]["labelOnly"] = False
                    items["labelOnly"] = items["settings"][0]["labelOnly"]
                if not items["labelOnly"]:
                    ySmooth = self.graph.smoothListGaussian(items["yValues"], 5)
                    plotLine, = self.graph.subplot.plot(ySmooth, zorder=items["zorder"])
                    items["lines"] = [plotLine]
            else:
                self.labelHandler.enableLabel(category, False)
        
        if not self.graphDisabled:
            self.graph.subplot.margins(0,0)
            self.graph.graphFigure.axes[0].set_ylim(bottom=0, top=100)
            self.graph.graphFigure.canvas.draw()
        
        self.paused = False
        