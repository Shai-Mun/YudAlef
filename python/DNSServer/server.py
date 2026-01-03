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


def build_ip(ip):
    nums = ip.decode().split('.')
    b_ip = b''
    for n in nums:
        b_ip += struct.pack('B', int(n))

    return b_ip


def dns_reply(fields):
    reply = b''
    reply += struct.pack('H', socket.htons(fields[0]))  # id
    reply += struct.pack('H', socket.htons(fields[1]) | 0x8080)  # flags
    reply += struct.pack('H', socket.htons(fields[2]))  # q count
    reply += struct.pack('H', socket.htons(fields[2]))  # a count
    reply += struct.pack('H', socket.htons(fields[3]))  # auth
    reply += struct.pack('H', socket.htons(fields[4]))  # add

    reply += struct.pack(f'{len(fields[5])}s', fields[5])  # domain
    reply += struct.pack('H', socket.htons(fields[6]))  # type
    reply += struct.pack('H', socket.htons(fields[7]))  # class

    reply += b'\xc0\x0c' # offset
    reply += struct.pack('H', socket.htons(fields[6]))  # type
    reply += struct.pack('H', socket.htons(fields[7]))  # class
    reply += b'\x4f\x00\x00\x00' # TTL
    reply += struct.pack('H', socket.htons(len(fields[8])))
    reply += build_ip(fields[8])

    return reply


def dns_handler(data, address):
    if b'shai' in data:
        msg_id = socket.ntohs(struct.unpack('H', data[:2])[0])
        msg_flags = socket.ntohs(struct.unpack('H', data[2:4])[0])
        msg_q_count = socket.ntohs(struct.unpack('H', data[4:6])[0])
        msg_a_count = socket.ntohs(struct.unpack('H', data[6:8])[0])
        msg_auth = socket.ntohs(struct.unpack('H', data[8:10])[0])
        msg_add = socket.ntohs(struct.unpack('H', data[10:12])[0])

        start_domain = 12
        user_domain = handle_domain(data[start_domain:data[start_domain:].find(b'0')])
        end_domain = start_domain + len(user_domain) + 2 # 1 for the size byte, 1 for the end byte

        msg_domain = struct.unpack(f'{len(user_domain) + 2}s', data[start_domain: end_domain])[0]
        msg_type = socket.ntohs(struct.unpack('H', data[end_domain: end_domain + 2])[0])
        msg_class = socket.ntohs(struct.unpack('H', data[end_domain + 2: end_domain + 4])[0])

        print(user_domain)
        return dns_reply([msg_id, msg_flags, msg_q_count, msg_auth, msg_add, msg_domain, msg_type, msg_class, address[0].encode()])
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)

        sock.sendto(data, ('8.8.8.8', 53))
        ret, _ = sock.recvfrom(4096)
        sock.close()
        return ret


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
            msg = dns_handler(data, addr)
            sock.sendto(msg, addr)
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
