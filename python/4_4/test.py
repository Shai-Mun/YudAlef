# Ex 4.4 - HTTP Server Shell
# Author: Barak Gonen
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

# TO DO: import modules
import socket
import os
from http.client import responses

from HttpProcs import http_recv, http_send

# TO DO: set constants
IP = '0.0.0.0'

PORT = 80
SOCKET_TIMEOUT = 0.5
FIXED_RESPONSE = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\nContent-Type: text/html; charset=ISO-8859-1\r\n\r\nhello"
OK_RESPONSE = 'HTTP/1.1 200 OK\r\n'
NOT_FOUND_RESPONSE = ('HTTP/1.1 404 Not Found\r\nContent-Length: 27\r\nContent-Type: text/html; charset=utf-8\r\n\r\n +'
                  '<h1>404 File Not Found</h1>')
ERROR_RESPONSE = ('HTTP/1.0 500 Internal Server Error\r\nContent-Length: 34\r\nContent-Type: text/html; charset=utf-8\r\n\r\n +'
                  '<h1>500 Internal Server Error</h1>')
EWOULDBLOCK = 10035


def get_file_data(filename):
    """ Get data from file """
    with open(filename, 'rb') as f:
        return f.read()


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TO DO : add code that given a resource (URL and parameters) generates the proper response

    url = './'
    if resource == '':
        url += 'index.html'
    else:
        url += resource

    filename = url

    """""
    # TO DO: check if URL had been redirected, not available or other error code. For example:
    if url in REDIRECTION_DICTIONARY:
        # TO DO: send 302 redirection response
    """""

    if os.path.isfile(filename):
        http_header = ''

        file_type = url.split(".")[url.count(".")]
        match file_type:
            case "txt" | "html":
                http_header = 'Content-Type: text/html; charset=utf-8'
            case "jpg":
                http_header = 'Content-Type: image/jpeg'
            case "js":
                http_header = 'Content-Type: text/javascript; charset=UTF-8'
            case "css":
                http_header = 'Content-Type: text/css'
            case "ico":
                http_header = 'Content-Type: image/x-icon'
        http_header += '\r\n'
        data = get_file_data(filename)
        http_send(client_socket, OK_RESPONSE, http_header, data)
    else:
        client_socket.send(NOT_FOUND_RESPONSE.encode())



def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    method, resource, req = request.split()
    if method == "GET" and req == "HTTP/1.1":
        return True, resource[1:]
    else:
        return False, ''


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')

    while True:
        try:
            client_request, headers, body = http_recv(client_socket)
            print(f"#:----{client_request}\n----headers:{headers}\n----Body:{body}")

            valid_http, resource = validate_http_request(client_request)
            if valid_http:
                print('Got a valid HTTP request')
                handle_client_request(resource, client_socket)

            else:
                print('Error: Not a valid HTTP request')
                client_socket.send(ERROR_RESPONSE.encode())
                break
        except socket.error as err:
            if err.errno == EWOULDBLOCK or str(err) == "timed out":  # if we use conn.set timeout(x)
                continue
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()