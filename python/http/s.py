import socket
import webbrowser


def http_recv(sock: socket.socket, size=8192):
    data = b''
    recv_byte = b' '
    rnrn_pos = -1

    while rnrn_pos == -1:
        recv_byte = sock.recv(size)
        if recv_byte == b'':
            return None, None, None
        data += recv_byte
        rnrn_pos = data.find(b'\r\n\r\n')

    headers_list = data[:rnrn_pos-4].split(b'\r\n')
    first_line = headers_list[0].decode()

    if len(headers_list) < 2:
        return first_line, {}, b''

    headers = {}
    for h in headers_list[1:]:
        headers[h.split(b': ')[0].lower().strip()] = h.split(b': ')[1]

    body_length = -1
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
    if len(body) != 0:
        to_send += 'Content-Length: ' + str(len(body))
    to_send += '\r\n'
    to_send = to_send.encode() + body

    sock.send(to_send)


def open_by_webbrowser(body):
    if not body:
        return
    fn = "temp.html"
    with open(fn, 'wb') as f:
        f.write(body)
    webbrowser.open(fn)


def main():
    d = {"1": "/stories/", "2": "/history/", "3": "/support/", "4": "/computers/"}
    server = 'textfiles.com'
    answer_cnt = 1
    request = "GET / HTTP/1.0\r\n"
    request_headers = f'Host: {server}\r\nConnection: close\r\n'
    while True:
        cli_sock = socket.socket()
        cli_sock.connect((server, 80))
        print("Connected")
        http_send(cli_sock, request, request_headers, b'')
        reply, headers, body = http_recv(cli_sock)
        print("---------------- GOT AS CLIENT")
        reply_data = f"Answer#:{answer_cnt}\n----{reply}\n----headers:{headers}\n----Body:{body}"
        print(reply_data)
        open_by_webbrowser(body)
        answer_cnt += 1
        print("".join([f"\n{k}. {v}" for k, v in d.items()]))
        resource = d.get(input("type your request>\n"), "1")
        request = f'GET {resource} HTTP/1.0\r\n'
        cli_sock.close()

    # CLIENT SIDE
    # cli = socket.socket()
    # port = 80
    # ip = 'textfiles.com'
    # try:
    #     cli.connect((ip, port))
    #     print(f'Connect succeeded {ip}:{port}')
    # except:
    #     print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')
    #
    # cli.send("POST / HTTP/1.0\r\n\r\n".encode())
    # cli.close()
    # cli = socket.socket()
    # try:
    #     cli.connect((ip, port))
    #     print(f'Connect succeeded {ip}:{port}')
    # except:
    #     print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')
    #
    # cli.send("GET /stories/ HTTP/1.0\r\n\r\n".encode())

    # SERVER SIDE:
    # s = socket.socket()
    # s.bind(("0.0.0.0", 8001))
    # s.listen(3)
    # print("Listening...")
    # cli, addr = s.accept()
    # print("New Client")
    # request_cnt = 1
    #
    # while True:
    #     request, headers, body = http_recv(cli)
    #     print("------------------------------------------ ", request_cnt)
    #     if request == b'':
    #         print("Client disconnected")
    #         break
    #     all_data = f"#:{request_cnt}\n----{request}\n----headers:{headers}\n----Body:{body}"
    #     print(all_data)
    #     resource = request.split()[1]
    #     if resource == '/':
    #         html = (f'<html><head><title>My Site</title></head>'
    #                 f'<body>Got Default Request<br/>') + all_data
    #     elif resource == "/favicon.ico":
    #         html = (f'<html><head><title>My Site</title></head>'
    #                 f'<body>Favicon Request:<br/>') + all_data
    #     else:
    #         html = f'<html><head><title>My Site</title></head><body>Else:<br/> ' + all_data
    #     response = (f'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8' +
    #                 f'f\r\nContent-Length: {str(len(html))}\r\n\r\n').encode() + html.encode()
    #     cli.send(response)
    #     if request.split()[2].strip().lower() == "http/1.0" or headers.get('connection', '') == 'close':
    #         break
    #     request_cnt += 1


if __name__ == '__main__':
    main()

#http://127.0.0.1:8001/