"""

"""

import platform
from PySide2.QtCore import QObject, QEvent, QPoint

class BaseWindow():
    def __init__(self):
        self.windowMover = WindowMover(self.window)
        self.oldPos = self.window.pos()

        self.window.installEventFilter(self.windowMover)
    
class WindowMover(QObject):
    def __init__(self, window):
        QObject.__init__(self)
        self.window = window
        self.oldPos = window.pos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.window.move(self.window.x() + delta.x(), self.window.y() + delta.y())
        self.oldPos = event.globalPos()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
            return True
        else:
            # standard event processing
            return QObject.eventFilter(self, obj, event)
