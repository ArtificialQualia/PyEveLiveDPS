"""
Main file for PyEveLiveDPS

All the heavy lifting for PELD is done in window.py
This should probably be changed in the future, so things can be initialized 
here rather than in the BorderlessWindow class (and improve error handling)
but almost everything has a dependency on some window component, so we just 
allow that to control it for now.
"""

import window

class App():
    def __init__(self):
        graphWindow = window.BorderlessWindow()
        graphWindow.mainloop()
    
App()