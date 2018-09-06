"""
This class handles all the animation for peld
it is the main loop of PELD, and runs in a separate thread
"""
import threading
import time
import numpy as np
import matplotlib
import simulator
import simulationWindow
from peld import settings
import logging


class Animator(threading.Thread):
    # zorder may be added as a settings in the future
    categories = {
        "dpsIn": { "zorder": 90 },
        "dpsOut": { "zorder": 100 },
        "logiOut": { "zorder": 80 }, 
        "logiIn": { "zorder": 70 },
        "capTransfered": { "zorder": 60 },
        "capRecieved": { "zorder": 50 },
        "capDamageOut": { "zorder": 40 }, 
        "capDamageIn": { "zorder": 30 },
        "mining": { "zorder": 20 }
        }
    def __init__(self, mainWindow, **kwargs):
        threading.Thread.__init__(self, name="animator")
        self.mainWindow = mainWindow
        self.graph = mainWindow.graphFrame
        self.labelHandler = mainWindow.labelHandler
        self.characterDetector = mainWindow.characterDetector
        self.detailsHandler = mainWindow.detailsWindow.detailsHandler
        self.queue = None
        
        self.slowDown = False
        self.simulationEnabled = False
        self.daemon = True
        
        self.changeSettings()
        self.start()
    
    def run(self):
        logging.info('Starting animator thread')
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
            self.simulator = simulator.Simulator(values, settings.getInterval())
        if not enable:
            self.simulator = None
            self.simulationEnabled = False
            
    def animate(self):
        """ this function gets called every 'interval', and handles all the tracking data """
        try:
            # data points are retrieved from either the simulator or the EVE logs
            if self.simulationEnabled:
                newEntries = self.simulator.simulate()
            else:
                newEntries = self.characterDetector.readLog()
            
            # insert all the new values into the categories entries
            self.categories["dpsOut"]["newEntry"] = newEntries[0]
            self.categories["dpsIn"]["newEntry"] = newEntries[1]
            self.categories["logiOut"]["newEntry"] = newEntries[2]
            self.categories["logiIn"]["newEntry"] = newEntries[3]
            self.categories["capTransfered"]["newEntry"] = newEntries[4]
            self.categories["capRecieved"]["newEntry"] = newEntries[5]
            self.categories["capDamageOut"]["newEntry"] = newEntries[6]
            self.categories["capDamageIn"]["newEntry"] = newEntries[7]
            self.categories["mining"]["newEntry"] = newEntries[8]
            interval = settings.getInterval()
            
            # pops old values, adds new values, and passes those to the graph and other handlers
            for category, items in self.categories.items():
                if self.queue and category != 'mining':
                    for entry in items["newEntry"]:
                        self.queue.put({"category": category, "entry": entry})
                # if items["settings"] is empty, this isn't a category that is being tracked
                if items["settings"]:
                    # remove old values
                    items["historical"].pop(0)
                    items["historicalDetails"].pop(0)
                    # as values are broken up by weapon, add them together for the non-details views
                    amountSum = sum([entry['amount'] for entry in items["newEntry"]])
                    items["historical"].insert(len(items["historical"]), amountSum)
                    items["historicalDetails"].insert(len(items["historicalDetails"]), items["newEntry"])
                    # 'yValues' is for the actual DPS at that point in time, as opposed to raw values
                    items["yValues"] = items["yValues"][1:]
                    average = (np.sum(items["historical"])*(1000/interval))/len(items["historical"])
                    items["yValues"] = np.append(items["yValues"], average)
                    # pass the values to the graph and other handlers
                    if not items["labelOnly"] and not self.graphDisabled:
                        self.graph.animateLine(items["yValues"], items["settings"], items["lines"], zorder=items["zorder"])
                        self.labelHandler.updateLabel(category, average, matplotlib.colors.to_hex(items["lines"][-1].get_color()))
                    else:
                        color = self.findColor(category, average)
                        self.labelHandler.updateLabel(category, average, color)
                    self.detailsHandler.updateDetails(category, items["historicalDetails"])
            
            # Find highest average for the y-axis scaling
            # We need to track graph avg and label avg separately, since graph avg is used for y-axis scaling
            #  and label average is needed for detecting when to slow down the animation
            self.highestAverage = 0
            self.highestLabelAverage = 0
            for i in range(len(items.get('yValues', 0))):
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
                self.graph.readjust(settings.getWindowWidth(), self.highestAverage)
            
            # if there are no values coming in to the graph, enable 'slowDown' mode to save CPU
            if (self.highestAverage == 0 and self.highestLabelAverage == 0):
                if not self.slowDown:
                    self.slowDown = True
                    self.interval = 500
            else:
                if self.slowDown:
                    self.slowDown = False
                    self.interval = settings.getInterval()
            
            # display of pilot details is handled after all values are updated, for sorting and such
            self.detailsHandler.cleanupAndDisplay(interval, int((self.seconds*1000)/self.interval), lambda x,y: self.findColor(x,y))
    
            if not self.graphDisabled:
                self.graph.graphFigure.canvas.draw()
            
        except Exception as e:
            logging.exception(e)
        
    def changeSettings(self):
        """This function is called when a user changes settings after the settings are verified"""
        if self.is_alive():
            self.paused = True
            self.mainWindow.after_cancel(self.animate)
            self.graph.subplot.clear()
        if self.simulationEnabled:
            self.simulationSettings(enable=False)
            self.mainWindow.mainMenu.menu.delete(5)
            self.mainWindow.mainMenu.menu.insert_command(5, label="Simulate Input", command=lambda: simulationWindow.SimulationWindow(self.mainWindow))
            self.mainWindow.topLabel.grid_remove()
            self.mainWindow.mainMenu.menu.entryconfig(3, state="normal")
        
        self.slowDown = False
        self.seconds = settings.getSeconds()
        self.interval = settings.getInterval()
        self.categories["dpsOut"]["settings"] = settings.getDpsOutSettings()
        self.categories["dpsIn"]["settings"] = settings.getDpsInSettings()
        self.categories["logiOut"]["settings"] = settings.getLogiOutSettings()
        self.categories["logiIn"]["settings"] = settings.getLogiInSettings()
        self.categories["capTransfered"]["settings"] = settings.getCapTransferedSettings()
        self.categories["capRecieved"]["settings"] = settings.getCapRecievedSettings()
        self.categories["capDamageOut"]["settings"] = settings.getCapDamageOutSettings()
        self.categories["capDamageIn"]["settings"] = settings.getCapDamageInSettings()
        self.categories["mining"]["settings"] = settings.getMiningSettings()
        self.graphDisabled = settings.getGraphDisabled()
        
        if self.graphDisabled:
            self.graph.grid_remove()
        else:
            self.graph.grid()
        
        self.labelHandler.redoLabels()
        
        if settings.detailsWindowShow:
            self.mainWindow.detailsWindow.deiconify()
        else:
            self.mainWindow.detailsWindow.withdraw()
        
        # resets all the arrays to contain no values
        for category, items in self.categories.items():
            if items["settings"]:
                self.labelHandler.enableLabel(category, True)
                self.detailsHandler.enableLabel(category, True)
                items["historical"] = [0] * int((self.seconds*1000)/self.interval)
                items["historicalDetails"] = [[]] * int((self.seconds*1000)/self.interval)
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
                self.detailsHandler.enableLabel(category, False)
        
        if not self.graphDisabled:
            self.graph.subplot.margins(0,0)
            self.graph.graphFigure.axes[0].set_ylim(bottom=0, top=100)
            self.graph.graphFigure.canvas.draw()
        
        self.paused = False
        
    def findColor(self, category, value):
        """
        Helper function to find the right line/label color for a given value.
        Returns the color to use
        """
        categorySettings = self.categories[category]["settings"]
        for index, item in enumerate(categorySettings):
            if index == (len(categorySettings)-1):
                if value >= item["transitionValue"]:
                    return item["color"]
            elif value >= item["transitionValue"] and value < categorySettings[index+1]["transitionValue"]:
                return item["color"]