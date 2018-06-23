
import tkinter as tk
import tkinter.font as tkFont

class DetailsHandler(tk.Frame):
    def __init__(self, parent, makeAllChildrenDraggable, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowCount = 1
        self.pilots = []
        self.enabledLabels = []
        
    def updateDetails(self, fieldName, historicalDetails, color):
        if fieldName not in self.enabledLabels:
            return
        for detailList in historicalDetails:
            for detail in detailList:
                if detail.get('pilotName'):
                    match = False
                    for pilot in self.pilots:
                        if pilot['pilotName'] == detail['pilotName']:
                            match = True
                            weaponMatch = False
                            for weapon in pilot['weaponGroups']:
                                if weapon['name'] == detail['weaponType']:
                                    weaponMatch = True
                                    weapon['amount'] += detail['amount']
                            if not weaponMatch:
                                weaponGroup = {}
                                weaponGroup['name'] = detail['weaponType']
                                weaponGroup['amount'] = detail['amount']
                                weaponGroup['color'] = color
                                pilot['weaponGroups'].append(weaponGroup)
                    if not match:
                        newPilot = {}
                        newPilot['pilotName'] = detail['pilotName']
                        newPilot['shipType'] = detail['shipType']
                        weaponGroup = {}
                        weaponGroup['name'] = detail['weaponType']
                        weaponGroup['amount'] = detail['amount']
                        weaponGroup['color'] = color
                        newPilot['weaponGroups'] = [weaponGroup]
                        self.pilots.append(newPilot)

    def cleanupAndDisplay(self, interval, length):
        for pilot in self.pilots:
            for weapon in pilot['weaponGroups']:
                weapon['amount'] = (weapon['amount']*(1000/interval))/length
                
        self.displayPilots()
        
        for pilot in self.pilots:
            noValues = False
            for weapon in pilot['weaponGroups']:
                if weapon['amount'] == 0:
                    pilot['weaponGroups'].remove(weapon)
                else:
                    weapon['amount'] = 0
            if len(pilot['weaponGroups']) == 0:
                pilot['detailFrame'].grid_forget()
                pilot['detailFrame'].destroy()
                self.pilots.remove(pilot)
        self.update_idletasks()
            
                
    def displayPilots(self):
        for pilot in self.pilots:
            if not pilot.get('detailFrame'):
                pilot['detailFrame'] = DetailFrame(self, pilot, background="black")
                self.rowCount += 1
                pilot['detailFrame'].grid(row=self.rowCount, column="0", sticky="news")
            pilot['detailFrame'].updateLabels(pilot['weaponGroups'])
            
    def enableLabel(self, labelName, enable):
        if labelName in self.enabledLabels:
            if not enable:
                self.enabledLabels.remove(labelName)
        else:
            if enable:
                self.enabledLabels.append(labelName)
            

class DetailFrame(tk.Frame):
    def __init__(self, parent, pilot, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.columnconfigure(1, weight=1)
        #self.decimalPlaces = settings["decimalPlaces"]
        #self.inThousands = settings["inThousands"]
        self.weaponLabels = []
        self.rowCount = 1
        
        self.pilotLabel = tk.Label(self, text=pilot['pilotName'], fg="white", background="black")
        self.pilotLabel.grid(row="0", column="0", columnspan="2", sticky="w")
        
        shipTypeString = "(" + pilot['shipType'] + ")"
        self.shipLabel = tk.Label(self, text=shipTypeString, fg="white", background="black")
        font = tkFont.Font(font=self.shipLabel['font'])
        font.config(slant='italic')
        self.shipLabel['font'] = font
        self.shipLabel.grid(row="0", column="2", sticky="w")
        
        tk.Frame(self, highlightthickness="1", highlightbackground="dim gray", background="black").grid(row="1000", column="0", columnspan="3", sticky="we")
        
    def updateLabels(self, weaponGroups):
        for label in self.weaponLabels:
            label[3] = False
        for group in weaponGroups:
            weaponMatch = False
            for label in self.weaponLabels:
                if group['name'] == label[1]['text']:
                    weaponMatch = True
                    label[2]['text'] = ('%.0f') % (round(group['amount'], 0),)
                    label[3] = True
            if not weaponMatch:
                self.rowCount += 1
                weaponLabel = []
                spacerFrame = tk.Frame(self, width="10", background="black")
                spacerFrame.grid(row=self.rowCount, column="0", sticky="w")
                weaponLabel.append(spacerFrame)
                nameLabel = tk.Label(self, text=group['name'], fg="white", background="black")
                nameLabel.grid(row=self.rowCount, column="1", sticky="w", columnspan="2")
                weaponLabel.append(nameLabel)
                amountLabel = tk.Label(self, fg=group['color'], background="black")
                amountLabel['text'] = ('%.0f') % (round(group['amount'], 0),)
                amountLabel.grid(row=self.rowCount, column="2", sticky="e")
                weaponLabel.append(amountLabel)
                weaponLabel.append(True)
                self.weaponLabels.append(weaponLabel)
        for label in self.weaponLabels:
            if not label[3]:
                label[0].grid_forget()
                label[0].destroy()
                label[1].grid_forget()
                label[1].destroy()
                label[2].grid_forget()
                label[2].destroy()
                self.weaponLabels.remove(label)