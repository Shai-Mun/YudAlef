__author__ = 'Yoshi'

# 2.6  client server October 2021
import socket


from tcp_by_size import send_with_size, recv_by_size
from listen_and_connect import handle_connect, handle_listen


def main():
    addr = "127.0.0.1"
    port = 8111

    while True:
        port = handle_connect(addr, port)
        if port is None:
            break

        addr, port = handle_listen(port, 'B', 'A')
        if addr is None:
            break

        addr = str(addr)
        port = int(port)


    print('Bye ..')


if __name__ == '__main__':
    main()
