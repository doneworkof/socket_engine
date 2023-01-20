import json
import socket


PORT = 5049
SERVER = socket.gethostbyname(socket.gethostname())
META_FIELD = 'META'
UDATA_FIELD = 'UDATA'
HEADER = 64
FORMAT = 'utf8'


class MetaTag(str):
    def __init__(self, name):
        self.name = name

    def __call__(self, d):
        mf = d[META_FIELD]
        if self.name == mf or self.name in mf:
            return True
        return False

    def __repr__(self):
        return self.name

    def toJSON(self):
        return self.name


class Enum:
    def __init__(self, const):
        self.tags = {
            k: MetaTag(k) for k in const
        }
    
    def __getattr__(self, v):
        if v in self.tags:
            return self.tags[v]
        raise Exception('Invalid key')


T = Enum(['DISCONNECT', 'CREATE_ROOM', 'SUCCESS', 'REJECT',
    'GET_ROOM_LIST', 'JOIN_ROOM'])


def message(text, author):
    return {
        'text': text,
        'author': author
    }


def data_to_bytes(data):
    return json.dumps(data).encode(FORMAT)

def data_from_bytes(data):
    return json.loads(data.decode(FORMAT))

def strat_stop(conn, send=True):
    print('STRAT_STOP', send)
    if send:
        conn.send(b'OK')
        return
    conn.recv(HEADER)

def h_recv(conn, sub=None):
    print('RECIEVING MSG LEN')
    msg_len = conn.recv(HEADER)
    msg_len = int(msg_len.decode(FORMAT))
    strat_stop(conn)
    print('RECIEVING MAIN MESSAGE')
    data = conn.recv(msg_len)
    data = data_from_bytes(data)
    strat_stop(conn)
    if sub is not None:
        return data[sub]
    return data

def h_send(conn, data):
    data = data_to_bytes(data)
    msg_len = str(len(data)).encode(FORMAT)
    #print(msg_len)
    print('SENDING MSG_LEN')
    conn.send(msg_len)
    strat_stop(conn, False)
    print('SEND MAIN DATA')
    conn.send(data)
    print(data)
    strat_stop(conn, False)


def add_meta(base_data, *meta_tags):
    base_data[META_FIELD] = list(meta_tags)
    return base_data

def meta(*meta_tags):
    return add_meta({}, *meta_tags)