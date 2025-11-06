__author__ = 'Yoshi'

import os
import random
# 2.6  client server October 2021
import socket
import subprocess
import threading
import time
import traceback
from datetime import datetime
import shutil
import pyautogui
import webbrowser

from tcp_by_size import send_with_size, recv_by_size

all_to_die = False  # global


def get_time():
    """return local time """
    return datetime.now().strftime('%H:%M:%S:%f')


def get_random():
    """return random 1-10 """
    return str(random.randint(1, 10))


def get_server_name():
    """return server name from os environment """
    return os.environ['COMPUTERNAME']


def get_server_dir(path):
    directory = ""

    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)

        if os.path.isfile(filepath):
            file_size = os.path.getsize(filepath)
            last_modified_time = os.path.getmtime(filepath)
            last_modified_time = datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')
            directory += f"{filename} | Size: {file_size} bytes | Last Modified: {last_modified_time}\n"
        elif os.path.isdir(filepath):
            last_modified_time = os.path.getmtime(filepath)
            last_modified_time = datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')
            directory += f"[DIR] {filename} | Last Modified: {last_modified_time}\n"

    return directory


global size
global f_path

def send_file(sock):
    global size, f_path

    chunk_size = 4096

    with open(f_path, 'rb') as f:
        data = f.read(chunk_size)
        while size > chunk_size:
            send_with_size(sock, ('RCHN' + '~' + str(size // chunk_size)).encode())
            send_with_size(sock, data)
            size -= chunk_size
            data = f.read(chunk_size)
        send_with_size(sock, ('SENT' + '~' + str(size // chunk_size)).encode())
        send_with_size(sock, data)


def protocol_build_reply(request):
    """
    Application Business Logic
    function dispatcher ! for each code will get to some function that handle specific request
    Handle client request and prepare the reply info
    string:return: reply
    """

    request_code = request[:4].decode()
    fields = ""
    if '~' in request.decode():
        fields = request.decode().split('~')

    global size
    global f_path

    match request_code:
        case 'TIME':
            reply = 'TIMR' + '~' + get_time()
        case 'RAND':
            reply = 'RNDR' + '~' + get_random()
        case 'WHOU':
            reply = 'WHOR' + '~' + get_server_name()
        case 'EXIT':
            reply = 'EXTR'
        case 'EXEC':
            reply = 'EXER'
        case 'SDIR':
            if os.path.exists(fields[1]) and os.path.isdir(fields[1]):
                reply = 'RDIR' + '~' + get_server_dir(fields[1])
            else:
                reply = 'ERRR~003~directory not found'

        case 'DELE':
            if not os.path.exists(fields[1]) or not os.path.isfile(fields[1]):
                reply = 'ERRR~004~file not found'
            else:
                try:
                    with open(fields[1], 'a'):
                        reply = 'DELR'
                except IOError:
                    reply = 'ERRR~005~file is in use'

        case 'COPY':
            if not os.path.exists(fields[1]) or not os.path.isfile(fields[1]):
                reply = 'ERRR~004~file not found'
            elif os.path.exists(fields[2]) and os.path.isdir(fields[2]):
                reply = 'COPR'
            else:
                reply = 'ERRR~003~directory not found'

        case 'SEND':
            if not os.path.exists(fields[1]) or not os.path.isfile(fields[1]):
                reply = 'ERRR~004~file not found'
            else:
                f_path = fields[1]
                size = os.path.getsize(f_path)
                reply = 'RCHN'

        case 'SCHN':
            reply = 'RCHN'

        case 'SESS':
            image = pyautogui.screenshot()
            image.save(r'F:\screen.jpg')
            f_path = fields[1]
            size = os.path.getsize(f_path)
            reply = 'SESR'

        case 'SLEP':
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

        case 'SRCH':
            url = "https://hertzog-hs.mashov.info/"
            webbrowser.open(url)
            reply = 'RSCH'

        case _:
            reply = 'ERRR~002~code not supported'
    return reply.encode(), request_code


def handle_request(request):
    """
    Handle client request
    tuple :return: return message to send to client and bool if to close the client socket
    """
    try:
        to_send, request_code = protocol_build_reply(request)

        fields = ""
        if '~' in request.decode():
            fields = request.decode().split('~')

        match request_code:
            case 'EXIT':
                return to_send, True
            case 'EXEC':
                subprocess.call(r'%s' % fields[1])
            case 'DELE':
                if to_send[:4].decode() == 'DELR':
                    try:
                        os.remove(fields[1])
                    except PermissionError:
                        to_send = "ERRR~006~no permission to delete".encode()
            case 'COPY':
                shutil.copy(fields[1], fields[2])

    except Exception:
        print(traceback.format_exc())
        to_send = b'ERRR~001~General error'
    return to_send, False


def handle_client(sock, tid, addr):
    """
    Main client thread loop (in the server),
    :param sock: client socket
    :param tid: thread number
    :param addr: client ip + reply port
    :return: void
    """
    global all_to_die

    finish = False
    print(f'New Client number {tid} from {addr}')
    while not finish:
        if all_to_die:
            print('will close due to main server issue')
            break
        try:
            byte_data = recv_by_size(sock)  # todo improve it to recv by message size
            if byte_data == b'':
                print('Seems client disconnected')
                break
            to_send, finish = handle_request(byte_data)
            if to_send != '':
                if to_send[:4].decode() == 'RCHN' or to_send[:4].decode() == 'SESR':
                    send_file(sock)
                else:
                    send_with_size(sock, to_send)
            if finish:
                time.sleep(1)
                break
        except socket.error as err:
            print(f'Socket Error exit client loop: err:  {err}')
            break
        except Exception as err:
            print(f'General Error %s exit client loop: {err}')
            print(traceback.format_exc())
            break

    print(f'Client {tid} Exit')
    sock.close()


def main():
    global all_to_die
    """
    main server loop
    1. accept tcp connection
    2. create thread for each connected new client
    3. wait for all threads
    4. every X clients limit will exit
    """
    threads = []
    srv_sock = socket.socket()

    srv_sock.bind(('0.0.0.0', 1233))

    srv_sock.listen(20)

    #next line release the port
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    i = 1
    while True:
        print('\nMain thread: before accepting ...')
        cli_sock, addr = srv_sock.accept()
        t = threading.Thread(target=handle_client, args=(cli_sock, str(i), addr))
        t.start()
        i += 1
        threads.append(t)
        if i > 100000000:     # for tests change it to 4
            print('\nMain thread: going down for maintenance')
            break

    all_to_die = True
    print('Main thread: waiting to all clients to die')
    for t in threads:
        t.join()
    srv_sock.close()
    print('Bye ..')


if __name__ == '__main__':
    main()
