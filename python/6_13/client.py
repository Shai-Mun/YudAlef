import sys
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, TCP, UDP

i, o, e = sys.stdin, sys.stdout, sys.stderr
sys.stdin, sys.stdout, sys.stderr = i, o, e


def main(ip):
    while True:
        msg = input("Enter a message")

        for c in msg:
            pack = IP(dst=ip, src='1.2.3.4')/UDP(dport=ord(c))/''
            send(pack)
            pack.show()


if __name__ == "__main__":
    main(sys.argv[1])
