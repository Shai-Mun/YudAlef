import base64
import socket


ip = '10.68.121.78'
port = 25
sock = socket.socket()
sock.connect((ip, port))
print(sock.recv(1024).decode())
sock.send('EHLO pc3-01\r\n'.encode())
print(sock.recv(1024).decode())

mail = b'\x00shai@gmail.com\x00MyPass1!'
sock.send('AUTH LOGIN PLAIN\r\n'.encode())
print(sock.recv(1024).decode())
sock.send(base64.b64encode(b'shai') + '\r\n'.encode())
print(sock.recv(1024).decode())
sock.send(base64.b64encode(b'MyPass1!') + '\r\n'.encode())
print(sock.recv(1024).decode())

sock.send('MAIL FROM:<shai@gmail.com>\r\n'.encode())
print(sock.recv(1024).decode())
sock.send('RCPT TO:yossi@gmail.com\r\n'.encode())
print(sock.recv(1024).decode())
sock.send('DATA\r\n'.encode())
print(sock.recv(1024).decode())
sock.send('Subject: Testing, testing!\r\nThis is Shai testing the protocol, I want to see if this works\r\n.\r\n'.encode())
print(sock.recv(1024).decode())

sock.send('QUIT\r\n'.encode())
print(sock.recv(1024).decode())







