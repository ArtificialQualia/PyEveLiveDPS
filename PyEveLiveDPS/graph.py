import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk

class DPSGraph(tk.Frame):

    def __init__(self):
        tk.Frame.__init__(self)
        
        self.graphFigure = Figure(figsize=(6,3), dpi=100, facecolor="black")
        
        self.subplot = self.graphFigure.add_subplot(1,1,1, facecolor=(0.3, 0.3, 0.3))
        self.subplot.tick_params(axis="both", colors="grey")
        self.subplot.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])
        
        self.graphFigure.tight_layout(pad=0.1, w_pad=0.1, h_pad=0.1)

        self.canvas = FigureCanvasTkAgg(self.graphFigure, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)