from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from string import ascii_lowercase, ascii_uppercase, digits
from client import Client
from toolkit import SERVER, PORT


ALLOWED_SYMBOLS = ascii_uppercase + ascii_lowercase + digits + '_'


def button(title, on_click, layout=None):
    butt = QPushButton()
    butt.clicked.connect(on_click)
    butt.setText(title)
    if layout is not None:
        layout.addWidget(butt)
    return butt


def check_room_name(name):
    non_empty = False
    for ch in name:
        if ch not in [' ', '\n']:
            non_empty = True
        if ch not in ALLOWED_SYMBOLS:
            return False
    return non_empty


def error(err):
    error_dialog = QErrorMessage(err)
    error_dialog.show()


class Inputbox(QWidget):
    def __init__(self, text, title, on_value):
        QWidget.__init__(self)
        self.setWindowTitle(title)
        self.setFixedSize(350, 150)
        self.on_value = on_value
        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        self.setLayout(layout)
        label = QLabel()
        label.setText(text)
        self.inpbox = QLineEdit()
        done_btn = button('ОК', on_click=self.send)
        layout.addWidget(label, 0, 0, 1, 3)
        layout.addWidget(self.inpbox, 1, 0, 1, 3)
        layout.addWidget(done_btn, 2, 2, 1, 1)

    def send(self):
        text = self.inpbox.text()
        self.on_value(text)
        self.close()


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle('Начать игру')
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.listwidget = QListWidget()
        bottom = QHBoxLayout()
        button('Обновить', self.refresh, bottom)
        button('Создать', self.create, bottom)
        button('Подключиться', self.connect, bottom)
        layout.addWidget(self.listwidget)
        layout.addLayout(bottom)

        self.client = Client(SERVER, PORT)
        

    def create(self):
        self.input_box = Inputbox('Введите название комнаты', 
            'Создание комнаты', self._create_on_input)
        self.input_box.show()
        
    def _create_on_input(self, value):
        print(value)

    def connect(self):
        pass

    def refresh(self):
        pass


app = QApplication(sys.argv)
screen = Window()
screen.show()
sys.exit(app.exec_())