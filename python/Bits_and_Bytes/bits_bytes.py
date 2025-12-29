import struct, socket, time


def hex_dump(s, SIZE=8):
    """
    print base 16 every byte
    :param s: byte array
    :param SIZE: optional (how many bytes per line)
    :return: Void
    """
    print("len=", len(s))
    for p in [s[i * SIZE: min((i + 1) * SIZE, len(s))] for i in range(len(s) // SIZE + 1)]:
        print(b" ".join([b"%02X" % int(p[i]) \
                             if i < len(p) else b"  " for i in range(SIZE)]) + \
              b"       " + b" ".join([chr(p[i]).encode()
                                      if 31 < p[i] < 128 else b"." for i in range(len(p))]))


print("\nQ1---------")
hex_dump("123 this string contains also hebrew אבג as you can see".encode(), 8)
heb = "אבג"
print("heb len:", len(heb))
print("heb len encoded :", len(heb.encode()))
hex_dump(heb.encode(), 8)

print("\nQ2---------")
some_byte_array = b"\x00\xd5\xfc\xfe\xff" + "Yossi".encode()
print(some_byte_array)
hex_dump(some_byte_array)
some_byte_array2 = b"\x00\x00\x00\x01\x02"
hex_dump(some_byte_array2)
some_int = struct.unpack("i", some_byte_array2[1:5])[0]  # LE=-66347=FF,FE,FC,D5     BE=-704,839,937
print("A some_int = ", some_int)
some_int = 0x00000102
print("B some_int = ", some_int)
some_int = 0x02010000
print("C some_int = ", some_int)

print("\nQ3---------")
some_int = 5
mask = 0xff000000
print("mask=", mask)
one_byte = some_int & mask
print("one_byte=", one_byte, "   %x" % one_byte, f"{one_byte:X}")
mask = 0x000000ff
print("mask=", mask)
one_byte2 = some_int & mask
print("one_byte2=", one_byte2, "   %x" % one_byte2, f"{one_byte2:X}")
#
# y = 65281
# mask = 0x0000ff00
# x = y & mask
# print("x=", x, f"{x:X}")

print("\nQ4---------")
print("Int By Bytes")
mask = 0x000000ff
x = 0xd3a4a506
print("x=", x, " ", "%08X" % x)
for i in range(4):

    print("  %02X " % ((x & mask) >> (i * 8)))
    mask <<= 8

print("\nQ5---------")
some_string = "\x00\x00\x00\x05"
some_byte_array = some_string.encode()
some_int = struct.unpack("i", some_byte_array[:4])[0]
print("1 some_int = ", some_int)
some_int = socket.ntohl(some_int)
print("2 some_int after ntohl = ", some_int)

print("\nQ6---------")
string = struct.pack("i", some_int)
hex_dump(string)
string = struct.pack("i", socket.htonl(some_int))
hex_dump(string)

some_int3 = struct.unpack("<i", string[:4])[0]
some_int4 = struct.unpack(">i", string[:4])[0]
print(" int 3 = ", some_int3)
print(" int 4 = ", some_int4)

# string = struct.pack("i",some_int)


print("\nQ7---------")


def send_one_message(sock, data):
    """
    Send a message to the socket with size before as int.
    """
    # sock.sendall(struct.pack('!I', len(message)) + message)
    length = socket.htonl(len(data))
    sock.sendall(struct.pack('I', length) + data)


print("\nQ8---------")


def recv_one_message(sock):
    """
    Recieve one message by two steps 4 bytes and all rest. max msg size 4G-1.
    """
    len_section = __recv_amount(sock, 4)
    if not len_section:
        return None
    len_int, = struct.unpack('I', len_section)
    len_int = socket.ntohl(len_int)
    # len_int, = struct.unpack('!I', len_section)

    data = __recv_amount(sock, len_int)

    if len_int != len(data):
        data = b''
    return data


def __recv_amount(sock, size):
    buffer = b''
    while size:
        new_bufffer = sock.recv(size)
        if not new_bufffer:
            return None
        buffer += new_bufffer
        size -= len(new_bufffer)
    # __hex(buffer)
    return buffer
