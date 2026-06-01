from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Raw
from scapy.utils import PcapWriter
import sys
import requests
import csv
from datetime import datetime

# --- Configuration ---
pcap_file = "traffic_analysis.pcap"
csv_file = "capture_log.csv"

# Initialize PCAP Writer
pktdump = PcapWriter(pcap_file, append=True, sync=True)

# --- ANSI Colors for Terminal ---
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
MAGENTA = "\033[95m"

# --- Port Mapping ---
PORT_MAP = {
    80: "HTTP", 443: "HTTPS", 53: "DNS", 22: "SSH",
    21: "FTP", 25: "SMTP", 3389: "RDP"
}

# --- Suspicious Keywords ---
SUSPICIOUS_KEYWORDS = ['password', 'user', 'username', 'login', 'admin', 'pass']

# --- Geo-Location Cache ---
IP_GEO_CACHE = {}

def print_banner():
    """Prints the tool banner with credit."""
    banner = f"""{CYAN}
    _   _      _                      _      
   | \ | | ___| |___      _____  _ __| | __  
   |  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ /  
   | |\  |  __/ |_ \ V  V / (_) | |  |   <   
   |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\  
                                             
    ____        _  __  __          
   / ___| _ __ (_)/ _|/ _| ___ _ __ 
   \___ \| '_ \| | |_| |_ / _ \ '__|
    ___) | | | | |  _|  _|  __/ |   
   |____/|_| |_|_|_| |_|  \___|_|   
                                    {RESET}"""
    
    print(banner)
    print(f"{YELLOW}{'='*50}")
    print(f" CREATED FOR:  {GREEN}CodeAlpha Internship Project{YELLOW}")
    print(f" DEVELOPER:    {MAGENTA} Priyan {YELLOW}")
    print(f"{'='*50}{RESET}\n")

def init_csv():
    """Creates the CSV file and writes the header row."""
    try:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Source IP', 'Destination IP', 'Protocol', 'Payload'])
        print(f"[*] CSV Log initialized: {csv_file}")
    except Exception as e:
        print(f"{RED}[!] Error creating CSV file: {e}{RESET}")

def get_geolocation(ip_address):
    """Fetches location data with caching."""
    if ip_address in IP_GEO_CACHE:
        return IP_GEO_CACHE[ip_address]

    if ip_address.startswith(("192.168.", "10.", "172.16.", "127.")):
        location = "[Local Network]"
        IP_GEO_CACHE[ip_address] = location
        return location

    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}", timeout=1)
        data = response.json()
        if data['status'] == 'success':
            location = f"[{data.get('city', '')}, {data.get('country', 'Unknown')}]"
        else:
            location = "[Unknown Location]"
    except:
        location = "[Lookup Failed]"
    
    IP_GEO_CACHE[ip_address] = location
    return location

def identify_service(port):
    if port in PORT_MAP:
        return PORT_MAP[port]
    return f"Port {port}"

def packet_callback(packet):
    if packet.haslayer(IP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        # Get Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Geo-Location
        dst_location = get_geolocation(dst_ip)
        
        # Protocol & Port extraction
        protocol_name = ""
        src_port = 0
        dst_port = 0
        
        if packet.haslayer(TCP):
            protocol_name = "TCP"
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        elif packet.haslayer(UDP):
            protocol_name = "UDP"
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
        else:
            protocol_name = "Other"

        service_name = identify_service(dst_port)

        # Payload Processing
        payload_content = "Empty"
        payload_display = "Empty"
        
        if packet.haslayer(Raw):
            payload_bytes = packet[Raw].load
            try:
                decoded_payload = payload_bytes.decode('utf-8', 'ignore')
                payload_content = decoded_payload

                # Keyword Check + Credential Extraction
                import re
                found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in decoded_payload.lower()]
                if found_keywords:
                    print(f"{RED}[!] SUSPICIOUS DATA DETECTED: {found_keywords}{RESET}")
                    pairs = re.findall(r'([\w\-]+)=([^&\r\n ]+)', decoded_payload)
                    for key, value in pairs:
                        if any(kw in key.lower() for kw in SUSPICIOUS_KEYWORDS):
                            print(f"{RED}    >>> {key} : {value}{RESET}")

                # Terminal Display Formatting
                if dst_port in [80, 21]:
                    payload_display = f"{decoded_payload.strip()[:100]}..."
                else:
                    payload_display = f"[Binary/Encrypted - {len(payload_bytes)} bytes]"
            except:
                payload_content = f"[Binary Data - {len(payload_bytes)} bytes]"
                payload_display = payload_content

        # --- 1. Terminal Output ---
        color = RESET
        if dst_port in [443, 22]:
            color = GREEN
        elif dst_port in [80, 21, 23, 25]:
            color = RED
        else:
            color = CYAN

        print(f"{color}{'='*60}")
        print(f"[*] {timestamp}")
        print(f"    Source:         {src_ip}:{src_port}")
        print(f"    Destination:    {dst_ip}:{dst_port} {YELLOW}{dst_location}{color}")
        print(f"    Protocol:       {protocol_name} ({service_name})")
        print(f"    Payload:        {payload_display}")
        print(f"{'='*60}{RESET}")
        
        # --- 2. CSV Logging ---
        try:
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, src_ip, dst_ip, protocol_name, payload_content])
        except Exception as e:
            print(f"{RED}[!] Error writing to CSV: {e}{RESET}")

        # --- 3. PCAP Logging ---
        pktdump.write(packet)

def start_sniffer():
    # Show Banner First
    print_banner()
    
    # Initialize CSV Headers
    init_csv()
    
    print(f"[*] Sniffer started...")
    print(f"[*] Logging to CSV: {csv_file}")
    print(f"[*] Logging to PCAP: {pcap_file}")
    print(f"[*] Press Ctrl+C to stop.")
    
    try:
        sniff(filter="ip", prn=packet_callback, store=False)
    except KeyboardInterrupt:
        print("\n[!] Stopping Sniffer.")
        pktdump.close()

if __name__ == "__main__":
    start_sniffer()
