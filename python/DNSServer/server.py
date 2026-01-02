import socket
import struct

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


def handle_domain(data):
    s = ''
    i = 0
    while True:
        size = struct.unpack('B', data[i:i+1])[0]
        i += 1
        if size == 0:
            break
        s += struct.unpack(f'{size}s', data[i:i+size])[0].decode() + '.'
        i += size

    return s[:-1]


def dns_reply(fields):
    reply = b''
    reply += struct.pack('H', socket.htons(fields[0]))[0]  # id
    reply += struct.pack('H', socket.htons(fields[1]))[0]  # id
    reply += struct.pack('H', socket.htons(fields[2]))[0]  # id
    reply += struct.pack('H', socket.htons(fields[2]))[0]  # id
    reply += struct.pack('H', socket.htons(fields[3]))[0]  # id
    reply += struct.pack('H', socket.htons(fields[4]))[0]  # id


    reply += socket.htons(struct.pack('H', fields[1] | 0x8080)[0])  # flags
    reply += socket.htons(struct.pack('H', fields[2])[0])  # q count
    reply += socket.htons(struct.pack('H', fields[2])[0])  # a count
    reply += socket.htons(struct.pack('H', fields[3])[0])  # auth
    reply += socket.htons(struct.pack('H', fields[4])[0])  # add


def dns_handler(data, address):

    if b'shai' in data:
        msg_id = socket.ntohs(struct.unpack('H', data[:2])[0])
        msg_flags = socket.ntohs(struct.unpack('H', data[2:4])[0])
        msg_q_count = socket.ntohs(struct.unpack('H', data[4:6])[0])
        msg_a_count = socket.ntohs(struct.unpack('H', data[6:8])[0])
        msg_auth = socket.ntohs(struct.unpack('H', data[8:10])[0])
        msg_add = socket.ntohs(struct.unpack('H', data[10:12])[0])

        start_domain = 12
        msg_domain = handle_domain(data[start_domain:data[start_domain:].find(b'0')])
        end_domain = start_domain + len(msg_domain) + 1

        msg_type = socket.ntohs(struct.unpack('H', data[end_domain: end_domain + 2])[0])
        msg_class = data[end_domain + 2: end_domain + 4]

        print(msg_domain, end_domain, msg_type, msg_class)
        start_domain = end_domain + 4


        print(msg_id, msg_flags, msg_q_count, msg_a_count, msg_auth, msg_add)
        return dns_reply([msg_id, msg_flags, msg_q_count, msg_auth, msg_add, msg_domain, msg_type, msg_class])


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
            dns_handler(data, addr)
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
