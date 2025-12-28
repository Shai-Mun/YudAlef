import socket

DNS_SERVER_IP = '127.0.0.1'
DNS_SERVER_PORT = 53
DEFAULT_BUFFER_SIZE = 1024
dns_dict = {
    "www.shai1.co.il": '0.0.0.1',
    "www.shai2.co.il": '0.0.0.2',
    "www.shai3.co.il": '0.0.0.3',
    "www.shai4.co.il": '0.0.0.4',
    "www.shai5.co.il": '0.0.0.5'
}



# def dns_handler(data, address):
#
#
#

def dns_udp_server(ip, port):
    """
    Starts a UDP server on a given IP:PORT, and calls
    dns_handler(data, client_address)
    prototyped function on any client request data.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    print("Server started successfully! Waiting for data..")

    while True:
        try:
            data, addr = sock.recvfrom(DEFAULT_BUFFER_SIZE)
            # dns_handler(data, addr)
        except Exception as ex:
            print(f"Client exception! {str(ex)}")


def main():
    """
    Main execution point of the program.
    """
    print("Starting UDP server...")
    dns_udp_server(DNS_SERVER_IP, DNS_SERVER_PORT)


if __name__ == '__main__':
    main()