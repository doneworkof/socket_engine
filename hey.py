from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys


def button(title, on_click, layout=None):
    butt = QPushButton()
    butt.clicked.connect(on_click)
    butt.setText(title)
    if layout is not None:
        layout.addWidget(butt)
    return butt


def strweight(s):
    for i in s:
        if i not in [' ', '\n']:
            return True
    return False



app = QApplication(sys.argv)
screen = ChatWindow()
screen.show()
sys.exit(app.exec_())