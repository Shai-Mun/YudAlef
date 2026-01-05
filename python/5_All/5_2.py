import sys
i, o, e = sys.stdin, sys.stdout, sys.stderr
from scapy.all import *
sys.stdin, sys.stdout, sys.stderr = i, o, e

from scapy.layers.dns import DNS, DNSQR, DNSRR

from scapy.layers.inet import IP, TCP, UDP


def http_get_filter(p):
    return TCP in p and Raw in p and bytes(p[Raw]).startswith(b'GET')


def print_get_name(http_packet):
    print(http_packet[Raw].load.show())


sniff(count=10, lfilter=http_get_filter, prn=print_get_name)
