import sys
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, TCP, UDP, ICMP

i, o, e = sys.stdin, sys.stdout, sys.stderr
sys.stdin, sys.stdout, sys.stderr = i, o, e

# 10.68.121.134
# 10.68.121.28


def main(ip, filename):
    data = b''
    with open(filename, 'rb') as f:
        cnt = 1
        data = f.read(1024)

        while True:
            if not data:
                send(IP(dst=ip) / ICMP(type="echo-request") / (str(cnt).zfill(4).encode() + b'end'))
                break
            print(data)

            send_packet = IP(dst=ip) / ICMP(type="echo-request") / (str(cnt).zfill(4).encode() + data)
            resp = sr1(send_packet, timeout=2)
            if resp is not None and resp[Raw].load.decode() == str(cnt).zfill(4):
                print(resp[Raw].load)
                cnt += 1
                data = f.read(1024)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
