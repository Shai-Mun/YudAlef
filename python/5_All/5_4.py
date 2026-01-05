import sys
i, o, e = sys.stdin, sys.stdout, sys.stderr
from scapy.all import *
sys.stdin, sys.stdout, sys.stderr = i, o, e

from scapy.layers.dns import DNS, DNSQR, DNSRR
from scapy.layers.inet import IP, TCP, UDP, Ether

my_packet = IP()
print(my_packet.show())
print('-----------------------------------------------------------')

my_packet = IP()/TCP()
print(my_packet.show())
print('-----------------------------------------------------------')

my_packet = Ether()/IP()/TCP()
print(my_packet.show())
print('-----------------------------------------------------------')

my_packet = Ether()/IP()/TCP()/b"GET / HTTP/1.0\r\n\r\n"
print(my_packet.show())
print('-----------------------------------------------------------')

hexdump(my_packet)

