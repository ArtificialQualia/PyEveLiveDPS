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
        self.dataQueue = None
        self.dataRecieveQueue = None
        self.fleetMetadataQueue = None
        self.errorQueue = None
        self.fleetData = {}
        self.fleetMode = False
        
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
            self.interval = settings.getInterval()
            
            # pops old values, adds new values, and passes those to the graph and other handlers
            for category, items in self.categories.items():
                if self.fleetMode and category != 'mining':
                    for entry in items["newEntry"]:
                        self.dataQueue.put({"category": category, "entry": entry})
                # if items["settings"] is empty, this isn't a category that is being tracked
                if items["settings"]:
                    # remove old values
                    items["historical"].pop(0)
                    items["historicalDetails"].pop(0)
                    # as values are broken up by weapon, add them together for the non-details views
                    amountSum = sum([entry['amount'] for entry in items["newEntry"]])
                    items["historical"].append(amountSum)
                    items["historicalDetails"].append(items["newEntry"])
                    # 'yValues' is for the actual DPS at that point in time, as opposed to raw values
                    items["yValues"] = items["yValues"][1:]
                    average = (np.sum(items["historical"])*(1000/self.interval))/self.arrayLength
                    items["yValues"] = np.append(items["yValues"], average)
                    # pass the values to the graph and other handlers
                    if not items["labelOnly"] and not self.graphDisabled:
                        self.graph.animateLine(items["yValues"], items["settings"], items["lines"], zorder=items["zorder"])
                    color = self.findColor(category, average)
                    self.labelHandler.updateLabel(category, average, color)
                    self.detailsHandler.updateDetails(category, items["historicalDetails"])
            
            # Find highest average for the y-axis scaling
            # We need to track graph avg and label avg separately, since graph avg is used for y-axis scaling
            #  and label average is needed for detecting when to slow down the animation
            self.highestAverage = 0
            self.highestLabelAverage = 0
            for category, items in self.categories.items():
                if items["settings"] and not items["labelOnly"]:
                    highest = max(items["yValues"])
                    if highest > self.highestAverage:
                        self.highestAverage = highest
                elif items["settings"]:
                    highest = max(items["yValues"])
                    if highest > self.highestLabelAverage:
                        self.highestLabelAverage = highest
            
            if not self.graphDisabled:
                self.graph.readjust(self.highestAverage)
            
            # if there are no values coming in to the graph, enable 'slowDown' mode to save CPU
            if self.highestAverage == 0 and self.highestLabelAverage == 0 and not self.fleetMode:
                if not self.slowDown:
                    self.slowDown = True
                    self.interval = 500
            else:
                if self.slowDown:
                    self.slowDown = False
                    self.interval = settings.getInterval()
            
            # display of pilot details is handled after all values are updated, for sorting and such
            self.detailsHandler.cleanupAndDisplay(self.interval, self.arrayLength, lambda x,y: self.findColor(x,y))

            if self.fleetMode:
                self.updateFleetWindow(self.mainWindow.fleetWindow)
            
        except Exception as e:
            logging.exception(e)
    
    def updateFleetWindow(self, fleetWindow):
        fleetWindow.processErrorQueue(self.errorQueue)
        fleetWindow.processMetadataQueue(self.fleetMetadataQueue)
        if not settings.fleetWindowShow:
            while not self.dataRecieveQueue.empty():
                fleetEntry = self.dataRecieveQueue.get(False)
            return
        fleetWindow.processRecieveQueue(self.dataRecieveQueue, self.fleetData, self.arrayLength)
        for category, pilots in self.fleetData.items():
            toDelete = []
            for pilot, entries in pilots.items():
                average = (np.sum(entries["historical"])*(1000/self.interval))/self.arrayLength
                if category != 'aggregate' and max(entries["yValues"]) == 0 and average == 0 and pilot != fleetWindow.characterName:
                    toDelete.append(pilot)
                entries["yValues"] = entries["yValues"][1:]
                entries["yValues"] = np.append(entries["yValues"], average)
            for pilot in toDelete:
                del pilots[pilot]
        fleetWindow.displayFleetData(self.fleetData)
        fleetWindow.displayAggregate(self.fleetData['aggregate'])
        
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
        self.mainWindow.makeAllChildrenDraggable(self.labelHandler)
        
        if settings.detailsWindowShow:
            self.mainWindow.detailsWindow.deiconify()
        else:
            self.mainWindow.detailsWindow.withdraw()
        
        if self.fleetMode and settings.fleetWindowShow:
            self.mainWindow.fleetWindow.deiconify()
        else:
            self.mainWindow.fleetWindow.withdraw()
        
        self.arrayLength = int((self.seconds*1000)/self.interval)
        historicalTemplate = [0] * self.arrayLength
        yValuesTemplate = np.array([0] * self.arrayLength)
        ySmooth = self.graph.smoothListGaussian(yValuesTemplate, 5)
        # resets all the arrays to contain no values
        for category, items in self.categories.items():
            if items["settings"]:
                self.labelHandler.enableLabel(category, True)
                showPeak = items["settings"][0].get("showPeak", False)
                self.labelHandler.enablePeak(category, showPeak)
                self.detailsHandler.enableLabel(category, True)
                items["historical"] = historicalTemplate.copy()
                items["historicalDetails"] = [[]] * self.arrayLength
                items["yValues"] = yValuesTemplate.copy()
                items["labelOnly"] = items["settings"][0].get("labelOnly", False)
                if not items["labelOnly"]:
                    plotLine, = self.graph.subplot.plot(ySmooth, zorder=items["zorder"])
                    items["lines"] = [plotLine]
            else:
                self.labelHandler.enableLabel(category, False)
                self.labelHandler.enablePeak(category, False)
                self.detailsHandler.enableLabel(category, False)
        
        if not self.graphDisabled:
            self.graph.subplot.margins(0,0)
            self.graph.graphFigure.axes[0].set_ylim(bottom=0, top=100)
            self.graph.graphFigure.canvas.draw()
        
        # reset fleet data
        characterName = self.mainWindow.fleetWindow.characterName
        if self.dataQueue:
            self.fleetData = {
                'aggregate': {
                    'dpsOut': {
                        'historical': historicalTemplate.copy(),
                        'yValues': yValuesTemplate.copy()
                    },
                    'dpsIn': {
                        'historical': historicalTemplate.copy(),
                        'yValues': yValuesTemplate.copy()
                    },
                    'logiOut': {
                        'historical': historicalTemplate.copy(),
                        'yValues': yValuesTemplate.copy()
                    }
                },
                'dpsOut': {
                    characterName: {
                        'historical': historicalTemplate.copy(),
                        'yValues': yValuesTemplate.copy()
                    }
                },
                'dpsIn': {
                    characterName: {
                        'historical': historicalTemplate.copy(),
                        'yValues': yValuesTemplate.copy()
                    }
                },
                'logiOut': {
                    characterName: {
                        'historical': historicalTemplate.copy(),
                        'yValues': yValuesTemplate.copy()
                    }
                }
            }
        self.mainWindow.fleetWindow.resetGraphs(ySmooth)
        self.mainWindow.fleetWindow.changeSettings()
        
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