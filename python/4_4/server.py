import socket
import os
from HttpProcs import http_recv, http_send

OK_RESPONSE = 'HTTP/1.1 200 OK\r\n'
NOT_FOUND_RESPONSE = ('HTTP/1.1 404 Not Found\r\nContent-Length: 27\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' +
                  '<h1>404 File Not Found</h1>')
ERROR_RESPONSE = ('HTTP/1.1 500 Internal Server Error\r\nContent-Length: 34\r\nContent-Type: text/html; charset=utf-8\r\n\r\n' +
                  '<h1>500 Internal Server Error</h1>')

def main():
    # SERVER SIDE:
    s = socket.socket()
    s.bind(("0.0.0.0", 80))
    s.listen(3)
    print("Listening...")
    cli, addr = s.accept()
    print("New Client")
    request_cnt = 1

    while True:
        request, headers, body = http_recv(cli)
        print("------------------------------------------ ", request_cnt)
        # if not request:
        #     print("Client disconnected")
        #     break


        all_data = f"#:{request_cnt}\n----{request}\n----headers:{headers}\n----Body:{body}"
        print(all_data)

        method, resource, req = request.split()

        if method == "GET" and req == "HTTP/1.1":

            if resource == '/':
                resource = '/index.html'
            filename = '.' + resource

            if '/calculate-next' in resource:
                num = int(resource.split("=")[1])
                html = f'<h1>{num}</h1>'
                cli.send(f'HTTP/1.1 200 OK\r\nContent-Length: {len(str(html))}]\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'.encode() + html.encode())

            elif os.path.isfile(filename):
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
                resp_headers += '\r\n'
                http_send(cli, OK_RESPONSE, resp_headers, data)
            else:
                cli.send(NOT_FOUND_RESPONSE.encode())

        else:
            cli.send(ERROR_RESPONSE.encode())

        if request.split()[2].strip().lower() == "http/1.0" or headers.get('connection', '') == 'close':
            break
        request_cnt += 1


if __name__ == '__main__':
    main()