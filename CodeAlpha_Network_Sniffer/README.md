# 🔍 Advanced Network Sniffer (Python)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Scapy-2.5+-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Platform-Kali%20Linux-purple?style=for-the-badge&logo=linux&logoColor=white"/>
  <img src="https://img.shields.io/badge/Internship-CodeAlpha-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge"/>
</p>

<p align="center">
  A real-time network packet sniffer built in Python using Scapy. Captures, analyzes, and logs live network traffic — displaying source/destination IPs, protocols, geo-location, and payload data with color-coded terminal output.
</p>

---



![Demo Output](https://github.com/priyan250806/CodeAlpha_tasks/blob/main/CodeAlpha_Network_Sniffer/screenshots/demo2_output.png)

---

## 📌 About This Project

This project was built as **Task 1** of the **CodeAlpha Cybersecurity Internship**.

The goal is to understand:
- How network packets are structured (Ethernet → IP → TCP/UDP → Payload)
- How data flows through a network in real time
- How unencrypted protocols (HTTP, FTP) expose sensitive data
- How tools like Wireshark work under the hood

> ⚠️ **Ethical Notice:** This tool is strictly for educational use on networks and systems you own or have explicit permission to test. Unauthorized packet sniffing is illegal.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🎨 **Color-coded output** | Green = encrypted (HTTPS/SSH), Red = unencrypted (HTTP/FTP), Cyan = other |
| 🌍 **Geo-location lookup** | Shows the city and country of destination IPs using ip-api.com |
| 🔐 **Credential detection** | Detects and extracts suspicious keywords like `username`, `password`, `login` |
| 📄 **CSV logging** | Every packet is logged to `capture_log.csv` for later analysis |
| 📦 **PCAP export** | Traffic saved to `traffic_analysis.pcap` — openable in Wireshark |
| ⚡ **Real-time capture** | Live packet analysis with zero packet storage in RAM |
| 🗺️ **Protocol identification** | Identifies HTTP, HTTPS, DNS, SSH, FTP, SMTP, RDP by port number |
| 🛡️ **IP caching** | Geo-location results cached to avoid repeated API calls |

---

## 🛠️ Installation

### Prerequisites
- Kali Linux (or any Debian-based Linux)
- Python 3.x
- Root / sudo privileges

### Step 1 — Clone the repository
```bash
git clone https://github.com/priyan250806/CodeAlpha_NetworkSniffer.git
cd CodeAlpha_NetworkSniffer
```

### Step 2 — Install dependencies

**Option A — Virtual environment (recommended)**
```bash
python3 -m venv sniffer-env
source sniffer-env/bin/activate
pip install -r requirements.txt
```

**Option B — Direct install**
```bash
pip3 install -r requirements.txt --break-system-packages
```

**Option C — Via apt (Kali Linux)**
```bash
sudo apt install python3-scapy
pip3 install requests --break-system-packages
```

---

## 🚀 Usage

```bash
sudo python3 sniffer.py
```

> Must run with `sudo` — raw packet capture requires root privileges on Linux.

If using a virtual environment:
```bash
sudo sniffer-env/bin/python3 sniffer.py
```

### Stop the sniffer
```bash
Ctrl + C
```

---

## 📊 Sample Output

### Normal HTTPS Traffic (Encrypted — Green)
```
============================================================
[*] 2025-05-31 10:23:45
    Source:         192.168.1.5:54321
    Destination:    142.250.80.46:443  [Chennai, India]
    Protocol:       TCP (HTTPS)
    Payload:        [Binary/Encrypted - 517 bytes]
============================================================
```

### Unencrypted HTTP with Credentials Detected (Red)
```
============================================================
[*] 2025-05-31 10:23:47
    Source:         192.168.1.5:49200
    Destination:    93.184.216.34:80  [Los Angeles, US]
    Protocol:       TCP (HTTP)
    Payload:        POST /login username=admin&password=...
============================================================
[!] SUSPICIOUS DATA DETECTED: ['username', 'password']
    >>> username : admin
    >>> password : secret123
```

### UDP DNS Query (Cyan)
```
============================================================
[*] 2025-05-31 10:23:50
    Source:         192.168.1.5:52410
    Destination:    8.8.8.8:53  [Local Network]
    Protocol:       UDP (DNS)
    Payload:        Empty
============================================================
```
### 🚨 Suspicious Credential Detection (Red Alert)

![Credential Detection](final_img.png)

> Real capture showing the sniffer intercepting a POST request over **HTTP (port 80)** to `httpbin.org`.  
> The tool successfully extracted:
> - `username : admin`
> - `password : secret123`  
>
> This demonstrates exactly why **HTTP is dangerous** — credentials are sent as plain text and can be intercepted. Always use **HTTPS**.

---

## 🧪 Testing the Sniffer

Open two terminals:

**Terminal 1 — Run the sniffer**
```bash
sudo python3 sniffer.py
```

**Terminal 2 — Generate traffic**
```bash
# Test HTTPS (encrypted)
curl https://google.com

# Test HTTP (plaintext — shows payload)
curl http://example.com

# Test credential detection
curl -X POST http://httpbin.org/post \
     -d "username=admin&password=secret123"

# Test DNS (UDP)
nslookup github.com

# Test ICMP
ping -c 4 google.com
```

---

## 📁 Output Files

| File | Description |
|------|-------------|
| `capture_log.csv` | Logs every packet: Timestamp, Source IP, Destination IP, Protocol, Payload |
| `traffic_analysis.pcap` | Full packet capture — open with `wireshark traffic_analysis.pcap` |

### View CSV log
```bash
cat capture_log.csv
# or
column -t -s',' capture_log.csv
```

### Open in Wireshark
```bash
wireshark traffic_analysis.pcap
```

---

## 🗂️ Project Structure

```
CodeAlpha_NetworkSniffer/
│
├── sniffer.py              # Main sniffer script
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── capture_log.csv         # Generated on run — CSV packet log
├── traffic_analysis.pcap   # Generated on run — Wireshark capture
│
└── screenshots/
    └── demo_output.svg     # Terminal demo screenshot
```

---

## 🔬 How It Works

```
Network Interface (eth0/wlan0)
        │
        ▼
   Scapy sniff()          ← captures all IP packets in real time
        │
        ▼
  packet_callback()
        │
        ├── Extract IP layer    → Source IP, Destination IP
        ├── Extract TCP/UDP     → Ports, Protocol name
        ├── Geo-location API    → City, Country of destination
        ├── Payload decode      → UTF-8 text from Raw layer
        ├── Keyword scan        → Detect credentials in plaintext
        │
        ├── 🖥️  Terminal output  → Color-coded live display
        ├── 📄  CSV logging      → Append row to capture_log.csv
        └── 📦  PCAP logging     → Write packet to .pcap file
```

---

## ⚙️ Configuration

You can customize these variables at the top of `sniffer.py`:

```python
# Output file names
pcap_file = "traffic_analysis.pcap"
csv_file  = "capture_log.csv"

# Add more ports to identify
PORT_MAP = {
    80: "HTTP", 443: "HTTPS", 53: "DNS", 22: "SSH",
    21: "FTP", 25: "SMTP", 3389: "RDP"
}

# Add more suspicious keywords to detect
SUSPICIOUS_KEYWORDS = ['password', 'user', 'username', 'login', 'admin', 'pass']
```

To capture on a specific interface (e.g. `wlan0`):
```python
# In start_sniffer(), change:
sniff(filter="ip", prn=packet_callback, store=False)

# To:
sniff(filter="ip", iface="wlan0", prn=packet_callback, store=False)
```

---

## 📚 What I Learned

- How network packets are structured layer by layer (OSI model in practice)
- The difference between encrypted (HTTPS) and unencrypted (HTTP) traffic
- Why HTTP is dangerous — credentials are visible in plain text
- How tools like Wireshark capture and store packets (PCAP format)
- Using Python's Scapy library for raw packet manipulation
- Real-world application of geo-IP lookups and CSV logging

---

## 🧰 Technologies Used

- **Python 3** — Core programming language
- **Scapy** — Packet capture and analysis library
- **Requests** — HTTP library for geo-location API calls
- **ip-api.com** — Free IP geo-location API
- **Wireshark** — For viewing `.pcap` output files

---

## 👨‍💻 Developer

**Priyan**
CodeAlpha Cybersecurity Internship

---

## 📜 License

This project is for **educational purposes only** as part of the CodeAlpha internship program.

> Use responsibly. Only capture traffic on networks you own or have written permission to test.
