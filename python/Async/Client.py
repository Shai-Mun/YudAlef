from sys import argv

import socket
import time

import threading

from tcp_by_size import send_with_size, recv_by_size

input_data = ""
user_num = 0
req_num = 0
close_thread = ""
to_send = ""
input_lock = threading.Lock()


class Input_thread(threading.Thread):
    """
    use global to indicate new command from user
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global input_data, req_num, to_send
        time.sleep(2)

        while not close_thread:

            input_lock.acquire()
            menu()
            input_data = input(">>>")

            if to_send == "":
                to_send = protocol_build_request(input_data)

            input_lock.release()
            time.sleep(0.2)  # prevent busy waiting


def handle_your_number(num):
    global user_num, req_num
    print("Your user number is " + num)
    user_num = num
    req_num = int(num) * 1000000


def handle_get_number(user_req):
    return protocol_build_request("3") + str(user_req) + "~"


def handle_reply(data):
    global to_send

    fields = data.split("~")
    code = fields[0]

    match code:
        case "URNM":
            handle_your_number(fields[1])

        case "WNUM":
            to_send = handle_get_number(fields[1])


def protocol_build_request(from_user):
    global req_num

    ret = ""
    match from_user:
        case "1":
            req_user = input("What is the user's num?\n")
            ret = "GNUM" + "~" + str(req_user) + "~" + str(req_num) + "~"

        case "2":
            ret = "GMAX" + "~" + str(req_num) + "~"

        case "3":
            num = input("What is your number? (100-999)\n")
            return "MNUM" + "~" + str(num) + "~"

    req_num += 1
    return ret


def menu():
    print("What do you want to do?")
    print("1. Ask another user for num")
    print("2. Ask for max num")


def main(ip):
    global input_data, close_thread, to_send

    cli_s = socket.socket()
    if not ip or len(ip) < 7:
        ip = "127.0.0.1"
    cli_s.connect((ip, 5050))

    cli_s.settimeout(0.3)

    close_thread = False
    input_t = Input_thread()
    input_t.start()

    while True:

        data = ""
        if input_data == "q":
            break
        if input_data != "" or to_send != "":

            # data = input_data
            #
            # input_lock.acquire()
            # input_data = ""
            # input_lock.release()

            # if to_send == "":
            #     to_send = protocol_build_request(data)
            if to_send != "":
                send_with_size(cli_s, bytearray(to_send,'utf8'))

            to_send = ""

        try:

            byte_data = recv_by_size(cli_s)
            data = byte_data.decode()
            if data == "":
                print("seems server DC")
                break
            print("Got data >>> " + data)
            handle_reply(data)


        except socket.error as err:

            if err.errno == 10035 or str(err) == "timed out":  # if we use conn.set timeout(x)
                continue
            if err.errno == 10054:
                # 'Connection reset by peer'
                print("Error %d Client is Gone. %s reset by peer." % (err.errno, str(cli_s)))
                break
            else:
                print("%d General Sock Error Client %s disconnected" % (err.errno, str(cli_s)))
                break

        except Exception as err:
            print("General Error:", err.message)
            break

    close_thread = True
    print("Press Enter for exit")
    cli_s.close()
    input_t.join()

    print("Bye Bye")


if __name__ == "__main__":
    if len(argv) < 3:
        addr = "127.0.0.1"
        main(addr)

        # print( "you must enter <IP> <username>")
        # exit()
    else:
        addr = argv[1]
        main(addr)
