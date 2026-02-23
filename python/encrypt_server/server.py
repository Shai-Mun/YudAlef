import threading
import socket
import traceback
from user import User
from tcp_by_size import send_with_size, recv_by_size

all_to_die = False  # global


def handle_request(data):
    action = data.decode().split("|")[0]
    fields = data.decode().split("|")[1:]
    match action:
        case "SIGNUP":
            username = fields[0]

            # if username in db.users.keys():
            #     reply = "ERRORX~005~username already exist"
            # else:
            salt, hashed_password = User.hash_salt_passwd(fields[1])
            u = User(username, fields[2], fields[3], fields[4], fields[5])
            u.hashed_password = hashed_password
            u.salt = salt
            print(u)
            # db.add_user_to_db(u)

        case "LOGIN":
            fields = data.decode().split("~")
            username = fields[1]
            password = fields[2]

            # if username in db.users.keys():
            #     db_hashed = db.users[username].hashed_password
            #     db_salt = db.users[username].salt
            #     _, hashed_password = User.hash_salt_passwd(password, db_salt)
            #
            #     if hashed_password == db_hashed:
            #         # Note: The line below is partially cut off in the image
            #         reply = f"LOG_OK~welcome {db.users[username].first_name} {db.users[username].last_name}"
    reply = "Testing"
    return reply


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
            to_send = handle_request(byte_data)
            if to_send != '':
                send_with_size(sock, to_send.encode())

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

    threads = []
    srv_sock = socket.socket()

    srv_sock.bind(('0.0.0.0', 5555))

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