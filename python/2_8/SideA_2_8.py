__author__ = 'Yoshi'

# 2.6  client server October 2021
import socket


from tcp_by_size import send_with_size, recv_by_size
from listen_and_connect import handle_connect, handle_listen


def main():
    port = 8111

    while True:
        a_sock = socket.socket()
        a_sock.bind(('0.0.0.0', port))
        a_sock.listen(2)
        # next line release the port
        a_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        b_sock, addr = a_sock.accept()

        listen_msg = f'Side A listening to port {port}'
        print(listen_msg)
        send_with_size(b_sock, listen_msg.encode())

        port = int(handle_listen(b_sock, 'B'))

        a_sock.close()

        a_sock = socket.socket()
        a_sock.connect((addr, port))

        connect_msg = recv_by_size(b_sock).decode()
        print(connect_msg)

        to_send, port = handle_connect(a_sock)
        to_send += "~" + str(port)
        send_with_size(a_sock, to_send.encode())

        a_sock.close()

    print('Bye ..')


if __name__ == '__main__':
    main()
