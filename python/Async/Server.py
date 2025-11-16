import socket
import time
import threading

from tcp_by_size import send_with_size, recv_by_size
from AsyncMessages import AsyncMessages

global async_msg

EWOULDBLOCK = 10035
user_dict = {}


def handle_gmax():
    temp_u = ""
    temp_n = -1

    for key in user_dict:
        if user_dict[key] > temp_n:
            temp_u = key
            temp_n = user_dict[key]

    return temp_u, temp_n


def handle_message(data, user):
    global async_msg

    to_send = ""
    fields = data.split("~")
    code = fields[0]

    match code:
        case "GNUM":
            to_user = fields[1]
            req_num = fields[2]
            async_msg.put_msg_by_user("WNUM" + "~" + str(req_num) + "~", to_user)

        case "MNUM":
            num = fields[1]
            to_user = str(int(fields[2]) // 1000000)
            user_dict[str(user)] = int(num)
            async_msg.put_msg_by_user("TNUM" + "~" + str(user) + "~" + str(num) + "~", to_user)

        case "GMAX":
            max_u, max_n = handle_gmax()
            to_send = "MAXR" + "~" + str(max_u) + "~" + str(max_n) + "~"

    return to_send


def handle_client(sock, tid):
    """
    main thread - recv handle and answer also push async msgs
    :param sock: socket
    :param tid: thread is
    :return:
    """
    global async_msg

    user_name = ""
    exit_thread = False

    print("New Client num " + str(tid))
    to_send = "URNM" + "~" + str(tid) + "~"
    send_with_size(sock, to_send.encode())
    async_msg.sock_by_user[str(tid)] = sock


    sock.settimeout(0.3)
    while not exit_thread:
        try:

            byte_data = recv_by_size(sock)
            data = byte_data.decode()
            if data == "":
                print("Error: Seems Client DC")
                break

            to_send = handle_message(data, tid)
            if to_send != "":
                send_with_size(sock, bytearray(to_send, 'utf8'))

        except socket.error as err:

            if err.errno == EWOULDBLOCK or str(err) == "timed out":  # if we use conn.set timeout(x)
                msgs = async_msg.get_async_messages_to_send(sock)
                for data in msgs:
                    send_with_size(sock, bytearray(data, 'utf8'))
                    time.sleep(0.1)
                continue

            if err.errno == 10054:
                # 'Connection reset by peer'
                print("Error %d Client is Gone.  reset by peer." % err.errno)
                break
            else:
                print("%d General Sock Error Client disconnected" % err.errno)
                break

        except Exception as err:
            print("General Error:", str(err))
            break
    async_msg.delete_socket(sock)
    sock.close()


def main():
    global async_msg

    s = socket.socket()

    async_msg = AsyncMessages()

    s.bind(("0.0.0.0", 5050))

    s.listen(4)
    print("after listen")

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    threads = []
    i = 1
    while True:
        cli_s, addr = s.accept()
        print("New Client")
        async_msg.add_new_socket(cli_s)

        t = threading.Thread(target=handle_client, args=(cli_s, i))
        t.start()
        i += 1
        threads.append(t)

        if i >= 100:
            break

    for t in threads:
        t.join()
    s.close()
    print("Bye ..")


if __name__ == "__main__":
    main()
