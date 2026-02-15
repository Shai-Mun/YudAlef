import sys
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, TCP, UDP, ICMP

i, o, e = sys.stdin, sys.stdout, sys.stderr
sys.stdin, sys.stdout, sys.stderr = i, o, e


def filter_packet(p):
    return IP in p and p[IP].src == '10.68.121.134' and ICMP in p and Raw in p and p[Raw].load[:4].decode().isnumeric()


def print_packet(p):
    print(p[Raw].load)


def main(ip):
    done = 0

    with open('copy.jpg', 'wb') as f:
        while True:
            pack = sniff(count=1, lfilter=filter_packet, prn=print_packet)[0]

            p_num = int(pack[Raw].load[:4].decode())
            if p_num == done + 1:
                f.write(pack[Raw].load[4:])
                send(IP(dst=ip) / ICMP(type="echo-reply") / (str(p_num).zfill(4).encode()))
                done += 1


if __name__ == '__main__':
    main(sys.argv[1])
