import socket
from toolkit import *
from threading import Thread


    
class Client:
    def create_socket(self, address, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, port))
        return sock

    def __init__(self, address, port):
        self.recver = self.create_socket(address, port)
        h_send(self.recver, {
            'status': 'recver'
        })
        idx = h_recv(self.recver, 'idx')
        self.sender = self.create_socket(address, port)
        h_send(self.sender, {
            'status': 'sender',
            'idx': idx
        })

    def send(self, data, *meta_tags):
        data = add_meta(data, *meta_tags)
        h_send(self.sender, data)

    def close(self):
        h_send(self.sender, meta(T.DISCONNECT))
        self.sender.close()
        self.recver.close()

    def get_room_list(self):
        self.send(meta(T.GET_ROOM_LIST))
        return self.recv()
    
    def join_room(self, name):
        raise NotImplementedError()
        h_send(self.sock, add_meta({
            'name': name
        }, T.JOIN_ROOM))
        cb = h_recv(self.sock)
        return T.SUCCESS(cb)

    def create_room(self, name):
        raise NotImplementedError()
        h_send(self.sock, add_meta({
            'name': name
        }, T.CREATE_ROOM))
        cb = h_recv(self.sock)
        return T.SUCCESS(cb)
    
    def recv(self, actions=None, pass_data=False):
        data = h_recv(self.recver)
        if actions is None:
            return data
        for tag, func in actions.items():
            if not tag(data):
                continue
            if pass_data:
                func(data)
            else:
                func()
        return data

    def _loop(self, func):
        while True:
            cb = func()
            if not cb:
                break

    def start_loop(self, loop_func):
        thr = Thread(target=self._loop, args=(loop_func,))
        thr.start()

