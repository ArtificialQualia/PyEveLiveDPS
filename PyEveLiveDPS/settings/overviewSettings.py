import tkinter as tk
import tkinter.font as tkFont
from peld import settings
import sys
import time
import platform
import os
import yaml
import logging

from logreader import _logReaders

class AnimatedGif(tk.Label):
    """
    Class to show animated GIF file in a label
    Use start() method to begin animation, and set the stop flag to stop it
    """
    def __init__(self, root, gif_file, delay=0.3):
        """
        :param root: tk.parent
        :param gif_file: filename (and path) of animated gif
        :param delay: delay between frames in the gif animation (float)
        """
        tk.Label.__init__(self, root)
        self.root = root
        self.gif_file = gif_file
        self.delay = delay  # Animation delay - try low floats, like 0.04 (depends on the gif in question)
        self.stop = False  # Thread exit request flag

        self._num = 0

    def start(self):
        """ Starts non-threaded version that we need to manually update() """
        self.start_time = time.time()  # Starting timer
        self._animate()

    def stop(self):
        """ This stops the after loop that runs the animation, if we are using the after() approach """
        self.stop = True

    def _animate(self):
        try:
            self.gif = tk.PhotoImage(file=self.gif_file, format='gif -index {}'.format(self._num))  # Looping through the frames
            self.configure(image=self.gif)
            self._num += 1
        except tk.TclError:  # When we try a frame that doesn't exist, we know we have to start over from zero
            self._num = 0
        if not self.stop:    # If the stop flag is set, we don't repeat
            self.root.after(int(self.delay*1000), self._animate)

class OverviewNotification(tk.Toplevel):
    
    def __init__(self):
        tk.Toplevel.__init__(self)
        
        self.wm_attributes("-topmost", True)
        self.wm_title("PyEveLiveDPS Overview Settings Warning")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        self.geometry("575x175")
        self.update_idletasks()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        warningText = "\nWARNING:\n\n" + \
                      "If you use custom EVE overview settings or you use an overview pack like Z-S, SaraShawa, etc.\n" + \
                      "You need to import your overview settings into PELD.\n\n" + \
                      "You can access these settings from the character menu at any time."

        tk.Label(self, image="::tk::icons::warning").grid(column="0", row="0", rowspan="90", padx="15")
        tk.Label(self, text=warningText, anchor='w', justify=tk.LEFT).grid(column="1", row="0", sticky="w")

        tk.Frame(self, height="20", width="10").grid(row="99", column="1", columnspan="5")
        
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row="100", column="0", columnspan="5")
        okButton = tk.Button(buttonFrame, text="  Open overview settings  ", command=self.openSettings)
        okButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame, text="  I am using default EVE overview settings  ", command=self.useDefault)
        cancelButton.grid(row="0", column="2")
        
        tk.Frame(self, height="20", width="10").grid(row="101", column="1", columnspan="5")

    def openSettings(self):
        OverviewSettingsWindow()
        self.destroy()

    def useDefault(self):
        settings.setOverviewFiles({'default': None})
        self.destroy()


