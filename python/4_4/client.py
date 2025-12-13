import socket
import os
from HttpProcs import http_recv, http_send


def main():
    # CLIENT SIDE:
    ip = "127.0.0.1"
    port = 80
    try:
        s = socket.socket()
        s.connect((ip, port))
        print(f'Connect succeeded {ip}:{port}')

        with open('ClientFiles/test-image.jpg', 'rb') as f:
            data = f.read()

        f_line = 'POST /upload HTTP/1.1\r\n'
        headers = 'file-name: test-image.jpg\r\n'
        http_send(s, f_line, headers, data)
        print(http_recv(s))

        s = socket.socket()
        s.connect((ip, port))
        f_line = 'GET /image?image-name=test-image.jpg HTTP/1.1\r\n'
        http_send(s, f_line, '', '')
        request, headers, body = http_recv(s)
        with open('./ClientFiles/test2.jpg', 'wb') as f2:
            f2.write(body)

        s = socket.socket()
        s.connect((ip, port))
        f_line = 'GET /ClientFiles/test2.jpg HTTP/1.1\r\n'
        http_send(s, f_line, '', '')
        print(http_recv(s))

        s = socket.socket()
        s.connect((ip, port))
        f_line = 'GET /imgs/moved.jpg HTTP/1.1\r\n'
        http_send(s, f_line, '', '')
        print(http_recv(s))

    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')



if __name__ == '__main__':
    main()