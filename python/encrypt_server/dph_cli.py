import socket
import random

ip = '127.0.0.1'
port = 1233

sock = socket.socket()
sock.connect((ip, port))

parameters = sock.recv(1024).decode()
parts = parameters.split(',')

p = int(parts[0])
g = int(parts[1])  # alpha

y = random.randint(2, p - 2)
B = pow(g, y, p)
sock.send(str(B).encode())

A = int(sock.recv(1024).decode())

K = pow(A, y, p)

print(f"the key is: {K}")