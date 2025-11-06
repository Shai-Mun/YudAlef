__author__ = 'Yossi'
# 2.6  client server October 2021

import socket
import sys
import traceback

from tcp_by_size import send_with_size, recv_by_size


def menu():
    """
    show client menu
    return: string with selection
    """
    print('\n  1. ask for time')
    print('\n  2. ask for random')
    print('\n  3. ask for name')
    print('\n  4. notify exit')
    print('\n  5. run a file in the server')
    print('\n  6. show a dir of the server')
    print('\n  7. delete a file in the server')
    print('\n  8. copy a file in the server')
    print('\n  9. send a file from the server to you')
    print('\n  10. send a screenshot the screen of the server')
    print('\n  (11. some invalid data for testing)')
    print('\n  12. make the pc sleep')
    print('\n  13. make the pc open Hertzog' + 's Google')


    return input('Input 1 - 13 > ')


global f_name

def protocol_build_request(from_user):
    """
    build the request according to user selection and protocol
    return: string - msg code
    """
    global f_name

    match from_user:
        case "1":
            return 'TIME'
        case "2":
            return 'RAND'
        case "3":
            return 'WHOU'
        case "4":
            return 'EXIT'
        case "5":
            return 'EXEC' + '~' + input("enter exe file path: ")
        case "6":
            return 'SDIR' + '~' + input("enter directory path: ")
        case "7":
            return 'DELE' + '~' + input("enter file path: ")
        case "8":
            return 'COPY' + '~' + input("enter from file path: ") + "~" + input("\nenter to file path: ")
        case "9":
            ret_string = 'SEND' + '~' + input("enter file path: ")
            f_name = input("enter file name: ")
            return ret_string

        case "10":
            f_name = input("enter file name: ")
            return 'SESS' + '~' + 'F:\screen.jpg'

        case "11":
            return input("enter free text data to send> ")

        case "12":
            return 'SLEP'

        case "13":
            return 'SRCH'

        case _:
            return ''


def receive_file(sock, code_message):
    global f_name

    with open(f_name, 'wb') as f:
        while True:
            if not code_message:
                break
            else:
                code_message = code_message[:4]
                if code_message == 'RCHN' or code_message == 'SENT':
                    bdata = recv_by_size(sock)
                    while True:
                        if b'RCHN' in bdata or b'SENT' in bdata:
                            break
                        f.write(bdata)
                        bdata = recv_by_size(sock)

                    code_message = bdata[:4].decode()
                    if code_message != 'SENT':
                        send_with_size(sock, 'SCHN'.encode())
                    else:
                        bdata = recv_by_size(sock)
                        while True:
                            if b'SENT' in bdata:
                                break
                            f.write(bdata)
                            bdata = recv_by_size(sock)
                        break


def protocol_parse_reply(reply):
    """
    parse the server reply and prepare it to user
    return: answer from server string
    """

    to_show = 'Invalid reply from server'
    try:
        reply = reply.decode()
        fields = ""
        if '~' in reply:
            fields = reply.split('~')
        code = reply[:4]
        match code:
            case 'TIMR':
                to_show = 'The Server time is: ' + fields[1]
            case 'RNDR':
                to_show = 'Server draw the number: ' + fields[1]
            case 'WHOR':
                to_show = 'Server name is: ' + fields[1]
            case 'ERRR':
                to_show = 'Server return an error: ' + fields[1] + ' ' + fields[2]
            case 'EXTR':
                to_show = 'Server acknowledged the exit message'
            case 'EXER':
                to_show = 'Server executed the file'
            case 'RDIR':
                to_show = 'The directory you wanted to see is:\n' + fields[1]
            case 'DELR':
                to_show = 'Server acknowledged the deletion request'
            case 'COPR':
                to_show = 'Server acknowledged the copying request'
            case 'SENT':
                to_show = 'Server sent the file'
            case 'RSCH':
                to_show = 'Server opened the website'

    except:
        print('Server replay bad format')
    return to_show


def handle_reply(reply):
    """
    get the tcp upcoming message and show reply information
    return: void
    """
    to_show = protocol_parse_reply(reply)
    if to_show != '':
        print('\n==========================================================')
        print (f'  SERVER Reply: {to_show}   |')
        print(  '==========================================================')


def main(ip):
    """
    main client - handle socket and main loop
    """
    connected = False

    sock = socket.socket()

    port = 1233
    try:
        sock.connect((ip,port))
        print(f'Connect succeeded {ip}:{port}')
        connected = True
    except:
        print(f'Error while trying to connect.  Check ip or port -- {ip}:{port}')

    while connected:
        from_user = menu()
        to_send = protocol_build_request(from_user)
        if to_send == '':
            print("Selection error try again")
            continue
        try:
            send_with_size(sock,to_send.encode())
            byte_data = recv_by_size(sock)
            if byte_data == b'':
                print('Seems server disconnected abnormal')
                break
            elif b'RCHN' in byte_data or b'SENT' in byte_data or b'SESR' in byte_data:
                receive_file(sock, byte_data.decode())
            else:
                handle_reply(byte_data)

            if from_user == '4':
                print('Will exit ...')
                connected = False
                break
        except socket.error as err:
            print(f'Got socket error: {err}')
            break
        except Exception as err:
            print(f'General error: {err}')
            print(traceback.format_exc())
            break
    print ('Bye')
    sock.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main('127.0.0.1')