import random
import threading
import socket
import traceback

from Player import User
from db import Database
import smtplib
import time
from email.message import EmailMessage

from enc_utils import send_with_size, recv_by_size, dph_serv, rsa_serv

all_to_die = False
db = Database()
temp = {}
active_lobbies = {}  # Format: {host_username: guest_username_or_None}
lobbies_lock = threading.Lock()

online_users      = {}   # {username: (sock, encryption_key)}
online_users_lock = threading.Lock()

pub_keys      = {}   # {username: b64_pem}  — persists even when user is offline
pub_keys_lock = threading.Lock()


def broadcast(message: str, exclude: str = None):
    with online_users_lock:
        for uname, (s, key) in list(online_users.items()):
            if uname == exclude:
                continue
            try:
                send_with_size(s, message.encode(), key)
            except Exception:
                pass


def send_verification_email(dest_email, code):
    sender_email = "yudalephcyber@gmail.com"
    app_password = "ojzz nize xqlo rpyn"
    msg = EmailMessage()
    msg['Subject'] = "Your Verification Code"
    msg['From'] = sender_email
    msg['To'] = dest_email
    msg.set_content(f"Hi! Your secure code is: {code}\nThis code is valid for 5 minutes.")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        return time.time()
    except Exception as e:
        print(f"Error sending email: {e}")
        return time.time()


def handle_request(data, current_user=None):
    action = data.decode().split("~")[0]
    fields = data.decode().split("~")[1:]
    reply = ""
    logged_in_user = None
    # don't log full PEM / encrypted payloads
    print(action, fields[:2])

    match action:
        case "SIGNUP":
            username = fields[0]
            if username in db.users.keys():
                reply = "ERRORX~005~username already exist"
            else:
                c = random.randint(100000, 999999)
                print(c)
                t = send_verification_email(fields[2], c)
                salt, hashed_password = User.hash_salt_passwd(fields[1])
                u = User(username, fields[2])
                u.hashed_password = hashed_password
                u.salt = salt
                temp[username] = {"user": u, "code": c, "time": t}
                reply = "SIGNOK~Enter code"

        case "VERIFY1" | "VERIFY2":
            username = fields[0]
            c = fields[1]
            print(c)
            if (int(temp[username]["code"]) == int(c) and
                    int(time.time()) - int(temp[username]["time"]) < 300):
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
            print(db.users.keys())
            if username in db.users.keys():
                db_hashed = db.users[username].hashed_password
                db_salt   = db.users[username].salt
                _, hashed_password = User.hash_salt_passwd(password, db_salt)
                if hashed_password == db_hashed:
                    reply = f"LOG_OK~welcome {db.users[username].username}"
                    logged_in_user = username
                else:
                    reply = "LOG_FAIL~Wrong password"
            else:
                reply = "LOG_FAIL~User not found"

        case "FORGOT":
            username = fields[0]
            c = random.randint(100000, 999999)
            print(c)
            t = send_verification_email(fields[1], c)
            temp[username] = {"pass": fields[2], "code": c, "time": t}

        case "PUB_KEY":
            # Store and broadcast this user's public key
            # fields[0]=username, fields[1]=b64_pem
            username = fields[0]
            b64_pem  = fields[1]
            with pub_keys_lock:
                pub_keys[username] = b64_pem
            broadcast(f"PUB_KEY~{username}~{b64_pem}", exclude=username)
            print(f"[PUB_KEY] Stored and broadcast key for {username}")

        case "SESSION_INIT":
            # Route the RSA-encrypted AES key blindly — server never sees the key
            # fields[0]=to_username, fields[1]=rsa_encrypted_aes_key_hex
            to_user = fields[0]
            enc_key_hex = fields[1]
            with online_users_lock:
                if to_user in online_users:
                    s, key = online_users[to_user]
                    try:
                        send_with_size(s,
                                       f"SESSION_INIT~{current_user}~{enc_key_hex}".encode(),
                                       key)
                    except Exception:
                        print(f"Failed to route SESSION_INIT to {to_user}")
                else:
                    reply = f"MSG_FAIL~{to_user} is not online"

        # Also update PRIV_MSG to forward iv_hex too — fields are now [to, iv_hex, ct_hex]
        case "PRIV_MSG":
            to_user = fields[0]
            iv_hex = fields[1]
            ct_hex = fields[2]
            with online_users_lock:
                if to_user in online_users:
                    s, key = online_users[to_user]
                    try:
                        send_with_size(s,
                                       f"PRIV_MSG~{current_user}~{iv_hex}~{ct_hex}".encode(),
                                       key)
                    except Exception:
                        print(f"Failed to route PRIV_MSG to {to_user}")
                else:
                    reply = f"MSG_FAIL~{to_user} is not online"

        case "CREATE_LOBBY":
            with lobbies_lock:
                if current_user not in active_lobbies:
                    active_lobbies[current_user] = None  # None means waiting for guest

                # Broadcast updated list to everyone
            with lobbies_lock:
                open_rooms = [host for host, guest in active_lobbies.items() if guest is None]
            broadcast(f"LOBBY_LIST~{'~'.join(open_rooms)}")

        case "GET_LOBBIES":
            with lobbies_lock:
                open_rooms = [host for host, guest in active_lobbies.items() if guest is None]
            reply = f"LOBBY_LIST~{'~'.join(open_rooms)}"

        case "JOIN_LOBBY":
            target_host = fields[0]

            with lobbies_lock:
                if target_host in active_lobbies and active_lobbies[target_host] is None:
                    active_lobbies[target_host] = current_user  # Lock the room

                    # Find both sockets and trigger the game launch
                    with online_users_lock:
                        if target_host in online_users and current_user in online_users:
                            host_sock, host_key = online_users[target_host]
                            guest_sock, guest_key = online_users[current_user]

                            # Alert Host (Assign P1)
                            send_with_size(host_sock, f"START_GAME~{current_user}~P1".encode(), host_key)
                            # Alert Guest (Assign P2)
                            send_with_size(guest_sock, f"START_GAME~{target_host}~P2".encode(), guest_key)

            # Broadcast updated lobbies to hide the filled room
            with lobbies_lock:
                open_rooms = [host for host, guest in active_lobbies.items() if guest is None]
            broadcast(f"LOBBY_LIST~{'~'.join(open_rooms)}")

        case "GAME_ACTION":
            # fields[0] is the sub-action (e.g., PLACE_MONKEY)
            # Find who the opponent is in your active_lobbies dictionary
            opponent = None
            with lobbies_lock:
                if current_user in active_lobbies:
                    opponent = active_lobbies[current_user]  # current_user is host, guest is opponent
                else:
                    # current_user might be the guest, search for the host
                    for host, guest in active_lobbies.items():
                        if guest == current_user:
                            opponent = host
                            break

            # Forward the action string cleanly to the opponent's socket
            if opponent:
                with online_users_lock:
                    if opponent in online_users:
                        opp_sock, opp_key = online_users[opponent]
                        # Re-wrap the remaining fields back together
                        action_payload = "~".join(fields)
                        try:
                            send_with_size(opp_sock, action_payload.encode(), opp_key)
                        except Exception:
                            print(f"Failed to relay game data to {opponent}")


    return reply, logged_in_user


