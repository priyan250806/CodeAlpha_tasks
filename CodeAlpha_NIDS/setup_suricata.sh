#!/bin/bash
# =============================================================
#  Suricata Setup Script for Kali Linux
#  CodeAlpha NIDS — Task 3 | Developer: Priyan
# =============================================================

echo "=============================================="
echo "  SURICATA SETUP — CodeAlpha NIDS Task 3"
echo "  DEVELOPER: PRIYAN"
echo "=============================================="

# Step 1 — Install Suricata
echo "[*] Installing Suricata..."
sudo apt update -y
sudo apt install -y suricata

# Step 2 — Find active network interface
IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
echo "[*] Detected interface: $IFACE"

# Step 3 — Update Suricata rules
echo "[*] Updating Suricata rules (this may take a few minutes)..."
sudo suricata-update

# Step 4 — Backup and patch config
echo "[*] Configuring Suricata..."
sudo cp /etc/suricata/suricata.yaml /etc/suricata/suricata.yaml.bak

# Set interface in config
sudo sed -i "s/interface: eth0/interface: $IFACE/g" /etc/suricata/suricata.yaml

# Enable eve-log JSON output (should already be on by default)
echo "[*] Verifying eve.json logging is enabled..."
grep -q "eve-log" /etc/suricata/suricata.yaml && echo "[+] eve-log confirmed active" || echo "[!] Check suricata.yaml manually"

# Step 5 — Add custom detection rules
echo "[*] Adding custom detection rules..."
sudo tee /etc/suricata/rules/custom.rules > /dev/null << 'RULES'
# ── Custom NIDS Rules — CodeAlpha Task 3 ──────────────────

# Detect Nmap SYN scan
alert tcp any any -> $HOME_NET any (msg:"NIDS: Possible Nmap SYN Scan"; flags:S,12; threshold:type threshold,track by_src,count 20,seconds 5; sid:9000001; rev:1;)

# Detect SSH brute force (20 attempts in 5 seconds)
alert tcp any any -> $HOME_NET 22 (msg:"NIDS: SSH Brute Force Attempt"; flow:to_server,established; content:"SSH"; threshold:type threshold,track by_src,count 20,seconds 5; sid:9000002; rev:1;)

# Detect HTTP SQL injection attempt
alert http any any -> $HOME_NET any (msg:"NIDS: SQL Injection Attempt Detected"; content:"' OR '1'='1"; nocase; http_uri; sid:9000003; rev:1;)
alert http any any -> $HOME_NET any (msg:"NIDS: SQL Injection UNION SELECT"; content:"UNION SELECT"; nocase; http_uri; sid:9000004; rev:1;)

# Detect XSS attempt
alert http any any -> $HOME_NET any (msg:"NIDS: XSS Attempt Detected"; content:"<script>"; nocase; http_uri; sid:9000005; rev:1;)

# Detect ICMP ping sweep
alert icmp any any -> $HOME_NET any (msg:"NIDS: ICMP Ping Sweep"; itype:8; threshold:type threshold,track by_src,count 10,seconds 3; sid:9000006; rev:1;)

# Detect port scan (many ports from same IP)
alert tcp any any -> $HOME_NET any (msg:"NIDS: Possible Port Scan"; flags:S; threshold:type threshold,track by_src,count 30,seconds 10; sid:9000007; rev:1;)

# Detect Telnet access (insecure protocol)
alert tcp any any -> $HOME_NET 23 (msg:"NIDS: Telnet Access Attempt"; flow:to_server; sid:9000008; rev:1;)

# Detect FTP login attempt
alert tcp any any -> $HOME_NET 21 (msg:"NIDS: FTP Login Attempt"; flow:to_server,established; content:"USER"; sid:9000009; rev:1;)

# Detect RDP brute force
alert tcp any any -> $HOME_NET 3389 (msg:"NIDS: RDP Brute Force Attempt"; flags:S; threshold:type threshold,track by_src,count 10,seconds 10; sid:9000010; rev:1;)
RULES

echo "[+] Custom rules written to /etc/suricata/rules/custom.rules"

# Add custom rules to suricata.yaml if not already present
if ! grep -q "custom.rules" /etc/suricata/suricata.yaml; then
    sudo sed -i '/rule-files:/a\  - custom.rules' /etc/suricata/suricata.yaml
    echo "[+] custom.rules added to suricata.yaml"
fi

# Step 6 — Test configuration
echo "[*] Testing Suricata configuration..."
sudo suricata -T -c /etc/suricata/suricata.yaml -v 2>&1 | tail -5

echo ""
echo "=============================================="
echo "[+] Setup complete!"
echo "[*] Start Suricata with:"
echo "    sudo systemctl start suricata"
echo "    sudo systemctl enable suricata"
echo "[*] Or run manually:"
echo "    sudo suricata -c /etc/suricata/suricata.yaml -i $IFACE"
echo "[*] View live alerts:"
echo "    sudo tail -f /var/log/suricata/eve.json | python3 -m json.tool"
echo "[*] Run the dashboard parser:"
echo "    python3 parser.py"
echo "    Then open dashboard/index.html in your browser"
echo "=============================================="
