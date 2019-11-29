"""

"""

import platform
from PySide2.QtCore import QObject, QEvent, QPoint, Qt

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
        self.mousePresed = False

    def mousePressEvent(self, event):
        self.mousePresed = True
        self.oldPos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.window.move(self.window.x() + delta.x(), self.window.y() + delta.y())
        self.oldPos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.mousePresed = False

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self.mousePressEvent(event)
            return True
        elif event.type() == QEvent.MouseMove and self.mousePresed:
            self.mouseMoveEvent(event)
            return True
        elif event.type() == QEvent.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            self.mouseReleaseEvent(event)
            return True
        else:
            # standard event processing
            return QObject.eventFilter(self, obj, event)
