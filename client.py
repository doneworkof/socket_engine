import socket
from toolkit import *
from threading import Thread


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((SERVER, PORT))


rooms = h_recv(server, 'rooms')


def create_room():
    h_send(server, {'room': T.NEW_ROOM})
    room_name = input('Room name: ')
    h_send(server, {'name': room_name})

def join_room(rooms):
    print(rooms)
    room_id = int(input())
    h_send(server, {'room': rooms[room_id]})


def handle_data(server, on_recieve, on_close):
    while True:
        msg = h_recv(server)
        if T.DISCONNECT in msg:
            server.close()
            return
        on_recieve(msg)
    
    
class Client:
    def __init__(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = self.sock.connect((address, port))

    def get_room_list(self):
        pass

    def join_room(self):
        pass

    def create_new_room(self, name):
        pass

    def on_recieve(self, msg):
        pass

    def on_drop(self):
        pass

    def close(self):
        pass
    
    def _loop(self):
        while True:
            msg = h_recv(self.sock)
            if T.DISCONNECT(msg):
                self.on_drop()
                self.sock.close()
            self.on_recieve(msg)
    
    def start(self):
        thr = Thread(target=self._loop, args=(self))
        thr.start()



if not rooms:
    create_room()
else:
    p = input('Create room? (y/n) ')
    if p == 'y':
        create_room()
    else:
        join_room(rooms)


h_send(server, {'msg': 'fuck!'})

while True:
    msg = h_recv(server)
    print(msg)


server.close()