import socket
import re

s = socket.socket()
ip = '10.68.121.78'
port = 8576
s.connect((ip, port))

print(s.recv(1024).decode())
s.send(b'help')
print(s.recv(1024).decode())

# check = False
# for c in range(ord('A'), ord('Z')+1):
#     if check:
#         break
#
#     for sc in range(33, 48):
#         if check:
#             break
#
#         for n in range(0, 100):
#             if check:
#                 break
#
#             s.send((chr(c) + chr(sc) + str(n)).encode())
#
#             data = s.recv(1024).decode()
#             if not data.startswith("INCORRECT"):
#                 print((chr(c) + chr(sc) + str(n)).encode())
#                 check = True

s.send(b'G)11')
print(s.recv(1024).decode())

s.send(b'CONFIRM')
with open('test.jpg', 'wb') as p:
    for c in range(13):
        length = int(s.recv(6))
        data = b''
        while length != 0:
            chunk = s.recv(length)
            data += chunk
            length -= len(chunk)
        p.write(data)

'Moshe - 01001101 01101111 01110011 01101000 01100101'
'Tomer - 01010100 01101111 01101101 01100101 01110010'
'XOR - 00011001 00000000 00011110 00001101 00010111'

'25 0 30 13 23'
'80 78 65 97 73'
'50 4E 41 61 49'
'PNAaI'

s.send(b'PNAaI')
print(s.recv(1024).decode())
s.send(b'\x04')
print(s.recv(1024).decode())


def side_special(s):
    if 32 < ord(s[0]) < 47 and 32 < ord(s[1]) < 47:
        return True
    return False


s.send(b'CONFIRM')
data = s.recv(59469).decode()

with open('data.txt', 'w') as f:
    f.write(data)

words = data.split()
key = ""
for w in words:

    if re.search('^[!-/]{2}[A-Za-z]*[!-/]{2}$', w) is not None:
        print(w)
        if re.search('A-Z', w) is not None:
            key += re.search('A-Z', w)

print(key)
