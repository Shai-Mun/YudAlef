import socket


def get_chunk_num(chunk):
    num = 0
    for s in chunk:
        if s != ">":
            num *= 10
            num += int(s)
        else:
            break

    return num


ip = "10.68.121.201"
port = 5014
sock = socket.socket()
sock.connect((ip, port))
data = sock.recv(1024)
print(data.decode())
sock.send('knthngowntin'.encode())

chunk_dict = {}

num = 1
string = ""
with open("file.txt", 'wb') as f:
    while data:
        data = sock.recv(1024)
        string += data.decode()

    chunks = string.split("<chunk number:")
    max_chunk_num = -1
    for c in chunks:
        chunk_num = get_chunk_num(c)
        if chunk_num > max_chunk_num:
            max_chunk_num = chunk_num

    for c in chunks:
        num = get_chunk_num(c)
        chunk_dict[num] = c[len(str(num)) + 1:]

    for i in range(677):
        f.write(chunk_dict[i].encode())
        print(chunk_dict[i], end="")
        # print(to_write)
        # print()




