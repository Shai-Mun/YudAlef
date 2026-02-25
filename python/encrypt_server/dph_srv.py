import socket
import random

ip = '0.0.0.0'
port = 1233

srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv_sock.bind((ip, port))
srv_sock.listen()

cli_sock, addr = srv_sock.accept()

p = 17
g = 3  # alpha
cli_sock.send(f"{p},{g}".encode())

x = random.randint(2, p - 2)
A = pow(g, x, p)
cli_sock.send(str(A).encode())

B = int(cli_sock.recv(1024).decode())

K = pow(B, x, p)

print(f"the key is: {K}")