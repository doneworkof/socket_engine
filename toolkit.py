import json
import socket


PORT = 4999
SERVER = socket.gethostbyname(socket.gethostname())
META_FIELD = 'META'
UDATA_FIELD = 'UDATA'
HEADER = 64
FORMAT = 'utf8'


class MetaTag:
    def __init__(self, name):
        self.name = name

    def __call__(self, d):
        mf = d[META_FIELD]
        if self.name == mf or self.name in mf:
            return True
        return False


class Enum:
    def __init__(self, const):
        self.tags = {
            k: MetaTag(k) for k in const
        }
    
    def __getattr__(self, v):
        if v in self.tags:
            return self.tags[v]
        raise Exception('Invalid key')


T = Enum(['DISCONNECT', 'NEW_ROOM'])


def data_to_bytes(data):
    return json.dumps(data).encode(FORMAT)

def data_from_bytes(data):
    return json.loads(data.decode(FORMAT))

def strat_stop(conn, send=True):
    if send:
        conn.send(b'OK')
        return
    conn.recv(HEADER)

def h_recv(conn, sub=None):
    msg_len = conn.recv(HEADER)
    msg_len = int(msg_len.decode(FORMAT))
    strat_stop(conn)
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
    conn.send(msg_len)
    strat_stop(conn, False)
    conn.send(data)
    print(data)
    strat_stop(conn, False)


def add_meta(base_data, *meta_tags):
    base_data[META_FIELD] = list(meta_tags)
    return base_data

def meta(*meta_tags):
    return add_meta({}, *meta_tags)