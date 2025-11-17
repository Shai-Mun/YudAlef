from tcp_by_size import send_with_size, recv_by_size


def handle_listen(sock, side):
    byte_data = b''

    while byte_data == b'':
        byte_data = recv_by_size(sock)

    data = byte_data.decode()
    fields = data.split("~")
    print(f"Side {side}: " + fields[0])
    return fields[1]


def handle_connect(sock):

    while True:
        msg = input("Enter a message\n")

        ret_port = input("Choose a port\n")
        if ret_port.isnumeric():
            return msg, int(ret_port)