class OverviewSettingsWindow(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        
        self.wm_attributes("-topmost", True)
        self.wm_title("PyEveLiveDPS Overview Settings")
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        self.geometry("700x800")
        self.update_idletasks()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        if (platform.system() == "Windows"):
            import win32com.client
            oShell = win32com.client.Dispatch("Wscript.Shell")
            self.overviewPath = oShell.SpecialFolders("MyDocuments") + "\\EVE\\Overview\\"
        else:
            self.overviewPath = os.environ['HOME'] + "/Documents/EVE/Overview/"

        mainFrame = tk.Frame(self, relief="groove", borderwidth=1)
        mainFrame.grid(row="0", column="0", sticky="news")
        mainFrame.columnconfigure(0, weight=1)
        mainFrame.rowconfigure(0, weight=1)

        self.scrollableCanvas = tk.Canvas(mainFrame, borderwidth=0)
        canvasFrame = tk.Frame(self.scrollableCanvas, padx=10, pady=5)
        scrollbar = tk.Scrollbar(mainFrame, orient="vertical", command=self.scrollableCanvas.yview)
        self.scrollableCanvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.scrollableCanvas.pack(side="left", fill="both", expand=True)
        self.canvas_frame = self.scrollableCanvas.create_window((0,0), window=canvasFrame, anchor="nw")
        self.scrollableCanvas.bind("<Configure>", self.onCanvasResize)
        canvasFrame.columnconfigure(1, weight=1)
        canvasFrame.rowconfigure(1, weight=1)
        canvasFrame.bind("<Configure>", self.onFrameConfigure)
        
        self.scrollableCanvas.bind('<Enter>', self.bindMousewheel)
        self.scrollableCanvas.bind('<Leave>', self.unbindMousewheel)

        topLabel = tk.Label(canvasFrame, text="You need to export your EVE overview settings for PELD to use them:")
        topLabel.grid(row="0", column="1")
            
        try:
            self.image = AnimatedGif(canvasFrame, sys._MEIPASS + '\\images\\peld-overview-export.gif')
            self.image.grid(row="1", column="1")
            self.image.start()
        except Exception:
            try:
                path = os.path.join('PyEveLiveDPS', 'images', 'peld-overview-export.gif')
                self.image = AnimatedGif(canvasFrame, path)
                self.image.grid(row="1", column="1")
                self.image.start()
            except Exception as e:
                logging.exception('Exception playing gif:')
                logging.exception(e)

        pictureLabelText = "NOTE: If you have separate overviews for different characters \n" + \
                           "you will need to export your settings to different files"
        belowPictureLabel = tk.Label(canvasFrame, text=pictureLabelText)
        belowPictureLabel.grid(row="2", column="1")

        settingsFrame = tk.Frame(canvasFrame)
        settingsFrame.grid(row="5", column="0", sticky="news", columnspan="5")
        self.settingRow = 0

        characters = []
        for logReader in _logReaders:
            characters.append(logReader.character)
        self.overviewFiles = settings.getOverviewFiles()
        if self.overviewFiles == {}:
            self.overviewFiles['default'] = None
            self.addSetting(settingsFrame, 'default', default=True)
        else:
            if 'default' in self.overviewFiles:
                self.addSetting(settingsFrame, 'default', default=True)
            for character in self.overviewFiles:
                if character != 'default':
                    if character in characters:
                        characters.remove(character)
                    self.addSetting(settingsFrame, character)
        for character in characters:
            self.addSetting(settingsFrame, character)
        
        tk.Frame(self, height="20", width="10").grid(row="99", column="0")
        
        buttonFrame = tk.Frame(self)
        buttonFrame.grid(row="100", column="0")
        okButton = tk.Button(buttonFrame, text="  Apply  ", command=self.doSettings)
        okButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="30").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame, text="  Cancel  ", command=self.destroy)
        cancelButton.grid(row="0", column="2")
        
        tk.Frame(self, height="20", width="10").grid(row="101", column="0")
            
    def addSetting(self, settingsFrame, characterName, default=None):
        innerFrame = tk.Frame(settingsFrame)
        innerFrame.grid(row=self.settingRow, column="0", sticky="w")
        innerFrame.columnconfigure(3, weight=1)
        tk.Frame(innerFrame, width="1", height="20").grid(row="0", column="0")

        settingLabel = tk.Label(innerFrame, text=characterName, padx=0, borderwidth=0)
        font = tkFont.Font(font=settingLabel['font'])
        font.config(weight='bold')
        settingLabel['font'] = font
        settingLabel.grid(row="1", column="0", sticky="w")
        settingColon = tk.Label(innerFrame, text=":")
        settingColon.grid(row="1", column="1", sticky="w")
        if default:
            settingDescriptor = tk.Label(innerFrame, text="(this is the overview setting applied to new characters)")
            font = tkFont.Font(font=settingDescriptor['font'])
            font.config(slant='italic')
            settingDescriptor['font'] = font
            settingDescriptor.grid(row="1", column="2")
        
        if characterName in self.overviewFiles:
            overviewFile = self.overviewFiles[characterName]
        else:
            overviewFile = 'Using PELD default overview setting'
        fileString = overviewFile or 'Using default EVE overview settings'
        overviewLabel = tk.Label(innerFrame, text=fileString)
        overviewLabel.grid(row="2", column="0", columnspan="5", sticky="w")

        buttonFrame = tk.Frame(innerFrame)
        buttonFrame.grid(row="3", column="0", columnspan="4")
        openOverviewFile = lambda: self.processOverviewFile(characterName, overviewLabel,
                           tk.filedialog.askopenfilename(initialdir=self.overviewPath, title="Select overview file"))
        openOverviewButton = tk.Button(buttonFrame, text=" Select overview settings file ", command=openOverviewFile)
        openOverviewButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="15").grid(row="0", column="1")
        revertEVEDefaultFunc = lambda: self.revertEVEDefault(characterName, overviewLabel)
        revertEVEDefaultButton = tk.Button(buttonFrame, text=" Use default EVE overview settings ", command=revertEVEDefaultFunc)
        revertEVEDefaultButton.grid(row="0", column="2")
        if not default:
            tk.Frame(buttonFrame, height="1", width="15").grid(row="0", column="3")
            revertDefaultFunc = lambda: self.revertPELDDefault(characterName, overviewLabel)
            revertDefaultButton = tk.Button(buttonFrame, text=" Use PELD default overview setting ", command=revertDefaultFunc)
            revertDefaultButton.grid(row="0", column="4")

        self.settingRow += 1

    def processOverviewFile(self, characterName, label, path):
        if not path:
            return
        try:
            with open(path, encoding='utf8') as overviewFileContent:
                overviewSettings = yaml.safe_load(overviewFileContent.read())
                if 'shipLabelOrder' not in overviewSettings or 'shipLabels' not in overviewSettings:
                    tk.messagebox.showerror("Error", "Overview settings not in YAML file:\n"+path)
                    return
                for shipLabel in overviewSettings['shipLabels']:
                    shipLabel[1] = dict(shipLabel[1])
                    if not shipLabel[1]['state']:
                        if shipLabel[1]['type'] in ['pilot name', 'ship type']:
                            logging.warning(shipLabel[1]['type'] + " not in "+str(path))
                            tk.messagebox.showerror("Error", "Error: The '"+shipLabel[1]['type']+"' is disabled in these " + \
                              "overview settings.  You need to enable the display of this label for PELD to track properly.\n\n" + \
                              "You can enable it on the 'ships' tab of your overview settings in EVE.\n\n" + \
                              "Don't forget to export your overview settings again!")
        except:
            logging.error("Error processing overview settings file: "+str(path))
            tk.messagebox.showerror("Error", "Error processing overview settings file:\n"+str(path))
            return
            
        self.overviewFiles[characterName] = path
        label.configure(text=path)

    def revertPELDDefault(self, characterName, label):
        self.overviewFiles[characterName] = "Using PELD default overview setting"
        label.configure(text=self.overviewFiles[characterName])

    def revertEVEDefault(self, characterName, label):
        self.overviewFiles[characterName] = "Using default EVE overview settings"
        label.configure(text=self.overviewFiles[characterName])
        
    def bindMousewheel(self, event):
        self.scrollableCanvas.bind_all("<MouseWheel>",self.MouseWheelHandler)
        self.scrollableCanvas.bind_all("<Button-4>",self.MouseWheelHandler)
        self.scrollableCanvas.bind_all("<Button-5>",self.MouseWheelHandler)
        
    def unbindMousewheel(self, event):
        self.scrollableCanvas.unbind_all("<MouseWheel>")
        self.scrollableCanvas.unbind_all("<Button-4>")
        self.scrollableCanvas.unbind_all("<Button-5>")
        
    def MouseWheelHandler(self, event):
        def delta(event):
            if event.num == 5 or event.delta < 0:
                return -1 
            return 1 
        self.scrollableCanvas.yview_scroll(-1*delta(event), "units")
        
    def onCanvasResize(self, event):
        self.scrollableCanvas.itemconfig(self.canvas_frame, width=event.width)
        
    def onFrameConfigure(self, event):
        self.scrollableCanvas.configure(scrollregion=self.scrollableCanvas.bbox("all"))   
        
    def doSettings(self):
        for characterName, settingsFile in self.overviewFiles.items():
            if settingsFile == "Using PELD default overview setting":
                del self.overviewFiles[characterName]
            elif settingsFile == "Using default EVE overview settings":
                self.overviewFiles[characterName] = None
        
        settings.setOverviewFiles(self.overviewFiles)

        for logReader in _logReaders:
            logReader.compileRegex()
        
        self.destroy()