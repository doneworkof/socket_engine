from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from string import ascii_lowercase, ascii_uppercase, digits
from client import Client
from toolkit import SERVER, PORT
from toolkit import *


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


def error(parent, msg, title='Ошибка!'):
    QMessageBox.about(parent, title, msg)


def strweight(s):
    for i in s:
        if i not in [' ', '\n']:
            return True
    return False


class ChatWindow(QWidget):
    def __init__(self, client):
        QWidget.__init__(self)
        self.resize(800, 600)
        self.setWindowTitle('Пробный чат')
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.textbox = QPlainTextEdit()
        self.textbox.setReadOnly(True)
        self.entry = QLineEdit()
        layout.addWidget(self.textbox)
        layout.addWidget(self.entry)
        button('Отправить', self.send, layout)
        self.client = client
        self.client.start_loop(self.loop)
    
    def loop(self):
        print('LOOP ITER')
        msg = self.client.recv()
        print('bloody nose!!!')
        author, text = msg['author'], msg['msg']
        self.append_chat(text, author)

    def send(self):
        v = self.entry.text()
        if not strweight(v):
            return
        self.entry.setText('')
        self.client.send({
            'author': '123',
            'msg': v
        })

    def append_chat(self, text, author):
        s = f'{author}: {text}'
        self.textbox.appendPlainText(s + '\n')


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
        self.refresh()
        
    def on_recv(self, msg):
        print('HEEEEEY', msg)

    def create(self):
        self.input_box = Inputbox('Введите название комнаты', 
            'Создание комнаты', self._create_on_input)
        self.input_box.show()
        
    def _create_on_input(self, value):
        self.client.send({
            'name': value
        }, T.CREATE_ROOM)
        
        self.client.recv({
            T.SUCCESS: self.refresh,
            T.REJECT: lambda: error(self, 'Ошибка создания!')
        })

    def get_selected(self):
        idx_list = self.listwidget.selectedIndexes()
        if not idx_list:
            return None
        return idx_list[0].row()

    def connect(self):
        idx = self.get_selected()
        if idx is None:
            return error(self, 'Необходимо выбрать комнату!')

        room_name = self.last_refresh['rooms'][idx]

        self.client.send({
            'name': room_name
        }, T.JOIN_ROOM)

        self.client.recv({
            T.SUCCESS: self.done,
            T.REJECT: lambda: error(self, 'Что-то пошло не так...')
        })

    def done(self):
        self.app = ChatWindow(self.client)
        self.app.show()

    def refresh(self):
        data = self.client.get_room_list()
        self.last_refresh = data
        self.listwidget.clear()
        self.listwidget.addItems([
            f'{a} ({c}/{b})' for a, b, c in zip(*data.values())
        ])


app = QApplication(sys.argv)
screen = Window()
screen.show()
sys.exit(app.exec_())