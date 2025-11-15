from sys import argv

import socket
import time

import threading

from tcp_by_size import send_with_size, recv_by_size

input_data = ""
close_thread = ""
input_lock = threading.Lock()


class Input_thread(threading.Thread):
    """
    use global to indicate new command from user
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global input_data
        time.sleep(2)

        while not close_thread:

            input_lock.acquire()

            print("What do you want to do?\n")
            print("1. Ask another user for num")
            print("2. Ask for max num")
            num = input()

            match "num":
                case "1":
                    pass
                case "2":
                    pass

            input_data = input("What do you want to do?\n")

            input_lock.release()
            time.sleep(0.2)  # prevent busy waiting


def main(ip, num):
    global input_data, close_thread

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
        if input_data != "":
            data = input_data
            input_lock.acquire()
            input_data = ""
            input_lock.release()


        try:

            byte_data = recv_by_size(cli_s)
            data = byte_data.decode()
            if data == "":
                print("seems server DC")
                break
            print("Got data >>> " + data)
            fields = data.split("|")
            msg_type = data[:3]


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
        number = input("What is your number?\n")

        main(addr, number)

        # print( "you must enter <IP> <username>")
        # exit()
    else:
        addr = argv[1]
        number = argv[2]
        main(addr, number)
