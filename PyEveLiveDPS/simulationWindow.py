import tkinter as tk
from peld import settings
from localization import tr


class SimulationWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        tk.Toplevel.__init__(self)

        self.mainWindow = mainWindow
        self.graph = mainWindow.getGraph()
        self.animator = mainWindow.animator

        self.values = {}

        self.wm_attributes("-topmost", True)
        self.wm_title(tr("PyEveLiveDPS Simulation Settings"))
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        self.geometry("300x120")
        self.update_idletasks()

        self.columnconfigure(0, weight=1)

        tk.Label(self,
                 text=tr("For each item, a random number will be chosen") +
                 "\n" + tr("in the range you specify every cycle.")).grid(
                     row="0", column="0", columnspan="10")

        tk.Frame(self, height="20", width="1").grid(row="1",
                                                    column="1",
                                                    columnspan="5")

        self.innerFrame = tk.Frame(self)
        self.innerFrame.grid(row="2", column="0")

        if settings.getDpsOutSettings():
            tk.Label(self.innerFrame,
                     text=tr("DPS Out") + ":").grid(row="2",
                                                    column="0",
                                                    sticky="e")
            self.addRow("dpsOut", "2")
        if settings.getLogiOutSettings():
            tk.Label(self.innerFrame,
                     text=tr("Logistics Out") + ":").grid(row="3",
                                                          column="0",
                                                          sticky="e")
            self.addRow("logiOut", "3")
        if settings.getCapTransferedSettings():
            tk.Label(self.innerFrame,
                     text=tr("Cap Transfer Out") + ":").grid(row="4",
                                                             column="0",
                                                             sticky="e")
            self.addRow("capOut", "4")
        if settings.getCapDamageOutSettings():
            tk.Label(self.innerFrame,
                     text=tr("Cap Warfare Out") + ":").grid(row="5",
                                                            column="0",
                                                            sticky="e")
            self.addRow("neutOut", "5")
        if settings.getDpsInSettings():
            tk.Label(self.innerFrame, text=tr("DPS In") + ":").grid(row="6",
                                                                    column="0",
                                                                    sticky="e")
            self.addRow("dpsIn", "6")
        if settings.getLogiInSettings():
            tk.Label(self.innerFrame,
                     text=tr("Logistics In") + ":").grid(row="7",
                                                         column="0",
                                                         sticky="e")
            self.addRow("logiIn", "7")
        if settings.getCapRecievedSettings():
            tk.Label(self.innerFrame,
                     text=tr("Cap Transfer In") + ":").grid(row="8",
                                                            column="0",
                                                            sticky="e")
            self.addRow("capIn", "8")
        if settings.getCapDamageInSettings():
            tk.Label(self.innerFrame,
                     text=tr("Cap Warfare In") + ":").grid(row="9",
                                                           column="0",
                                                           sticky="e")
            self.addRow("neutIn", "9")
        if settings.getMiningSettings():
            tk.Label(self.innerFrame, text=tr("Mining") + ":").grid(row="10",
                                                                    column="0",
                                                                    sticky="e")
            self.addRow("mining", "10")

        tk.Frame(self, height="20", width="1").grid(row="99",
                                                    column="1",
                                                    columnspan="5")

        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row="100", column="0", columnspan="10")
        okButton = tk.Button(buttonFrame,
                             text=tr("  Run  "),
                             command=self.doSimulation)
        okButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame,
                                 text=tr("  Cancel  "),
                                 command=self.destroy)
        cancelButton.grid(row="0", column="2")

    def addRow(self, prefix, row):
        self.values[prefix] = {}
        self.values[prefix]["floor"] = tk.Entry(self.innerFrame, width=7)
        self.values[prefix]["floor"].grid(row=row, column="1")
        self.values[prefix]["floor"].insert(0, "0")
        tk.Label(self.innerFrame, text="-").grid(row=row, column="2")
        self.values[prefix]["ceiling"] = tk.Entry(self.innerFrame, width=7)
        self.values[prefix]["ceiling"].grid(row=row, column="3")
        self.values[prefix]["ceiling"].insert(0, "100")
        tk.Label(self.innerFrame, text=tr("  every")).grid(row=row, column="4")
        self.values[prefix]["cycle"] = tk.Entry(self.innerFrame, width=4)
        self.values[prefix]["cycle"].grid(row=row, column="5")
        self.values[prefix]["cycle"].insert(0, "3")
        tk.Label(self.innerFrame, text="s  ").grid(row=row, column="6")
        self.geometry("%sx%s" % (self.winfo_width(), self.winfo_height() + 20))
        self.update_idletasks()

    def doSimulation(self):
        valuesCopy = {}
        for value in self.values:
            valuesCopy[value] = {}
            for innerValue in self.values[value]:
                valuesCopy[value][innerValue] = self.values[value][
                    innerValue].get()

        for value in valuesCopy.values():
            try:
                value["floor"] = int(value["floor"])
                value["ceiling"] = int(value["ceiling"])
                value["cycle"] = int(value["cycle"])
                if not (value["cycle"] > 0):
                    tk.messagebox.showerror(
                        tr("Error"),
                        tr("Value for seconds must be greater than 0"))
                    return
                if (value["floor"] < 0) or (value["ceiling"] < 0):
                    tk.messagebox.showerror(
                        tr("Error"),
                        tr("Value for ranges must not be negative"))
                    return
            except ValueError:
                tk.messagebox.showerror(
                    tr("Error"),
                    tr("Please enter only whole, positive numbers for all values"
                       ))
                return

        self.mainWindow.mainMenu.menu.delete(7)
        self.mainWindow.mainMenu.menu.insert_command(
            7, label=tr("Stop Simulation"), command=self.stopSimulation)
        self.mainWindow.mainMenu.menu.entryconfig(5, state="disabled")

        self.mainWindow.topLabel.configure(text=tr("Simulation Mode"))
        self.mainWindow.topLabel.grid()

        self.mainWindow.characterDetector.catchupLog()
        self.animator.simulationSettings(enable=True, values=valuesCopy)

        self.destroy()

    def stopSimulation(self):
        self.animator.simulationSettings(enable=False)
        self.mainWindow.characterDetector.catchupLog()
        self.mainWindow.mainMenu.menu.delete(7)
        self.mainWindow.mainMenu.menu.insert_command(
            7,
            label=tr("Simulate Input"),
            command=lambda: SimulationWindow(self.mainWindow))
        self.mainWindow.mainMenu.menu.entryconfig(5, state="normal")
        self.mainWindow.topLabel.grid_remove()