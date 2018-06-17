"""
Main file for PyEveLiveDPS

All the heavy lifting for PELD is done in window.py
This should probably be changed in the future, so things can be initialized 
here rather than in the BorderlessWindow class (and improve error handling)
but almost everything has a dependency on some window component, so we just 
allow that to control it for now.

"""

import mainWindow
import traceback

class App():
    def __init__(self):
        graphWindow = mainWindow.MainWindow()
        graphWindow.mainloop()
    
try:
    App()
except Exception:
    traceback.print_exc()
    input("Press any key to close console")