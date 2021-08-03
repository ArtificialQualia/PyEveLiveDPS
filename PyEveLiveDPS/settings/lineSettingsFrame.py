import tkinter as tk
import tkinter.font as tkFont
import tkinter.colorchooser as colorchooser
import sys
import copy
from peld import settings
from localization import tr


class LineSettingsFrame(tk.Frame):
    def __init__(self, parent, mainWindow, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.mainWindow = mainWindow

        self.scrollableCanvas = tk.Canvas(self, borderwidth=0, height="350")
        canvasFrame = tk.Frame(self.scrollableCanvas)
        scrollbar = tk.Scrollbar(self,
                                 orient="vertical",
                                 command=self.scrollableCanvas.yview)
        self.scrollableCanvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.scrollableCanvas.pack(side="left", fill="both", expand=True)
        self.canvas_frame = self.scrollableCanvas.create_window(
            (0, 0), window=canvasFrame, anchor="nw")
        self.scrollableCanvas.bind("<Configure>", self.onCanvasResize)
        canvasFrame.columnconfigure(0, weight=1)
        canvasFrame.bind("<Configure>", self.onLineFrameConfigure)

        self.scrollableCanvas.bind('<Enter>', self.bindMousewheel)
        self.scrollableCanvas.bind('<Leave>', self.unbindMousewheel)

        dpsOutFrame = tk.Frame(canvasFrame)
        dpsOutFrame.grid(row="6",
                         column="0",
                         columnspan="5",
                         padx="5",
                         sticky="we")
        self.dpsOutSettings = settings.getDpsOutSettings()
        self.addLineSection(dpsOutFrame, tr("Outgoing: DPS"),
                            self.dpsOutSettings)

        dpsInFrame = tk.Frame(canvasFrame)
        dpsInFrame.grid(row="14",
                        column="0",
                        columnspan="5",
                        padx="5",
                        sticky="we")
        self.dpsInSettings = settings.getDpsInSettings()
        self.addLineSection(dpsInFrame, tr("Incoming: DPS"),
                            self.dpsInSettings)

        logiOutFrame = tk.Frame(canvasFrame)
        logiOutFrame.grid(row="8",
                          column="0",
                          columnspan="5",
                          padx="5",
                          sticky="we")
        self.logiOutSettings = settings.getLogiOutSettings()
        self.addLineSection(logiOutFrame, tr("Outgoing: logistics"),
                            self.logiOutSettings)

        logiInFrame = tk.Frame(canvasFrame)
        logiInFrame.grid(row="16",
                         column="0",
                         columnspan="5",
                         padx="5",
                         sticky="we")
        self.logiInSettings = settings.getLogiInSettings()
        self.addLineSection(logiInFrame, tr("Incoming: logistics"),
                            self.logiInSettings)

        capTransferedFrame = tk.Frame(canvasFrame)
        capTransferedFrame.grid(row="10",
                                column="0",
                                columnspan="5",
                                padx="5",
                                sticky="we")
        self.capTransferedSettings = settings.getCapTransferedSettings()
        self.addLineSection(capTransferedFrame,
                            tr("Outgoing: capacitor transfer"),
                            self.capTransferedSettings)

        capRecievedFrame = tk.Frame(canvasFrame)
        capRecievedFrame.grid(row="18",
                              column="0",
                              columnspan="5",
                              padx="5",
                              sticky="we")
        self.capRecievedSettings = settings.getCapRecievedSettings()
        self.addLineSection(
            capRecievedFrame,
            tr("Incoming: capacitor transfer (including +nos)"),
            self.capRecievedSettings)

        capDamageOutFrame = tk.Frame(canvasFrame)
        capDamageOutFrame.grid(row="12",
                               column="0",
                               columnspan="5",
                               padx="5",
                               sticky="we")
        self.capDamageOutSettings = settings.getCapDamageOutSettings()
        self.addLineSection(capDamageOutFrame, tr("Outgoing: capacitor drain"),
                            self.capDamageOutSettings)

        capDamageInFrame = tk.Frame(canvasFrame)
        capDamageInFrame.grid(row="20",
                              column="0",
                              columnspan="5",
                              padx="5",
                              sticky="we")
        self.capDamageInSettings = settings.getCapDamageInSettings()
        self.addLineSection(capDamageInFrame, tr("Incoming: capacitor drain"),
                            self.capDamageInSettings)

        miningFrame = tk.Frame(canvasFrame)
        miningFrame.grid(row="22",
                         column="0",
                         columnspan="5",
                         padx="5",
                         sticky="we")
        self.miningSettings = settings.getMiningSettings()
        self.addLineSection(miningFrame,
                            tr("Mining"),
                            self.miningSettings,
                            mining=True)

    def bindMousewheel(self, event):
        self.scrollableCanvas.bind_all("<MouseWheel>", self.MouseWheelHandler)
        self.scrollableCanvas.bind_all("<Button-4>", self.MouseWheelHandler)
        self.scrollableCanvas.bind_all("<Button-5>", self.MouseWheelHandler)

    def unbindMousewheel(self, event):
        self.scrollableCanvas.unbind_all("<MouseWheel>")
        self.scrollableCanvas.unbind_all("<Button-4>")
        self.scrollableCanvas.unbind_all("<Button-5>")

    def MouseWheelHandler(self, event):
        def delta(event):
            if event.num == 5 or event.delta < 0:
                return -1
            return 1

        self.scrollableCanvas.yview_scroll(-1 * delta(event), "units")

    def onCanvasResize(self, event):
        self.scrollableCanvas.itemconfig(self.canvas_frame, width=event.width)

    def onLineFrameConfigure(self, event):
        self.scrollableCanvas.configure(
            scrollregion=self.scrollableCanvas.bbox("all"))

    def addLineSection(self, frame, text, settingsList, mining=False):
        #frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        innerFrame = tk.Frame(frame, borderwidth=1, relief="sunken", padx="5")
        innerFrame.columnconfigure(0, weight=1)
        innerFrame.grid(row="2", column="0", columnspan="3", sticky="we")
        lineCheckboxValue = tk.BooleanVar()
        lineCheckbox = tk.Checkbutton(frame,
                                      variable=lineCheckboxValue,
                                      text=tr("Only show label"),
                                      state="disabled")
        lineCheckbox.grid(row="0", column="2", sticky="w")
        lineCheckbox.var = lineCheckboxValue
        peakCheckboxValue = tk.BooleanVar()
        peakCheckbox = tk.Checkbutton(frame,
                                      variable=peakCheckboxValue,
                                      text=tr("Show peak value"),
                                      state="disabled")
        peakCheckbox.grid(row="1", column="2", sticky="e")
        peakCheckbox.var = peakCheckboxValue
        totalCheckboxValue = tk.BooleanVar()
        totalCheckbox = tk.Checkbutton(frame,
                                       variable=totalCheckboxValue,
                                       text=tr("Show total value"),
                                       state="disabled")
        totalCheckbox.grid(row="1", column="0", columnspan="2", sticky="e")
        totalCheckbox.var = totalCheckboxValue
        if mining:
            m3CheckboxValue = tk.BooleanVar()
            m3Checkbox = tk.Checkbutton(
                frame,
                variable=m3CheckboxValue,
                text=tr("Show m3 mined instead of units"),
                state="disabled")
            m3Checkbox.grid(row="1", column="0", columnspan="2", sticky="w")
            m3Checkbox.var = m3CheckboxValue
        else:
            m3Checkbox = None
        checkboxValue = tk.BooleanVar()
        if len(settingsList) == 0:
            checkboxValue.set(False)
        else:
            checkboxValue.set(True)
            lineCheckboxValue.set(settingsList[0].get("labelOnly", False))
            peakCheckboxValue.set(settingsList[0].get("showPeak", False))
            totalCheckboxValue.set(settingsList[0].get("showTotal", False))
            if mining:
                m3CheckboxValue.set(settingsList[0].get("showM3", False))
            self.addLineCustomizationSection(innerFrame, text, checkboxValue,
                                             lineCheckbox, peakCheckbox,
                                             totalCheckbox, settingsList,
                                             m3Checkbox)
        sectionCheckbox = tk.Checkbutton(
            frame,
            variable=checkboxValue,
            text=text + tr(" tracking"),
            command=lambda: self.addLineCustomizationSection(
                innerFrame, text, checkboxValue, lineCheckbox, peakCheckbox,
                totalCheckbox, settingsList, m3Checkbox))
        font = tkFont.Font(font=sectionCheckbox['font'])
        font.config(weight='bold')
        sectionCheckbox['font'] = font
        sectionCheckbox.grid(row="0", column="0", sticky="w")
        tk.Frame(frame, height="20", width="10").grid(row="1000",
                                                      column="1",
                                                      columnspan="5")

    def addLineCustomizationSection(self, frame, text, checkboxValue,
                                    lineCheckbox, peakCheckbox, totalCheckbox,
                                    settingsList, m3Checkbox):
        if checkboxValue.get():
            frame.grid()
            innerLabel = tk.Label(
                frame,
                text=tr(
                    "Color and threshold (when to change colors) for this line:"
                ))
            innerLabel.grid(row="0", column="0")
            font = tkFont.Font(font=innerLabel['font'])
            font.config(slant='italic')
            innerLabel['font'] = font
            if len(settingsList) == 0:
                settingsList.append({"transitionValue": 0, "color": "#FFFFFF"})
            for setting in settingsList:
                valueHolder = setting["transitionValue"]
                setting["transitionValue"] = tk.StringVar()
                setting["transitionValue"].set(valueHolder)
            innerFrame = tk.Frame(frame)
            innerFrame.grid(row="1", column="0", columnspan="5")
            self.expandCustomizationSettings(innerFrame, settingsList)
            lineCheckbox.configure(state="normal")
            settingsList[0].update({"labelOnly": lineCheckbox.var})
            peakCheckbox.configure(state="normal")
            settingsList[0].update({"showPeak": peakCheckbox.var})
            totalCheckbox.configure(state="normal")
            settingsList[0].update({"showTotal": totalCheckbox.var})
            if m3Checkbox:
                m3Checkbox.configure(state="normal")
                settingsList[0].update({"showM3": m3Checkbox.var})
        else:
            for child in frame.winfo_children():
                child.destroy()
            frame.grid_remove()
            settingsList.clear()
            lineCheckbox.var.set(0)
            lineCheckbox.configure(state="disabled")
            peakCheckbox.var.set(0)
            peakCheckbox.configure(state="disabled")
            totalCheckbox.var.set(0)
            totalCheckbox.configure(state="disabled")
            if m3Checkbox:
                m3Checkbox.var.set(0)
                m3Checkbox.configure(state="disabled")

    def expandCustomizationSettings(self, frame, settingsList):
        index = 0
        for setting in settingsList:
            removeButton = tk.Button(frame,
                                     text="X",
                                     command=lambda i=index: self.removeLine(
                                         i, settingsList, frame))
            font = tkFont.Font(font=removeButton['font'])
            font.config(weight='bold')
            removeButton['font'] = font
            removeButton.grid(row=index, column="0")
            initialLabel = tk.Label(
                frame, text=tr("Threshold when the line changes color:"))
            initialLabel.grid(row=index, column="1")
            initialThreshold = tk.Entry(
                frame,
                textvariable=settingsList[index]["transitionValue"],
                width=10)
            if (index == 0):
                initialThreshold.configure(state="disabled")
                removeButton.configure(state="disabled",
                                       borderwidth="0",
                                       text=" X ")
            initialThreshold.grid(row=index, column="2")
            initialLabel = tk.Label(frame, text=tr("Color:"))
            initialLabel.grid(row=index, column="3")
            colorButton = tk.Button(frame,
                                    text="    ",
                                    command=lambda i=index: self.colorWindow(
                                        settingsList[i], colorButton),
                                    bg=settingsList[index]["color"])
            colorButton.grid(row=index, column="4")
            index += 1

        addLineButton = tk.Button(
            frame,
            text=tr("Add Another Threshold"),
            command=lambda: self.addLine(settingsList, frame))
        addLineButton.grid(row="100", column="1")

    def addLine(self, settingsList, dpsFrame):
        lineNumber = len(settingsList)
        settingsList.append({"transitionValue": "", "color": "#FFFFFF"})
        settingsList[lineNumber]["transitionValue"] = tk.StringVar()
        settingsList[lineNumber]["transitionValue"].set(str(100 * lineNumber))

        removeButton = tk.Button(dpsFrame,
                                 text="X",
                                 command=lambda: self.removeLine(
                                     lineNumber, settingsList, dpsFrame))
        font = tkFont.Font(font=removeButton['font'])
        font.config(weight='bold')
        removeButton['font'] = font
        removeButton.grid(row=lineNumber, column="0")
        lineLabel = tk.Label(dpsFrame,
                             text=tr("Threshold when the line changes color:"))
        lineLabel.grid(row=lineNumber, column="1")
        initialThreshold = tk.Entry(
            dpsFrame,
            textvariable=settingsList[lineNumber]["transitionValue"],
            width=10)
        initialThreshold.grid(row=lineNumber, column="2")
        initialLabel = tk.Label(dpsFrame, text="Color:")
        initialLabel.grid(row=lineNumber, column="3")
        colorButton = tk.Button(dpsFrame,
                                text="    ",
                                command=lambda: self.colorWindow(
                                    settingsList[lineNumber], colorButton),
                                bg=settingsList[lineNumber]["color"])
        colorButton.grid(row=lineNumber, column="4")

    def removeLine(self, index, settingsList, dpsFrame):
        settingsList.pop(index)
        for child in dpsFrame.winfo_children():
            child.destroy()
        self.expandCustomizationSettings(dpsFrame, settingsList)

    def colorWindow(self, settingsListValue, button):
        x, settingsListValue["color"] = colorchooser.askcolor()
        button.configure(bg=settingsListValue["color"])

    def doSettings(self):
        self.settingsCopy = {
            "dpsIn": copy.copy(self.dpsInSettings),
            "dpsOut": copy.copy(self.dpsOutSettings),
            "logiIn": copy.copy(self.logiInSettings),
            "logiOut": copy.copy(self.logiOutSettings),
            "capTransfered": copy.copy(self.capTransferedSettings),
            "capRecieved": copy.copy(self.capRecievedSettings),
            "capDamageOut": copy.copy(self.capDamageOutSettings),
            "capDamageIn": copy.copy(self.capDamageInSettings),
            "mining": copy.copy(self.miningSettings)
        }

        for name, settings in self.settingsCopy.items():
            if len(settings) > 0:
                settings[0]["labelOnly"] = settings[0]["labelOnly"].get()
                settings[0]["showPeak"] = settings[0]["showPeak"].get()
                settings[0]["showTotal"] = settings[0]["showTotal"].get()

        if len(self.settingsCopy["mining"]) > 0:
            self.settingsCopy["mining"][0]["showM3"] = self.settingsCopy[
                "mining"][0]["showM3"].get()

        for name, settings in self.settingsCopy.items():
            for setting in settings:
                try:
                    int(setting["transitionValue"].get())
                except ValueError:
                    tk.messagebox.showerror(
                        tr("Error"),
                        tr("Please enter a number for all line color threshold values"
                           ))
                    return
            for setting in settings:
                setting["transitionValue"] = int(
                    setting["transitionValue"].get())

        for name, settings in self.settingsCopy.items():
            settings = sorted(settings,
                              key=lambda setting: setting["transitionValue"])

        return self.settingsCopy