import socket

def http_recv(sock: socket.socket, size=8192):
    data = b''
    rnrn_pos = -1

    while rnrn_pos == -1:
        recv_byte = sock.recv(size)
        if recv_byte == b'':
            return None, None, None
        data += recv_byte
        rnrn_pos = data.find(b'\r\n\r\n')

    first_line = data[:data.find(b'\r\n')].decode("utf-8","ignore")

    headers_list = data[:rnrn_pos].split(b'\r\n')[1:]
    if len(headers_list) == 0:
        return first_line, {}, b''

    headers = {}
    for h in headers_list:
        headers[h.split(b': ')[0].lower().strip()] = h.split(b': ')[1]

    body = b''
    if b'content-length' in headers:
        body_length = int(headers[b'content-length'])

        body = data[rnrn_pos+4:]
        while len(body) < body_length:
            body += sock.recv(min(body_length - len(body), size))

    return first_line, headers, body


def http_send(sock: socket.socket, first_line, headers, body):
    to_send = first_line
    to_send += headers
    if type(body) is not bytes:
        body = body.encode()
    if len(body) != 0:
        to_send += 'Content-Length: ' + str(len(body)) + '\r\n'
    to_send += '\r\n'
    to_send = to_send.encode() + body

    sock.send(to_send)