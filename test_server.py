import socket


ADDRESS, PORT = 'localhost', 9764


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((ADDRESS, PORT))

sock.listen(1)

conn, addr = sock.accept()
conn.send('hello'.encode('utf8'))

conn.close()
sock.close()