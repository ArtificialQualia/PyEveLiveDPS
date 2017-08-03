import random

class Simulator():
    def __init__(self, values, interval):
        self.values = values
        self.interval = interval
        self.timesRun = 0
        
    def simulate(self):
        try: damageOut = self.simulateValue(self.values["dpsOut"])
        except KeyError: damageOut = 0
        try: logisticsOut = self.simulateValue(self.values["logiOut"])
        except KeyError: logisticsOut = 0
        try: capTransfered = self.simulateValue(self.values["capOut"])
        except KeyError: capTransfered = 0
        try: capDamageDone = self.simulateValue(self.values["neutOut"])
        except KeyError: capDamageDone = 0
        try: damageIn = self.simulateValue(self.values["dpsIn"])
        except KeyError: damageIn = 0
        try: logisticsIn = self.simulateValue(self.values["logiIn"])
        except KeyError: logisticsIn = 0
        try: capRecieved = self.simulateValue(self.values["capIn"])
        except KeyError: capRecieved = 0
        try: capDamageRecieved = self.simulateValue(self.values["neutIn"])
        except KeyError: capDamageRecieved = 0
        
        self.timesRun += 1
        
        return damageOut, damageIn, logisticsOut, logisticsIn, capTransfered, capRecieved, capDamageDone, capDamageRecieved
    
    def simulateValue(self, value):
        if ((self.timesRun*self.interval)%(value["cycle"]*1000) == 0):
            return random.randint(value["floor"], value["ceiling"])
        return 0