import socket
import struct


start = '10.68.121.78'
# ip = 78
port = 62534
# for i in range(0, 256):
#     ip = start + str(i)
#     print(i)
# for port in range(62500, 62600):
sock = socket.socket()
sock.settimeout(0.01)
try:
    sock.connect((start, port))
    sock.send('help'.encode())

    data = sock.recv(1024)
    print(data.decode())
    tup = struct.unpack('L', data[:4])
    x = socket.ntohl(tup[0])
    print(x)

    sock.send(str(x).encode())
    data = sock.recv(1024)
    print(data.decode())

    msg = 'NAME=Shai'
    sock.send(msg.encode())
    data = sock.recv(1024)
    print(data.decode())

    msg = 'what do you want'
    sock.send(msg.encode())
    data = sock.recv(1024)
    print(data.decode())

    msg = 'FF:FF:FF:FF:FF:FF'
    sock.send(msg.encode())
    data = sock.recv(1024)
    tup = struct.unpack('L', data[:4])
    x = socket.ntohl(tup[0])
    print(x)


except socket.error as err:
    if err.errno == 10035 or str(err) == "timed out":
        pass
    sock.close()