def handle_client(sock, tid, addr):
    global all_to_die
    print(f'New Client number {tid} from {addr}')
    current_user = None

    encryption_key = ""
    enc_type = recv_by_size(sock).decode()
    if enc_type == "DPH":
        encryption_key = dph_serv(sock)
    elif enc_type == "RSA":
        encryption_key = rsa_serv(sock)

    while not all_to_die:
        try:
            byte_data = recv_by_size(sock, encryption_key)
            if byte_data == b'':
                print('Seems client disconnected')
                break

            to_send, logged_in_user = handle_request(byte_data, current_user)

            if logged_in_user:
                current_user = logged_in_user
                with online_users_lock:
                    online_users[current_user] = (sock, encryption_key)
                    user_list = "U_LIST~" + "~".join(online_users.keys())
                    send_with_size(sock, user_list.encode(), encryption_key)
                broadcast(f"U_JOIN~{current_user}", exclude=current_user)

                # Send all known public keys to the newcomer
                with pub_keys_lock:
                    for uname, b64_pem in pub_keys.items():
                        if uname != current_user:
                            send_with_size(sock,
                                           f"PUB_KEY~{uname}~{b64_pem}".encode(),
                                           encryption_key)

            if to_send:
                send_with_size(sock, to_send.encode(), encryption_key)

        except socket.error as err:
            print(f'Socket Error: {err}')
            break
        except Exception as err:
            print(f'General Error: {err}')
            print(traceback.format_exc())
            break

    if current_user:
        with online_users_lock:
            online_users.pop(current_user, None)
        # Clean up any lobby this user owned or was a guest in
        with lobbies_lock:
            if current_user in active_lobbies:
                del active_lobbies[current_user]
            else:
                for host, guest in list(active_lobbies.items()):
                    if guest == current_user:
                        del active_lobbies[host]
                        break
        broadcast(f"U_LEFT~{current_user}")
        print(f'{current_user} removed from online users')

    print(f'Client {tid} Exit')
    sock.close()


def main():
    global all_to_die
    threads  = []
    srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_sock.bind(('0.0.0.0', 5555))
    srv_sock.listen(20)
    srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    i = 1
    while True:
        print('\nMain thread: before accepting ...')
        cli_sock, addr = srv_sock.accept()
        t = threading.Thread(target=handle_client, args=(cli_sock, str(i), addr))
        t.start()
        i += 1
        threads.append(t)
        if i > 100000000:
            print('\nMain thread: going down for maintenance')
            break
    all_to_die = True
    for t in threads:
        t.join()
    srv_sock.close()
    print('Bye ..')


if __name__ == '__main__':
    main()