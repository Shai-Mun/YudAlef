import socket


def http_recv(sock: socket.socket):
    data = b''
    recv_byte = b' '
    headers_end_pos = -1

    while recv_byte:
        recv_byte = sock.recv(1)
        if recv_byte == b'':
            return '', '', b''

        headers_end_pos = data.find(b'\r\n\r\n')
        if headers_end_pos != -1:
            break

        data += recv_byte

    first_line_end_pos = data.find(b'\r\n')
    first_line = data[:first_line_end_pos].decode().split()
    headers_list = data[first_line_end_pos+2:].split(b'\r\n')
    if headers_list is None:
        return first_line, [], b''

    body_length = -1
    body = b''
    if b'Content-Length' in headers_list:
        for head in headers_list:
            if head.find(b'Content-Length') != -1:
                body_length = int(head.split(b': ')[1])

        if body_length != -1:
            while len(body) < body_length:
                body += sock.recv(body_length - len(body))

        return first_line, headers_list, body


s_sock = socket.socket()
s_sock.bind(('0.0.0.0', 1233))
s_sock.listen(2)
cli_sock, addr = s_sock.accept()
print("after accept")
while True:
    f_line, headers, b = http_recv(cli_sock)
    print(f_line)
    print(headers)
    print(b)
    html = f'<html><title>Shai</title><body>Your request is {str(headers)}</body></html>'

    cli_sock.send(f'HTTP/1.1 200 OK\r\nContent-Length: {str(len(html))}\r\n\r\n{html}'.encode())
