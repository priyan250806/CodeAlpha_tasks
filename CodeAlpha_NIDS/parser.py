import json
import os
from collections import defaultdict
from datetime import datetime

# --- Configuration ---
SURICATA_LOG = "/var/log/suricata/eve.json"
OUTPUT_FILE  = "dashboard/data.json"

# --- Severity mapping by Suricata priority ---
SEVERITY_MAP = {1: "critical", 2: "high", 3: "medium", 4: "low"}

# --- Alert category colors for dashboard ---
CATEGORY_COLOR = {
    "Attempted Information Leak":    "#f87171",
    "Potential Corporate Privacy Violation": "#fb923c",
    "A Network Trojan was Detected": "#ef4444",
    "Attempted Denial of Service":   "#f97316",
    "Web Application Attack":        "#e879f9",
    "Misc Attack":                   "#fbbf24",
    "Unknown":                       "#94a3b8",
}

def parse_eve_log(log_path):
    """Parse Suricata eve.json and extract alert events."""
    alerts = []

    if not os.path.exists(log_path):
        print(f"[!] Log file not found: {log_path}")
        print("[*] Using sample data for dashboard demo...")
        return generate_sample_data()

    with open(log_path, "r") as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                if event.get("event_type") == "alert":
                    alert = {
                        "timestamp":   event.get("timestamp", ""),
                        "src_ip":      event.get("src_ip", "Unknown"),
                        "src_port":    event.get("src_port", 0),
                        "dest_ip":     event.get("dest_ip", "Unknown"),
                        "dest_port":   event.get("dest_port", 0),
                        "proto":       event.get("proto", "Unknown"),
                        "signature":   event["alert"].get("signature", "Unknown"),
                        "category":    event["alert"].get("category", "Unknown"),
                        "severity":    SEVERITY_MAP.get(event["alert"].get("severity", 4), "low"),
                        "sid":         event["alert"].get("signature_id", 0),
                        "action":      event["alert"].get("action", "allowed"),
                    }
                    alerts.append(alert)
            except (json.JSONDecodeError, KeyError):
                continue

    print(f"[*] Parsed {len(alerts)} alerts from {log_path}")
    return alerts

def generate_sample_data():
    """Generate realistic sample alerts for dashboard demo."""
    import random
    sample_signatures = [
        ("ET SCAN Nmap Scripting Engine User-Agent Detected", "Attempted Information Leak", 2),
        ("ET EXPLOIT Apache Log4j RCE Attempt", "A Network Trojan was Detected", 1),
        ("ET DOS Potential HTTP Flood", "Attempted Denial of Service", 2),
        ("ET WEB_SERVER SQL Injection Attempt", "Web Application Attack", 2),
        ("ET SCAN Possible Nmap Port Scan", "Attempted Information Leak", 3),
        ("ET MALWARE Suspicious User-Agent", "A Network Trojan was Detected", 2),
        ("ET POLICY RDP Attempt", "Potential Corporate Privacy Violation", 3),
        ("ET SCAN SSH Brute Force Attempt", "Attempted Information Leak", 2),
        ("ET WEB_SERVER XSS Attempt", "Web Application Attack", 3),
        ("ET TROJAN Reverse Shell Attempt", "A Network Trojan was Detected", 1),
    ]

    src_ips  = ["45.33.32.156","192.168.1.105","10.0.0.44","185.220.101.12",
                "203.0.113.42","198.51.100.7","172.16.0.99","91.108.4.10"]
    dst_ips  = ["192.168.1.1","192.168.1.10","192.168.1.20","10.0.0.1"]
    protos   = ["TCP","UDP","ICMP"]

    alerts = []
    now = datetime.now()
    for i in range(120):
        sig, cat, sev_num = random.choice(sample_signatures)
        delta_minutes = random.randint(0, 1440)
        ts = now.replace(
            minute=random.randint(0,59),
            second=random.randint(0,59)
        )
        alerts.append({
            "timestamp":  ts.strftime("%Y-%m-%dT%H:%M:%S.%f+0000"),
            "src_ip":     random.choice(src_ips),
            "src_port":   random.randint(1024, 65535),
            "dest_ip":    random.choice(dst_ips),
            "dest_port":  random.choice([22,80,443,3389,8080,21,53]),
            "proto":      random.choice(protos),
            "signature":  sig,
            "category":   cat,
            "severity":   SEVERITY_MAP.get(sev_num, "medium"),
            "sid":        random.randint(2000000, 2999999),
            "action":     random.choice(["allowed","blocked","blocked","allowed"]),
        })
    return alerts

def build_stats(alerts):
    """Build aggregated statistics for dashboard charts."""
    severity_count   = defaultdict(int)
    category_count   = defaultdict(int)
    src_ip_count     = defaultdict(int)
    proto_count      = defaultdict(int)
    action_count     = defaultdict(int)
    hourly_count     = defaultdict(int)
    top_signatures   = defaultdict(int)

    for a in alerts:
        severity_count[a["severity"]]   += 1
        category_count[a["category"]]   += 1
        src_ip_count[a["src_ip"]]       += 1
        proto_count[a["proto"]]         += 1
        action_count[a["action"]]       += 1
        top_signatures[a["signature"]]  += 1

        try:
            hour = datetime.fromisoformat(
                a["timestamp"].replace("+0000","").replace("Z","")
            ).strftime("%H:00")
            hourly_count[hour] += 1
        except Exception:
            pass

    # Top 10 source IPs
    top_ips = sorted(src_ip_count.items(), key=lambda x: x[1], reverse=True)[:10]

    # Top 10 signatures
    top_sigs = sorted(top_signatures.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_alerts":    len(alerts),
        "severity":        dict(severity_count),
        "categories":      dict(category_count),
        "top_src_ips":     top_ips,
        "protocols":       dict(proto_count),
        "actions":         dict(action_count),
        "hourly":          dict(sorted(hourly_count.items())),
        "top_signatures":  top_sigs,
        "recent_alerts":   alerts[-20:][::-1],
    }

def save_dashboard_data(stats, alerts):
    """Save parsed data as JSON for the dashboard."""
    os.makedirs("dashboard", exist_ok=True)
    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stats": stats,
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"[*] Dashboard data saved → {OUTPUT_FILE}")

def main():
    print("=" * 55)
    print("  SURICATA LOG PARSER — CodeAlpha NIDS Task 3")
    print("  DEVELOPER: PRIYAN")
    print("=" * 55)

    alerts = parse_eve_log(SURICATA_LOG)
    stats  = build_stats(alerts)
    save_dashboard_data(stats, alerts)

    print(f"\n[+] Total Alerts   : {stats['total_alerts']}")
    print(f"[+] Critical       : {stats['severity'].get('critical', 0)}")
    print(f"[+] High           : {stats['severity'].get('high', 0)}")
    print(f"[+] Medium         : {stats['severity'].get('medium', 0)}")
    print(f"[+] Low            : {stats['severity'].get('low', 0)}")
    print(f"\n[*] Open dashboard/index.html in your browser to view the dashboard.")

if __name__ == "__main__":
    main()
