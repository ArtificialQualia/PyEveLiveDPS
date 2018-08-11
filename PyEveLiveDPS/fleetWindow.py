
import tkinter as tk
import tkinter.font as tkFont
from peld import settings
import socketManager

class FleetWindow(tk.Toplevel):
    def __init__(self, mainWindow):
        tk.Toplevel.__init__(self)
        
        self.mainWindow = mainWindow
        self.counter = 0
        
        characterEntries = mainWindow.characterDetector.menuEntries
        if len(characterEntries) == 0:
            self.destroy()
            tk.messagebox.showerror("Error", "PELD must be tracking a character before enabling fleet mode.")
        characterIndex = mainWindow.characterDetector.selectedIndex.get()
        self.characterName = characterEntries[characterIndex]
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(9, weight=1)
        self.configure(pady=10)
        
        self.wm_attributes("-topmost", True)
        self.wm_title("PyEveLiveDPS Fleet Mode")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        self.geometry("375x310")
        self.update_idletasks()
        
        characterFrame = tk.Frame(self)
        tk.Label(characterFrame, text="Character to use for fleet mode: ").grid(row="0", column="1", sticky="w")
        nameLabel = tk.Label(characterFrame, text=self.characterName)
        font = tkFont.Font(font=nameLabel['font'])
        font.config(weight='bold')
        nameLabel['font'] = font
        nameLabel.grid(row="0", column="2", sticky="w")
        nameDescription = tk.Label(self, text="To use a different character for fleet mode, choose a different\n" +
                            " character in the 'Character...' menu on the main window")
        font = tkFont.Font(font=nameDescription['font'])
        font.config(slant='italic')
        nameDescription['font'] = font
        characterFrame.grid(row=self.counter, column="1", columnspan="2", sticky="w")
        nameDescription.grid(row=self.counter+1, column="1", columnspan="2", sticky="w")
        tk.Frame(self, height="15", width="10").grid(row=self.counter+2, column="1", columnspan="2")
        self.counter += 3
        
        self.serverVar = tk.StringVar()
        self.serverVar.set(settings.fleetServer)
        self.addEntrySetting(self.serverVar, "Server to use: ", 
                        "Don't change this unless your FC tells you to")
        
        self.modeVar = tk.IntVar()
        self.modeVar.set(1)
        tk.Radiobutton(self, text="Fleet Member", variable=self.modeVar, value=1).grid(row=self.counter, column="1", sticky="w")
        self.counter += 1
        tk.Radiobutton(self, text="FC (requires fleet boss)", variable=self.modeVar, value=2).grid(row=self.counter, column="1", sticky="w")
        self.counter += 1
        tk.Frame(self, height="10", width="10").grid(row=self.counter, column="1", columnspan="5")
        self.counter += 1
        
        self.lowCPUVar = tk.BooleanVar()
        self.lowCPUVar.set(False)
        lowCPUCheckbutton = tk.Checkbutton(self, text="Use low CPU mode", variable=self.lowCPUVar)
        lowCPUCheckbutton.grid(row=self.counter, column="1", columnspan="2", sticky="w")
        descriptor = tk.Label(self, text="Most features will be disabled, but networking will work normally")
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row=self.counter+1, column="1", columnspan="2", sticky="w")
        tk.Frame(self, height="10", width="10").grid(row=self.counter+2, column="1", columnspan="2")
        self.counter += 3
        
        tk.Frame(self, height="10", width="1").grid(row="99", column="1", columnspan="5")
        
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row="100", column="0", columnspan="10")
        okButton = tk.Button(buttonFrame, text="  Login  ", command=self.login)
        okButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame, text="  Cancel  ", command=self.destroy)
        cancelButton.grid(row="0", column="2")
        
    def login(self):
        settings.fleetServer = self.serverVar.get()
        requestArgs = "/sso/login?read_fleet=esi-fleets.read_fleet.v1"
        if self.modeVar.get() == 1:
            requestArgs += "&login_type=member"
        else:
            requestArgs += "&write_fleet=esi-fleets.write_fleet.v1"
            requestArgs += "&login_type=fc"
        self.sockMgr = socketManager.SocketManager(self.serverVar.get(), self.characterName, requestArgs)
        self.sockMgr.start()
        self.mainWindow.mainMenu.menu.delete(3)
        self.mainWindow.mainMenu.menu.insert_command(3, label="End Fleet Mode", command=self.logout)
        self.mainWindow.mainMenu.menu.entryconfig(5, state="disabled")
        self.mainWindow.mainMenu.menu.entryconfig(6, state="disabled")
        self.mainWindow.topLabel.configure(text="Fleet Mode (" + self.characterName + ")")
        self.mainWindow.topLabel.grid()
        self.mainWindow.characterMenu.configure(state="disabled")
        self.mainWindow.animator.queue = self.sockMgr.queue
        self.destroy()
        
    def logout(self):
        self.mainWindow.animator.queue = None
        self.sockMgr.stop()
        self.mainWindow.mainMenu.menu.delete(3)
        self.mainWindow.mainMenu.menu.insert_command(3, label="Fleet Mode", command=lambda: FleetWindow(self.mainWindow))
        self.mainWindow.mainMenu.menu.entryconfig(5, state="normal")
        self.mainWindow.mainMenu.menu.entryconfig(6, state="normal")
        self.mainWindow.topLabel.grid_remove()
        self.mainWindow.characterMenu.configure(state="normal")
        
    def addEntrySetting(self, var, labelText, descriptorText):
        centerFrame = tk.Frame(self)
        centerFrame.grid(row=self.counter, column="1", columnspan="2", sticky="w")
        label = tk.Label(centerFrame, text=labelText)
        label.grid(row=self.counter, column="1", sticky="w")
        entry = tk.Entry(centerFrame, textvariable=var, width=25)
        entry.grid(row=self.counter, column="2", sticky="w")
        descriptor = tk.Label(self, text=descriptorText)
        font = tkFont.Font(font=descriptor['font'])
        font.config(slant='italic')
        descriptor['font'] = font
        descriptor.grid(row=self.counter+1, column="1", columnspan="2", sticky="w")
        tk.Frame(self, height="10", width="10").grid(row=self.counter+2, column="1", columnspan="5")
        self.counter += 3