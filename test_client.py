import socket


ADDRESS, PORT = 'localhost', 9764


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ADDRESS, PORT))

msg = sock.recv(128).decode('utf8')
print(msg)
sock.close()