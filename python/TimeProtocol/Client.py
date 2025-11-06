import socket
import sys

def handle_reply(reply):
    handle_info = ""
    command = reply[:4]

    if command == "HOUR":
        handle_info = handle_hour(reply)
    elif command == "ERR_":
        handle_info = handle_err_(reply)
    return handle_info+"\n"


def handle_err_(reply):
    s = reply.split("~")
    cli_error = ""

    error = s[1]
    match int(error):
        case 1:
            cli_error = "Command doesn't exist."
        case 2:
            cli_error = "Invalid input."
        case 3:
            cli_error = "Place doesn't exist."
        case 4:
            cli_error = "I don't know the time."
        case 5:
            cli_error = "Connection ended unexpectedly."
        case 6:
            cli_error = "There is a problem with the geolocator."
    return cli_error

def handle_hour(reply):
    s = reply.split("~")
    cli_time = f"Your time is {s[1]}:{s[2]}:{s[3]}\n"
    return cli_time


sock = socket.socket()

ip = sys.argv[1]
port = 3001

sock.connect((ip, port))

print("Connected to server\n\n")
option = input("Options:\nEnter 1 to enter city name\nEnter exit to exit\n>")
data = ""

while option != "exit":
    if option == "1":
        data = "GTIM~" + input("Enter city name, first letter capital\n>")
    sock.send(data.encode())

    data = sock.recv(100).decode()
    if data == "":
        print("Server Disconnected")
        break

    info = handle_reply(data)
    print(info)

    option = input("Options:\nEnter 1 to enter city name\nEnter exit to exit\n>")
print("Disconnected from server")
sock.close()