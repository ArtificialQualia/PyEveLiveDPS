"""
UpdateChecker:
  
  checks for updates to PELD via the github releases API
  runs in a separate thread as to be non-blocking to the rest of the application
  
"""

import threading
import json
import version
import urllib.request
import urllib.error
import tkinter as tk
import tkinter.font as tkFont
from peld import logger
from peld import settings
import webbrowser

class UpdateChecker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, daemon=True)
        self.name = "UpdateChecker"

    def run(self):
        try:
            httpResponse = urllib.request.urlopen("https://api.github.com/repos/ArtificialQualia/PyEveLiveDPS/releases").read()
        except urllib.error.URLError as e:
            logger.exception('Exception checking for new releases:')
            logger.exception(e)
            return
        
        releases = json.loads(httpResponse.decode('utf-8'))
        
        logger.info('Current version: ' + version.version)
        logger.info('Latest release: ' + releases[0]['name'])
        if releases[0]['name'] != version.version and releases[0]['name'] != settings.disableUpdateReminderFor:
            UpdateNotificaitonWindow(releases)

class UpdateNotificaitonWindow(tk.Toplevel):
    def __init__(self, releases):
        tk.Toplevel.__init__(self)
        self.releases = releases
        self.wm_attributes("-topmost", True)
        self.wm_title("PELD Update Notification")
        
        try:
            self.iconbitmap(sys._MEIPASS + '\\app.ico')
        except Exception:
            try:
                self.iconbitmap("app.ico")
            except Exception:
                pass
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        
        self.geometry("+%s+%s" % (settings.getWindowX(), settings.getWindowY()))
        self.geometry("350x300")
        self.update_idletasks()
        
        windowHeader = tk.Label(self, text="Update Available")
        font = tkFont.Font(font=windowHeader['font'])
        font.config(size='16', weight='bold')
        windowHeader['font'] = font
        windowHeader.grid(row="0", column="0", columnspan="10")
        
        newVersionHeader = tk.Label(self, text=releases[0]['name'])
        font = tkFont.Font(font=newVersionHeader['font'])
        font.config(size='14', weight='bold')
        newVersionHeader['font'] = font
        newVersionHeader.grid(row="1", column="0", columnspan="10")
        
        oldVersionHeader = tk.Label(self, text="(current version: " + version.version + ")")
        font = tkFont.Font(font=oldVersionHeader['font'])
        font.config(slant='italic')
        oldVersionHeader['font'] = font
        oldVersionHeader.grid(row="2", column="0", columnspan="10")
        
        releaseNotesFrame = tk.Frame(self, padx="5")
        releaseNotesFrame.columnconfigure(0, weight=1)
        releaseNotesFrame.rowconfigure(0, weight=1)
        releaseNotesFrame.grid(row="3", column="0", columnspan="10")
        releaseNotes = tk.Text(releaseNotesFrame)
        for release in releases:
            if release['name'] != version.version:
                releaseNotes.insert(tk.END, 'Version '+release['name']+":\n")
                releaseNotes.insert(tk.END, release['body']+"\n\n\n")
            else:
                break
        releaseNotes.config(state=tk.DISABLED, wrap='word')
        releaseNotes.grid(row="0", column="0")
        scrollbar = tk.Scrollbar(releaseNotesFrame, command=releaseNotes.yview)
        scrollbar.grid(row="0", column="1", sticky='nsew')
        releaseNotes['yscrollcommand'] = scrollbar.set
        
        tk.Frame(self, height="5", width="1").grid(row="4", column="0")
        
        checkboxValue = tk.IntVar()
        checkboxValue.set(0)
        self.reminderCheckbox = tk.Checkbutton(self, text="Don't remind me about this release again", variable=checkboxValue)
        self.reminderCheckbox.var = checkboxValue
        self.reminderCheckbox.grid(row="5", column="0", columnspan="10", sticky="w")
        
        tk.Frame(self, height="5", width="1").grid(row="6", column="0")
        
        buttonFrame = tk.Frame(self)
        buttonFrame.columnconfigure(0, weight=1)
        buttonFrame.grid(row="100", column="0", columnspan="10")
        cancelButton = tk.Button(buttonFrame, text="Download", command=self.downloadAction, padx="10")
        cancelButton.grid(row="0", column="0")
        tk.Frame(buttonFrame, height="1", width="120").grid(row="0", column="1")
        cancelButton = tk.Button(buttonFrame, text="OK", command=self.okAction, padx="15")
        cancelButton.grid(row="0", column="2")
        
        tk.Frame(self, height="10", width="1").grid(row="101", column="0")
        
    def downloadAction(self):
        webbrowser.open("https://github.com/ArtificialQualia/PyEveLiveDPS/releases", autoraise=True)
        if self.reminderCheckbox.var.get():
            settings.disableUpdateReminderFor = self.releases[0]['name']
        self.destroy()
        
    def okAction(self):
        if self.reminderCheckbox.var.get():
            settings.disableUpdateReminderFor = self.releases[0]['name']
        self.destroy()