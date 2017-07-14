"""
Main file for PyEveLiveDPS

All the heavy lifting for PELD is done in window.py
This should probably be changed in the future, so things can be initialized 
here rather than in the BorderlessWindow class (and improve error handling)
but almost everything has a dependency on some window component, so we just 
allow that to control it for now.

TODO: most of the huge functions should really be split up into many smaller
  functions, and more things should be done through get and set methods
  rather than class variables.
  Probably a whole separate class for the settings window as well.
"""

import window
import traceback

class App():
    def __init__(self):
        graphWindow = window.BorderlessWindow()
        graphWindow.mainloop()
    
try:
    App()
except Exception:
    traceback.print_exc()
    input("Press any key to close console")