import socket
import os
from HttpProcs import http_recv, http_send


def main():
    # CLIENT SIDE:
    ip = "127.0.0.1"
    port = 80
    s = socket.socket()
    try:
        s.connect((ip, port))
        print(f'Connect succeeded {ip}:{port}')

    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')



if __name__ == '__main__':
    main()