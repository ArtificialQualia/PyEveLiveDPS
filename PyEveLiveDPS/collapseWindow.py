"""
CollapseWindow:

A special window which only contains a collapse button

This window overlays on top of the main window when PELD is in collapsed mode
  so that the rest of the window can not handle clicks (allowing the window
  underneath, i.e. EVE, to handle click events)
"""

from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QPushButton, QWidget, QGridLayout

from peld import settings, IMAGE_PATH

                
class UncollapseWindow():
    def __init__(self, mainWindow):
        self.window = QWidget()
        self.window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool | Qt.Dialog)
        self.window.setWindowOpacity(settings.compactTransparency/100)
        self.window.setStyleSheet('QPushButton { background: black; color: white; padding:2px 0px 2px 0px; border-style: none; }' + 
                                  'QPushButton:hover { background: rgb(60, 60, 60); } QPushButton:pressed { background: rgb(85, 85, 85); }' + 
                                  'QGridLayout { padding: 0px; margin: 0px; }')

        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.window.setLayout(self.layout)

        self.button = QPushButton()
        self.button.setIcon(QIcon(IMAGE_PATH + 'collapse.png'))
        self.button.clicked.connect(mainWindow.collapseEvent)
        self.layout.addWidget(self.button, 0, 0)

        geometry = mainWindow.window.buttonCollapse.geometry()
        globalPos = mainWindow.window.mapToGlobal(QPoint(geometry.x(), geometry.y()))
        self.window.setGeometry(globalPos.x(), globalPos.y(), geometry.width(), geometry.height())
        self.window.show()

    