import random
import threading
import socket
import traceback
from user import User
from db import Database
import smtplib
import time
from email.message import EmailMessage

from tcp_by_size import send_with_size, recv_by_size

all_to_die = False  # global
db = Database()
temp = {}

def send_verification_email(dest_email, code):
    """
    Sends a verification code to the given email and returns the send time.
    """
    # הגדרות שרת המייל (למשל Gmail)
    sender_email = "yudalephcyber@gmail.com"  # המייל שממנו תשלח
    app_password = "ojzz nize xqlo rpyn"  # סיסמת אפליקציה (App Password)

    # יצירת תוכן ההודעה
    msg = EmailMessage()
    msg['Subject'] = "Your Verification Code"
    msg['From'] = sender_email
    msg['To'] = dest_email
    msg.set_content(f"Hi! Your secure code is: {code}\nThis code is valid for 5 minutes.")

    try:
        # התחברות לשרת ושליחה
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)

        # החזרת זמן השליחה הנוכחי כפי שמתואר על הלוח
        return time.time()

    except Exception as e:
        print(f"Error sending email: {e}")
        return time.time()


def handle_request(data):
    action = data.decode().split("~")[0]
    fields = data.decode().split("~")[1:]
    reply = ""
    print(action, fields)
    match action:
        case "SIGNUP":
            username = fields[0]

            if username in db.users.keys():
                reply = "ERRORX~005~username already exist"
            else:
                c = random.randint(100000, 999999)
                print(c)
                t = send_verification_email(fields[4], c)

                salt, hashed_password = User.hash_salt_passwd(fields[1])
                u = User(username, fields[2], fields[3], fields[4], fields[5])
                u.hashed_password = hashed_password
                u.salt = salt

                temp[username] = {"user": u, "code": c, "time": t}

                reply = f"SIGNOK~Enter code"

        case "VERIFY1" | "VERIFY2":
            username = fields[0]
            c = fields[1]
            print(c)
            if int(temp[username]["code"]) == int(c) and int(time.time()) - int(temp[username]["time"]) < 300:
                if "1" in action:
                    db.add_user_to_db(temp[username]["user"])
                    reply = "VERFOK~Signup completed"

                elif "2" in action:
                    db.change_pass(username, temp[username]["pass"])
                    reply = "VEROK~Change password completed"
                del temp[username]



        case "LOG_IN":
            username = fields[0]
            password = fields[1]
            if username in db.users.keys():
                db_hashed = db.users[username].hashed_password
                db_salt = db.users[username].salt
                _, hashed_password = User.hash_salt_passwd(password, db_salt)

                if hashed_password == db_hashed:
                    reply = f"LOG_OK~welcome {db.users[username].fname} {db.users[username].lname}"
                else:
                    reply = "Not working"

        case "FORGOT":
            username = fields[0]

            c = random.randint(100000, 999999)
            print(c)
            t = send_verification_email(fields[1], c)

            temp[username] = {"pass": fields[2], "code": c, "time": t}

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
    with open('big_prime.txt', 'r') as f:
        p = int(f.read()[2:])
    g = 3  # alpha
    send_with_size(sock, f"{p},{g}".encode())

    x = random.randint(2, p - 2)
    a = pow(g, x, p)
    send_with_size(sock, str(a).encode())

    b = int(recv_by_size(sock).decode())

    k = pow(b, x, p)
    print(f"the key is: {k}")

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