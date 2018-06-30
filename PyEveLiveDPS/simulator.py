import random

class Simulator():
    def __init__(self, values, interval):
        self.values = values
        self.interval = interval
        self.timesRun = 0
        
    def simulate(self):
        try: damageOut = self.simulateValue(self.values["dpsOut"])
        except KeyError: damageOut = []
        try: logisticsOut = self.simulateValue(self.values["logiOut"])
        except KeyError: logisticsOut = []
        try: capTransfered = self.simulateValue(self.values["capOut"])
        except KeyError: capTransfered = []
        try: capDamageDone = self.simulateValue(self.values["neutOut"])
        except KeyError: capDamageDone = []
        try: damageIn = self.simulateValue(self.values["dpsIn"])
        except KeyError: damageIn = []
        try: logisticsIn = self.simulateValue(self.values["logiIn"])
        except KeyError: logisticsIn = []
        try: capRecieved = self.simulateValue(self.values["capIn"])
        except KeyError: capRecieved = []
        try: capDamageRecieved = self.simulateValue(self.values["neutIn"])
        except KeyError: capDamageRecieved = []
        try: mining = self.simulateValue(self.values["mining"])
        except KeyError: mining = []
        
        self.timesRun += 1
        
        return damageOut, damageIn, logisticsOut, logisticsIn, capTransfered, capRecieved, capDamageDone, capDamageRecieved, mining
    
    def simulateValue(self, value):
        returnValue = []
        returnGroup = {}
        if ((self.timesRun*self.interval)%(value["cycle"]*1000) == 0):
            returnGroup['amount'] = random.randint(value["floor"], value["ceiling"])
            returnGroup['pilotName'] = 'Pilot Name'
            returnGroup['shipType'] = 'ShipType'
            returnGroup['weaponType'] = 'Weapon Type'
            returnValue.append(returnGroup)
        return returnValue