new_png = []


def bit_not(n):
    n = int.from_bytes(n)
    return ((1 << 8) - 1 - n).to_bytes()


def bit_rol(n, d):
    n = int.from_bytes(n)
    return (((n << d) & ((1 << 8) - 1)) | (n >> (8 - d))).to_bytes()

with open('encrypted.png', 'rb') as png:
    i = 0
    while True:
        data = png.read(1)
        if not data:
            break

        data = bit_rol(data, 4)

        if i % 3 == 0:
            data = bit_not(data)

        data = (int.from_bytes(data) ^ 0xBA).to_bytes()
        new_png.append(data)

        i += 1

    new_png.reverse()

with open("new_png.png", 'wb') as f:
    for byte in new_png:
        f.write(byte)

