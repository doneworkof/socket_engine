import socket
from threading import Thread
from toolkit import *


class Room:
    def __init__(self, name, server):
        self.name = name
        self.server = server
        self.clients = {}

    def add_client(self, addr, conn):
        self.clients[addr] = conn

    def get_conn(self, addr):
        return self.clients[addr]

    def get_all_addr(self):
        return list(self.clients.keys())

    def broadcast(self, data, exclude=[]):
        for addr, conn in self.clients.items():
            if addr in exclude:
                continue
            try:
                h_send(conn, data)
            except Exception as ex:
                print(f'There is an error in room {self.name}: {ex}')
                self.clear()
    
    def close(self):
        for conn in self.clients.values():
            self.server.disconnect(conn)
        self.clients = {}
    
    def handle(self, addr, data):
        if addr not in self.clients:
            return False
        self.send(data, [addr])
        return True


class servfunc:
    def __init__(self, command):
        self.command = command
    
    def past_init(self, func):
        self.func = func
        return self

    def __call__(self, *args):
        return self.func(*args)


def ServerFunction(name):
    sf = servfunc(name)
    return sf.past_init


class Server:
    def __init__(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((address, port))
        self.rooms = {}
        self.serv_funcs = {
            k: a for k in dir(self)
            if type(a := getattr(self, k)) == servfunc
        }

    @ServerFunction(T.GET_ROOM_LIST)
    def _get_room_list(self, msg):
        room_names = list(self.rooms.keys())
        people = [r.people_count() for r in self.rooms.values()]
        max_capacity = [r.max_capacity() for r in self.rooms.values()]
        return {
            'rooms': room_names,
            'max_capacity': max_capacity,
            'current_size': people
        }

    @ServerFunction(T.CREATE_ROOM)
    def _create_room(self, msg):
        name = msg['name']
        if name in self.rooms:
            return meta(T.REJECT)
        self.rooms[name] = Room(name, self)
        return meta(T.SUCCESS)

    @ServerFunction(T.JOIN_ROOM)
    def _join_room(self, msg):
        addr, conn = msg[UDATA_FIELD]
        room_name = msg['name']
        if room_name not in self.rooms:
            return meta(T.REJECT)
        cb = self.rooms[room_name].add_client(addr, conn)
        return meta(T.REJECT if not cb else T.SUCCESS)

    def _start_serv_func(self, tag, data):
        if tag not in self.serv_funcs:
            return None
        func = self.serv_funcs[tag]
        return func(data)

    def _check_for_meta(self, addr, conn, msg):
        data = msg.copy()
        data[UDATA_FIELD] = (addr, conn)
        if META_FIELD not in data:
            return False
        success = 0
        for meta_tag in data[META_FIELD]:
            cb = self._start_serv_func(meta_tag, data)
            if cb is None:
                continue
            h_send(conn, cb)
            success += 1
        return success > 0

    def _destroy_room(self, name):
        if name in self.rooms:
            del self.rooms[name]

    def _handle_client(self, addr, conn):
        room = None

        while True:
            msg = h_recv(conn)
            if T.DISCONNECT(msg):
                conn.close()
                return
            callback = self._check_for_meta(msg)
            if callback or room is None:
                continue
            room.handle(addr, msg)
            if not room.clients:
                self._destroy_room(room.name)


    def _accept_loop(self):
        self.sock.listen()

        while True:
            conn, addr = self.sock.accept()
            thread = Thread(target=self._handle_client, args=(self, addr, conn))
            thread.start()

    def log(self, content, title='SERVER'):
        print(f'[{title}] {content}')

    def start(self):
        thr = Thread(target=self._accept_loop, args=(self,))
        thr.start()

    def disconnect(self, conn):
        try:
            h_send(conn, meta(T.DISCONNECT))
            conn.close()
        except:
            self.log(f'Failed disconnecting from {conn}')

    def close(self):
        for r in self.rooms.values():
            r.close()
        self.sock.close()



rooms = {}


def handle_client(addr, conn):
    room_list = list(rooms.keys())
    h_send(conn, {'rooms': room_list})
    ans = h_recv(conn, 'room')

    if ans == T.NEW_ROOM:
        room_name = h_recv(conn, 'name')
        room = Room(room_name)
        room.add_client(addr, conn)
        rooms[room_name] = room
    else:
        room = rooms[ans]
        room.add_client(addr, conn)

    while True:
        msg = h_recv(conn)
        if T.DISCONNECT in msg:
            conn.close()
            return
        room.recieve(addr, msg)
        if not room.clients:
            return


server.listen()

while True:
    conn, addr = server.accept()
    print('[NEW CONNECTION]', addr)
    thread = Thread(target=handle_client, args=(addr, conn))
    thread.start()


server.close()
