"""
FleetWindow:

Some of the styling for this window comes from BaseWindow

Contains graphs of fleet statistics
"""

import tkinter as tk
import numpy as np
from baseWindow import BaseWindow
from peld import settings
from graph import DPSGraph
from labelHandler import LabelHandler

class FleetWindow(tk.Toplevel):
    graphs = {
        'combined': {
            'frameGrid': {
                'column': 10,
                'row': 10
            },
            'labelText': 'Aggregate Stats',
            'handlerSettings': {
                'labels': {'fleetConnected': { 'text': 'Connected PELDs:' }},
                'labelSettings': {'fleetConnected': {'row': 0, 'column': 0, 'inThousands': 0, 'decimalPlaces': 0}}
            },
            'lines': {}
        },
        'dpsOut': {
            'frameGrid': {
                'column': 12,
                'row': 10
            },
            'labelText': 'Top 3 DPS Out',
            'handlerSettings': {
                'labels': {
                    'total': { 'text': 'Fleet DPS:' },
                    'top': { 'text': 'Top Pilot DPS:' }
                },
                'labelSettings': {
                    'total': {'row': 0, 'column': 0, 'inThousands': 0, 'decimalPlaces': 0},
                    'top': {'row': 0, 'column': 1, 'inThousands': 0, 'decimalPlaces': 0}
                }
            },
            'lines': [],
            'color': '#00FFFF'
        },
        'dpsIn': {
            'frameGrid': {
                'column': 10,
                'row': 13
            },
            'labelText': 'Top 3 DPS In',
            'handlerSettings': {
                'labels': {
                    'total': { 'text': 'Incoming DPS:' },
                    'top': { 'text': 'Top Incoming DPS:' }
                },
                'labelSettings': {
                    'total': {'row': 0, 'column': 0, 'inThousands': 0, 'decimalPlaces': 0},
                    'top': {'row': 0, 'column': 1, 'inThousands': 0, 'decimalPlaces': 0}
                }
            },
            'lines': [],
            'color': '#FF0000'
        },
        'logiOut': {
            'frameGrid': {
                'column': 12,
                'row': 13
            },
            'labelText': 'Top 3 Logi',
            'handlerSettings': {
                'labels': {
                    'total': { 'text': 'Fleet Logi:' },
                    'top': { 'text': 'Top Pilot Logi:' }
                },
                'labelSettings': {
                    'total': {'row': 0, 'column': 0, 'inThousands': 0, 'decimalPlaces': 0},
                    'top': {'row': 0, 'column': 1, 'inThousands': 0, 'decimalPlaces': 0}
                }
            },
            'lines': [],
            'color': '#00FF00'
        },
    }
    
    def __init__(self, mainWindow):
        tk.Toplevel.__init__(self)
        self.baseWindow = BaseWindow(self)
        self.mainWindow = mainWindow
        self.characterName = ''
        self.minsize(200,150)

        self.mainFrame = tk.Frame(self, background="black")
        self.mainFrame.grid(row="10", column="10", sticky="news")
        
        self.mainFrame.columnconfigure(10, weight=1)
        self.mainFrame.columnconfigure(12, weight=1)
        self.mainFrame.rowconfigure(10, weight=1)
        self.mainFrame.rowconfigure(13, weight=1)

        # window is hidden until fleet mode is started
        self.withdraw()
        
        # set the window size and position from the settings
        self.geometry("%sx%s+%s+%s" % (settings.fleetWindowWidth, settings.fleetWindowHeight, 
                                       settings.fleetWindowX, settings.fleetWindowY))
        self.update()
        
        # label that appears at the top of the window
        self.topLabel = tk.Label(self.mainFrame, text="Fleet Stats", fg="white", background="black")
        self.topLabel.grid(row="7", column="10", columnspan="4")

        # dividers for window
        tk.Frame(self.mainFrame, highlightthickness="1", highlightbackground="dim gray", background="black").grid(row="8", column="10", sticky="we", columnspan="3")
        self.horizontalDivider = tk.Frame(self.mainFrame, highlightthickness="1", highlightbackground="dim gray", background="black")
        self.horizontalDivider.grid(row="11", column="10", sticky="we", columnspan="3")
        self.verticalDivider = tk.Frame(self.mainFrame, highlightthickness="1", highlightbackground="dim gray", background="black")
        self.verticalDivider.grid(row="8", column="11", sticky="ns", rowspan="6")
        
        # create all graphs and content
        for key, entry in self.graphs.items():
            frame = tk.Frame(self.mainFrame, background="black")
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)
            frame.grid(entry['frameGrid'], sticky="news")
            if entry['frameGrid']['column'] == 10:
                # add spacer on right side of graph
                tk.Frame(frame, background="black", width="5").grid(row="0", column="90", sticky="ns", rowspan="100")
            entry['frame'] = frame

            label = tk.Label(frame, text=entry['labelText'], fg="white", background="black")
            label.grid(row="0", column="0")
            entry['label'] = label

            graph = DPSGraph(frame, background="black")
            graph.grid(row="1", column="0", sticky="nesw")
            entry['graph'] = graph

            labelHandler = LabelHandler(frame, labels=entry['handlerSettings']['labels'],
                                        labelSettings=entry['handlerSettings']['labelSettings'], background="black")
            for labelKey in entry['handlerSettings']['labels']:
                labelHandler.enableLabel(labelKey)
            labelHandler.grid(row="2", column="0", sticky="news")
            entry['labelHandler'] = labelHandler
        self.changeSettings()
        
        # special label handling for PELDs connected
        self.getConnectedLabel()['text'] = "? of ?"

        # spacer for compact mode
        self.rightSpacerFrame = tk.Frame(self.mainFrame, width=5, height=5, background="black")
        self.rightSpacerFrame.grid(row="9", column="100", rowspan="50")
        self.rightSpacerFrame.grid_remove()

        self.leftSpacerFrame = tk.Frame(self.mainFrame, width=5, height=5, background="black")
        self.leftSpacerFrame.grid(row="9", column="0", rowspan="50")
        self.leftSpacerFrame.grid_remove()

        # the window must be temporarily shown so that linux can draw the window properly
        self.wm_attributes("-alpha", 0.0)
        self.deiconify()
        self.stopMove()
        self.withdraw()
        self.wm_attributes("-alpha", 1.0)

        self.makeDraggable(self.mainFrame)
        self.makeAllChildrenDraggable(self.mainFrame)


    def __getattr__(self, attr):
        return getattr(self.baseWindow, attr)
    
    def saveWindowGeometry(self):
        settings.fleetWindowX = self.winfo_x()
        settings.fleetWindowY = self.winfo_y()
        settings.fleetWindowWidth = self.winfo_width()
        settings.fleetWindowHeight = self.winfo_height()
        
    def collapseHandler(self, collapsed):
        """ this is called when the main window receives a collapseEvent """
        if collapsed:
            self.wm_attributes("-alpha", 1.0)
            self.rightSpacerFrame.grid_remove()
            self.leftSpacerFrame.grid_remove()
            self.showResizeFrames()
            self.makeDraggable(self.mainFrame)
            self.makeAllChildrenDraggable(self.mainFrame)
        else:
            self.wm_attributes("-alpha", settings.getCompactTransparency()/100)
            self.hideResizeFrames()
            self.rightSpacerFrame.grid()
            self.leftSpacerFrame.grid()
            self.unmakeDraggable(self.mainFrame)
            self.unmakeAllChildrenDraggable(self.mainFrame)
                                   
    def stopMove(self):
        self.update_idletasks()
        for key, entry in self.graphs.items():
            entry['graph'].readjust(0)

    def calculateColor(self, color, rank):
        if rank == 0:
            return color
        else:
            return color + str(100-(10*rank))

    def changeSettings(self):
        self.mainFrame.columnconfigure(10, weight=1)
        self.mainFrame.columnconfigure(12, weight=1)
        self.mainFrame.rowconfigure(10, weight=1)
        self.mainFrame.rowconfigure(13, weight=1)
        self.horizontalDivider.grid()
        self.verticalDivider.grid()
        self.graphs['combined']['show'] = settings.fleetWindowShowAggregate
        self.graphs['dpsOut']['show'] = settings.fleetWindowShowDpsOut
        self.graphs['dpsIn']['show'] = settings.fleetWindowShowDpsIn
        self.graphs['logiOut']['show'] = settings.fleetWindowShowLogiOut
        for key, entry in self.graphs.items():
            entry['frame'].grid(entry['frameGrid'], sticky="news")
            if not entry['show']:
                entry['frame'].grid_remove()
        if not self.graphs['combined']['show'] and not self.graphs['dpsOut']['show']:
            self.mainFrame.rowconfigure(10, weight=0)
            self.horizontalDivider.grid_remove()
        if not self.graphs['combined']['show'] and not self.graphs['dpsIn']['show']:
            self.mainFrame.columnconfigure(10, weight=0)
            self.verticalDivider.grid_remove()
        if not self.graphs['dpsOut']['show'] and not self.graphs['logiOut']['show']:
            self.mainFrame.columnconfigure(12, weight=0)
            self.verticalDivider.grid_remove()
        if not self.graphs['dpsIn']['show'] and not self.graphs['logiOut']['show']:
            self.mainFrame.rowconfigure(13, weight=0)
            self.horizontalDivider.grid_remove()
        if (self.graphs['combined']['show'] and self.graphs['logiOut']['show'] and
             not self.graphs['dpsOut']['show'] and not self.graphs['dpsIn']['show']):
            self.graphs['logiOut']['frame'].grid(column=10, row=13, sticky="news")
            self.mainFrame.columnconfigure(12, weight=0)
            self.verticalDivider.grid_remove()
        if (self.graphs['dpsOut']['show'] and self.graphs['dpsIn']['show'] and
             not self.graphs['combined']['show'] and not self.graphs['logiOut']['show']):
            self.graphs['dpsOut']['frame'].grid(column=10, row=10, sticky="news")
            self.mainFrame.columnconfigure(12, weight=0)
            self.verticalDivider.grid_remove()
        if (not self.graphs['dpsOut']['show'] and not self.graphs['dpsIn']['show'] and
             not self.graphs['combined']['show'] and not self.graphs['logiOut']['show']):
            self.mainFrame.columnconfigure(12, weight=1)

    def resetGraphs(self, ySmooth):
        combined = self.graphs['combined']
        combined['graph'].subplot.clear()
        combined['lines']['dpsOut'], = combined['graph'].subplot.plot(ySmooth, zorder=10)
        combined['lines']['dpsIn'], = combined['graph'].subplot.plot(ySmooth, zorder=9)
        combined['lines']['logiOut'], = combined['graph'].subplot.plot(ySmooth, zorder=8)
        combined['graph'].subplot.margins(0,0)
        for category in ['dpsOut', 'dpsIn', 'logiOut']:
            entry = self.graphs[category]
            entry['graph'].subplot.clear()
            entry['lines'] = []
            for rank in range(3):
                color = self.calculateColor(entry['color'], rank)
                line, = entry['graph'].subplot.plot(ySmooth, color=color, zorder=10-rank)
                entry['lines'].append(line)
            line, = entry['graph'].subplot.plot(ySmooth, linestyle=':', color=entry['color'], zorder=5)
            entry['lines'].append(line)
            entry['graph'].subplot.margins(0,0)

    def getConnectedLabel(self):
        return self.graphs['combined']['labelHandler'].labels['fleetConnected']['label'].numberLabel
    
    def processErrorQueue(self, errorQueue):
        while not errorQueue.empty():
            error = errorQueue.get(False)
            if error == 'Character is not in a fleet':
                self.topLabel['text'] = "Fleet Stats (You are not in a fleet)"
    
    def processMetadataQueue(self, metadataQueue):
        while not metadataQueue.empty():
            fleetMetadata = metadataQueue.get(False)
            if fleetMetadata['client_access']:
                self.topLabel['text'] = "Fleet Stats"
            else:
                self.topLabel['text'] = "Fleet Stats (Your FC has removed access to this tool)"
            connectedLabel = self.getConnectedLabel()
            peldText = str(fleetMetadata['connected']) +  " of "
            if fleetMetadata['fc_connected']:
                peldText += str(fleetMetadata['total'])
            else:
                peldText += "?"
            connectedLabel['text'] = peldText
    
    def processRecieveQueue(self, recieveQueue, fleetData, arrayLength):
        for category, pilots in fleetData.items():
            for pilot, entries in pilots.items():
                entries["historical"].pop(0)
                entries["historical"].append(0)
        while not recieveQueue.empty():
            fleetEntry = recieveQueue.get(False)
            entryType = fleetEntry['category']
            amount = fleetEntry['entry']['amount']
            pilot = fleetEntry['entry']['owner']
            #enemy = fleetEntry['entry']['pilotName']
            fleetData['aggregate'][entryType]['historical'][-1] += amount
            if pilot not in fleetData[entryType]:
                fleetData[entryType][pilot] = {}
                fleetData[entryType][pilot]['historical'] = [0] * arrayLength
                fleetData[entryType][pilot]['yValues'] = np.array([0] * arrayLength)
                fleetData[entryType][pilot]['line'] = []
            fleetData[entryType][pilot]['historical'][-1] += amount
    
    def displayFleetData(self, fleetData):
        for category in ['dpsOut', 'dpsIn', 'logiOut']:
            if not self.graphs[category]['show']:
                continue
            graph = self.graphs[category]['graph']
            lines = self.graphs[category]['lines']
            categoryColor = self.graphs[category]['color']
            tops = sorted(fleetData[category], key=lambda pilot: -fleetData[category][pilot]['yValues'][-1])
            tops = tops[0:3]
            youTopThree = False
            highestAverage = 0
            for rank in range(len(tops)):
                pilot = tops[rank]
                yValues = fleetData[category][pilot]['yValues']
                line = lines[rank]
                color = self.calculateColor(categoryColor, rank)

                if pilot == self.characterName:
                    # remove special 'you' line
                    youTopThree = True
                    graph.basicLine(yValues, categoryColor, lines[3], '')
                graph.basicLine(yValues, color, line)
                
                highest = max(yValues)
                if highest > highestAverage:
                    highestAverage = highest
            if not youTopThree:
                yValues = fleetData[category][self.characterName]['yValues']
                graph.basicLine(yValues, categoryColor+'70', lines[3], ':')
                tops.append(self.characterName)
            graph.subplot.legend(lines, tops, loc='upper left', fontsize='x-small', framealpha=0.5).set_zorder(100)
            graph.readjust(highestAverage)
            topValue = fleetData[category][tops[0]]['yValues'][-1]
            self.graphs[category]['labelHandler'].updateLabel('top', topValue, categoryColor)

    def displayAggregate(self, aggregateData):
        if not self.graphs['combined']['show']:
            return
        highestAverage = 0
        for category, items in aggregateData.items():
            highest = max(items["yValues"])
            if highest > highestAverage:
                highestAverage = highest
        combinedLines = self.graphs['combined']['lines']
        self.graphs['combined']['graph'].basicLine(aggregateData['dpsOut']['yValues'], "#00FFFF", combinedLines['dpsOut'])
        self.graphs['combined']['graph'].basicLine(aggregateData['dpsIn']['yValues'], "#FF0000", combinedLines['dpsIn'])
        self.graphs['combined']['graph'].basicLine(aggregateData['logiOut']['yValues'], "#00FF00", combinedLines['logiOut'])
        self.graphs['combined']['graph'].readjust(highestAverage)

        self.graphs['dpsOut']['labelHandler'].updateLabel('total', aggregateData['dpsOut']['yValues'][-1], "#00FFFF")
        self.graphs['dpsIn']['labelHandler'].updateLabel('total', aggregateData['dpsIn']['yValues'][-1], "#FF0000")
        self.graphs['logiOut']['labelHandler'].updateLabel('total', aggregateData['logiOut']['yValues'][-1], "#00FF00")
