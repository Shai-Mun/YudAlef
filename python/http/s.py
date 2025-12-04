import socket


def http_recv(sock: socket.socket):
    data = b''
    recv_byte = b' '

    while recv_byte:
        recv_byte = sock.recv(1)
        if b'\r\n\r\n' in data:
            break
        elif recv_byte == b'':
            return None, None, None

        data += recv_byte

    end_pos = data.find(b'\r\n')
    first_line = data[:end_pos].decode().split()
    headers_list = data[end_pos+2::len(data)-4].split(b'\r\n')
    if headers_list is None:
        return first_line, {}, b''

    headers = {}
    for h in headers_list:
        headers[h.split(b': ')[0].lower().strip()] = h.split(b': ')[1]

    body_length = -1
    body = b''
    if b'content-length' in headers:
        body_length = int(headers[b'content-length'])

        while len(body) < body_length:
            body += sock.recv(body_length - len(body))

        return first_line, headers, body


def main():
    s = socket.socket()
    s.bind(("0.0.0.0", 8001))
    s.listen(3)
    print("Listening...")
    cli, addr = s.accept()
    print("New Client")
    request_cnt = 1
    while True:
        request, headers, body = http_recv(cli)
        print("------------------------------------------ ", request_cnt)
        if request == b'':
            print("Client disconnected")
            break
        all_data = f"#:{request_cnt}\n----{request}\n----headers:{headers}\n----Body:{body}"
        print(all_data)
        resource = request.split()[1]
        if resource == '/':
            html = (f'<html><head><title>My Site</title></head>'
                    f'<body>Got Default Request<br/>') + all_data
        elif resource == "/favicon.ico" :
            html = (f'<html><head><title>My Site</title></head>'
                    f'<body>Favicon Request:<br/>') + all_data
        else:
            html = f'<html><head><title>My Site</title></head><body>Else:<br/> ' + all_data
        response = (f'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8' +
                    f'f\r\nContent-Length: {str(len(html))}\r\n\r\n').encode() + html.encode()
        cli.send(response)
        if request.split()[2].strip().lower() == "http/1.0" or headers.get('connection', '') == 'close':
            break
        request_cnt += 1


if __name__ == '__main__':
    main()

#http://127.0.0.1:8001/