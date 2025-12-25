import socket
import datetime
import threading

LOCK = threading.Lock()


class MailInfo:
    def __init__(self):
        self.Messages = {}

    def add_user(self, user):
        self.Messages[user] = ""

    def get_mails(self, user):
        ret = self.Messages[user]
        LOCK.acquire()
        self.Messages[user] = ""
        LOCK.release()
        return ret

    def send_mail(self, user, msg):
        LOCK.acquire()
        self.Messages[user] += msg
        LOCK.release()


Users = {}
Mails = MailInfo()
DEBUG = True
all_to_die = False


def logging(user, direction, data):
    with open('./YAMailLogServer.txt', 'r') as f:
        file_data = f.read()
    with open('./YAMailLogServer.txt', 'w') as f:
        f.write(file_data)

        if user == "start":
            f.write("\r\n---\r\n")
        else:
            time = datetime.datetime.now().strftime('%Y%m%d %H:%M:%S')
            f.write(f"{time} {user} {direction} {data}\r")


def handle_client(s: socket.socket, num, size=4096):
    global all_to_die
    print("User " + num + " connected")
    s.send("HELLO###".encode())

    user_name = ""

    try:
        while True:

            if all_to_die:
                break

            data = ""
            while "###" not in data:
                data += s.recv(size).decode()

            if data == b'':
                break

            method = data[:5]
            to_send = ""

            match method:
                case "OLLEH":
                    user_name, password = data[6:len(data)-3].split("#")
                    if user_name not in Users or Users[user_name] != password:
                        logging('invalid login info', '', '')
                        break

                    new_mails = str(Mails.get_mails(user_name))
                    if new_mails != "":
                        to_send = "TKALL#NUM:" + str(new_mails.count("FROM")) + new_mails + "###"
                    else:
                        to_send = "NOPND###"

                case "MALTO":
                    time, to, sub, body = data[6:len(data) - 3].split("#")
                    to = to.split(":")
                    if body == "":
                        body = " "
                    else:
                        body = body.replace('#', '!')
                    for u in to[1:]:
                        if u in Users:
                            Mails.send_mail(u, f"#FROM:{user_name}#{time}#{sub}#{body}")
                    to_send = "GOTIT###"

                case "B_Y_E":
                    break

            s.send(to_send.encode())
            if DEBUG:
                logging(user_name, 'sent', data)
                logging(user_name, 'recv', to_send)
    except:
        print("An error occurred")
    print("User " + num + " disconnected")
    s.close()


def main():
    global all_to_die

    with open('./Files/YAMail_users.txt', 'rb') as f:
        line = " "
        while line:
            line = f.readline().decode()
            if line:
                name, password = line[5:].split("-")
                Users[name] = password[:password.find('\r\n')]
                Mails.add_user(name)

    srv_sock = socket.socket()

    ip = "0.0.0.0"
    port = 587
    srv_sock.bind((ip, port))
    srv_sock.listen(20)

    threads = []
    i = 1
    if DEBUG:
        logging('start', 'start', 'start')

    while i < 13:
        cli, addr = srv_sock.accept()
        t = threading.Thread(target=handle_client, args=(cli, str(i)))
        t.start()
        threads.append(t)
        i += 1

    all_to_die = True
    for t in threads:
        t.join()

    srv_sock.close()


if __name__ == "__main__":
    main()
# YAMailClient.exe Shai 127.0.0.1 Alice 11
