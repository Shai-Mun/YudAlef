import sys
i, o, e = sys.stdin, sys.stdout, sys.stderr
from scapy.all import *
sys.stdin, sys.stdout, sys.stderr = i, o, e

from scapy.layers.dns import DNS, DNSQR, DNSRR

from scapy.layers.inet import IP, TCP, UDP


def filter_dns(p):
    return DNS in p and p[DNS].opcode == 0 and DNSQR in p and p[DNSQR].qtype == 1


def print_query_name(dns_packet):
    print(dns_packet[DNSQR].qname)


packets = sniff(count=10, lfilter=filter_dns, prn=print_query_name)
