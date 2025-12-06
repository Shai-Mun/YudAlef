import socket

from tcp_by_size import send_with_size, recv_by_size


def handle_listen(port, side, other_side):
    sock = socket.socket()
    sock.bind(('0.0.0.0', port))
    sock.listen(2)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    other_sock, addr = sock.accept()

    listen_msg = f'Side {side} listening to port {port}'
    print(listen_msg)
    send_with_size(other_sock, listen_msg.encode())
    connect_msg = f'Side {other_side} connecting to port {port}'
    print(connect_msg)
    send_with_size(other_sock, connect_msg.encode())

    byte_data = b''

    while byte_data == b'':
        byte_data = recv_by_size(other_sock)
    data = byte_data.decode()
    byte_data = b''

    if data == "exit":
        return None, None

    print(f"Side {other_side}: " + data)
    disconnect_msg = f'Side {other_side} disconnected'
    print(disconnect_msg)
    send_with_size(other_sock, disconnect_msg.encode())

    while byte_data == b'':
        byte_data = recv_by_size(other_sock)
    data = byte_data.decode()

    sock.close()

    return addr[0], int(data)


def handle_connect(addr, port):
    sock = socket.socket()
    sock.connect((addr, port))

    print(recv_by_size(sock).decode())
    print(recv_by_size(sock).decode())

    msg = input("Enter a message >>> ")

    send_with_size(sock, msg.encode())
    if msg == "exit":
        return None

    print(recv_by_size(sock).decode())

    while True:
        ret_port = input("Choose a port >>> ")
        if ret_port.isnumeric():
            break

    send_with_size(sock, str(ret_port).encode())

    sock.close()
    return int(ret_port)
