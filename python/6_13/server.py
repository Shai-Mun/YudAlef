import sys
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, TCP, UDP

i, o, e = sys.stdin, sys.stdout, sys.stderr
sys.stdin, sys.stdout, sys.stderr = i, o, e


def filter_packet(p):
    p.show()
    return IP in p and p[IP].src == '1.2.3.4' and UDP in p and Raw in p and str(p[Raw]).startswith('')


def print_packet(p):
    print(chr(p[UDP].dport))


def main():
    while True:
        pack = sniff(count=1, lfilter=filter_packet, prn=print_packet)
        pack.show()


if __name__ == '__main__':
    main()
