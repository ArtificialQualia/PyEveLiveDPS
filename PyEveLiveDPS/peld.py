"""
Main file for PyEveLiveDPS
"""

import window

class App():
    def __init__(self):
        graphWindow = window.BorderlessWindow()
        graphWindow.mainWindowDecorator()
        graphWindow.mainloop()
        
App()