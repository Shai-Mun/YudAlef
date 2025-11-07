import socket

from geopy.geocoders import ArcGIS
from datetime import datetime
import requests


def handle_message(request):
    handle_reply = ""
    command = request[:4]

    if command == "GTIM":
        handle_reply = handle_gtim(request)
    else:
        handle_reply = "ERR_~001"

    return handle_reply


def handle_gtim(request):
    s = request.split("~")

    geolocator = ArcGIS()

    if not s[1].replace(" ", "").isalpha():
        return "ERR_~002"

    try:
        location = geolocator.geocode(s[1])
    except:
        return "ERR_~006"
    if not location:
        return "ERR_~003"

    lat, lon = location.latitude, location.longitude

    url = f"https://timeapi.io/api/Time/current/coordinate?latitude={lat}&longitude={lon}"
    response = requests.get(url)
    if response.status_code != 200:
        return "ERR_~004"

    time_data = response.json()
    time_str = time_data.get("dateTime")

    dt = datetime.fromisoformat(time_str)
    return f"HOUR~{dt.hour}~{dt.minute}~{dt.second}"


srv_sock = socket.socket()
ip = '127.0.0.1'  # '192.168.68.115'
port = 3001
srv_sock.bind((ip, port))

srv_sock.listen(5)

while True:
    print("Waiting for a connection...")

    cli_sock, address = srv_sock.accept()
    print("Client connected\n\n")
    while True:
        reply = ""
        try:
            cli_sock.settimeout(5.0)
            data = cli_sock.recv(100).decode()

            if data == "":
                print("Client Disconnected")
                break

            reply = handle_message(data)

        except socket.timeout:
            print("Socket operation timed out!")

        option = input("Options:\nEnter 1 to send the client a message\nEnter exit to exit\n>")
        if option == "1":
            reply = "MESG~" + input("Enter a message:\n>")

        if reply != "":
            cli_sock.send(reply.encode())
        else:
            cli_sock.send("ERR_~005".encode())



    cli_sock.close()
