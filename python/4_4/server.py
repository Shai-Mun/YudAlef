import socket
import os
from HttpProcs import http_recv, http_send

OK_RESPONSE = 'HTTP/1.1 200 OK\r\n'
NOT_FOUND_RESPONSE = ('HTTP/1.1 404 Not Found\r\nContent-Length: 27\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' +
                      '<h1>404 File Not Found</h1>')
ERROR_RESPONSE = ('HTTP/1.1 500 Internal Server Error\r\nContent-Length: 34\r\n' +
                  'Content-Type: text/html; charset=utf-8\r\n\r\n<h1>500 Internal Server Error</h1>')
PERMS_RESPONSE = ('HTTP/1.1 403 Forbidden\r\nContent-Length: 22\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' +
                  '<h1>403 Forbidden</h1>')
UPLOAD_RESPONSE = ('HTTP/1.1 200 OK\r\nContent-Length: 22\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' +
                   '<h1>File Uploaded</h1>')
HTML_RESPONSE = 'HTTP/1.1 200 OK\r\nContent-Length: r1\r\nContent-Type: text/html; charset=utf-8\r\n\r\nr2'
MOVED_RESPONSE = ('HTTP/1.1 302 Moved Temporarily\r\nContent-Length: 22\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' +
                   '<h1>File moved to r1</h1>')
VALID_PERM = ['/css', '/imgs', '/js', '/index.html', '/uploads']
MOVED_FILES = {'./imgs/moved.jpg': './ClientFiles/test-image.jpg'}

def main():
    # SERVER SIDE:
    s = socket.socket()
    s.bind(("127.0.0.1", 80))

    request_cnt = 1
    s.listen(20)
    print("Listening...")

    while True:
        cli, addr = s.accept()
        print(f"New Client Connected")

        request, headers, body = http_recv(cli)
        print("------------------------------------------ ", request_cnt)
        if not request:
            print("Client disconnected")
            cli.close()
            break

        all_data = f"#:{request_cnt}\n----{request}\n----headers:{headers}\n----Body:{body}"
        print(all_data)

        method, resource, req = request.split()

        if resource == '/':
            resource = '/index.html'
        filename = '.' + resource
        params = resource[resource.find("?") + 1:]

        if method == "GET" and (req == "HTTP/1.1" or req == "HTTP/1.0"):

            if '/image' in resource:
                filename = './uploads/' + params.split("=")[1]
                resource = filename[1:]

            if '/calculate-next' in resource:
                num = int(params.split("=")[1])
                html = f'<h1>{num+1}</h1>'
                cli.send(HTML_RESPONSE.replace('r1', str(len(str(html)))).replace('r2', str(html)).encode())

            elif '/calculate-area' in resource:
                num1, num2 = (float(x[str(x).find("=")+1:]) for x in params.split("&"))
                html = f'<h1>{(num1*num2)/2}</h1>'
                cli.send(HTML_RESPONSE.replace('r1', str(len(str(html)))).replace('r2', str(html)).encode())


            elif os.path.isfile(filename):
                if filename in MOVED_FILES:
                    cli.send(MOVED_RESPONSE.replace('r1', str(MOVED_FILES[filename])).encode())

                elif resource[:resource[1:].find("/")+1] in VALID_PERM or resource in VALID_PERM:

                    with open(filename, 'rb') as f:
                        data = f.read()
                    file_type = filename.split(".")[filename.count(".")]
                    resp_headers = ''
                    match file_type:
                        case "txt" | "html":
                            resp_headers = 'Content-Type: text/html; charset=utf-8'
                        case "jpg":
                            resp_headers = 'Content-Type: image/jpeg'
                        case "js":
                            resp_headers = 'Content-Type: text/javascript; charset=UTF-8'
                        case "css":
                            resp_headers = 'Content-Type: text/css'
                        case "ico":
                            resp_headers = 'Content-Type: image/x-icon'
                        case "gif":
                            resp_headers = 'Content-Type: image/gif'
                    resp_headers += '\r\n'
                    http_send(cli, OK_RESPONSE, resp_headers, data)

                else:
                    cli.send(PERMS_RESPONSE.encode())

            else:
                cli.send(NOT_FOUND_RESPONSE.encode())

        elif method == "POST" and req == "HTTP/1.1":

            if '/upload' in resource:
                upload_name = headers[b'file-name']

                with open(f'./uploads/{upload_name.decode()}', 'wb') as f:
                    f.write(body)
                cli.send(UPLOAD_RESPONSE.encode())

        else:
            cli.send(ERROR_RESPONSE.encode())

        request_cnt += 1

        if req == "HTTP/1.0":
            cli.close()
            break



if __name__ == '__main__':
    main()
