import requests
import json
import boto3  
from datetime import datetime
import socks  
import socket  
import os
from datetime import datetime
# ==========================================
# 1. KEYS CONFIGURATIONS (Enter Your Keys Here)
# ==========================================
ABUSEIPDB_API_KEY = "ABUSEIPDB_API_KEY_HERE"

# AWS Credentials
AWS_ACCESS_KEY = "YOUR_AWS_ACCESS_KEY_HERE"
AWS_SECRET_KEY = "YOUR_AWS_SECRET_KEY_HERE"  
AWS_REGION = "YOUR_REGION_HERE" # 
NACL_ID = "NACL_ID_HERE" # 

# osTicket API Credentials
OSTICKET_URL = "YOUR_OSTICKET_URL_HERE"
OSTICKET_API_KEY = "OSTICKET_API_KEY_HERE"

# ==========================================
# 2. FUNCTIONS (Intel, Block, Ticket)
# ==========================================

# Function 1: Threat Intel
def check_threat_intel(attacker_ip):
    print(f"[*] Checking IP: {attacker_ip} on AbuseIPDB...")
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {'Accept': 'application/json', 'Key': ABUSEIPDB_API_KEY}
    querystring = {'ipAddress': attacker_ip, 'maxAgeInDays': '90'}
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        threat_score = response.json()['data']['abuseConfidenceScore']
        print(f"[+] Result: Threat Score for {attacker_ip} is {threat_score}%")
        return threat_score
    except Exception as e:
        print(f"[-] Error: {e}")
        return 0
# Function 2: AWS Auto-Block
def block_ip_aws(attacker_ip):
    print(f"[*] Boto3 Activated: Blocking {attacker_ip} in AWS NACL...")
    try:
        # AWS Client Setup
        ec2 = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)
        
        # Configure a firewall rule to deny a specific IP address access to port 22, Remote Desktop Protocol (RDP), or all network ports.
        ec2.create_network_acl_entry(
            NetworkAclId=NACL_ID,
            RuleNumber=110, # Priority number
            Protocol='-1',  # All traffic
            RuleAction='deny',
            Egress=False,   # Inbound traffic ko rokna hai
            CidrBlock=f"{attacker_ip}/32", # Specific IP address
            PortRange={'From': 0, 'To': 65535}
        )
        print("[+] SUCCESS: IP successfully blocked in AWS Firewall!")
        return True
    except Exception as e:
        print(f"[-] AWS Block Failed: {e}")
        return False

# Function 3: osTicket Auto-Create
def create_osticket(attacker_ip, threat_score):
    print("[*] Creating automated Incident Ticket in osTicket...")
    
    
    ticket_data = {
        "alert": True,
        "autorespond": False,
        "source": "API",
        "name": "Wazuh SOC",           # User  name
        "email": "soc@yourdomain.com", # User  email id(This should be valid in osTicket.)
        "subject": f"Alert: IP {attacker_ip} Blocked",
        "message": f"IP: {attacker_ip} was detected with threat score {threat_score} and has been auto-blocked in AWS NACL.",
        "ip": attacker_ip,
        "topicId": 1  
    }
    
    headers = {
        'X-API-Key': OSTICKET_API_KEY,
        'Content-Type': 'application/json' 
    }
    
    try:
        response = requests.post(OSTICKET_URL, json=ticket_data, headers=headers)
        if response.status_code == 201:
            print(f"[+] SUCCESS: Ticket #{response.text} created automatically!")
        else:
            # Agar error aaye toh humein poora message dikhao
            print(f"[-] Ticket Creation Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[-] osTicket Error: {e}")

# ==========================================
# 0. WAZUH DETECTION ENGINE (Last 5 Mins)
# ==========================================
def get_wazuh_bruteforce_ip():
    print("[*] Checking Wazuh for Brute Force Alerts in the last 5 minutes...")
    try:
        # Copy alerts file locally for processing
os.system("sudo cp /var/ossec/logs/alerts/alerts.json /tmp/alerts_copy.json > /dev/null 2>&1")

# Set file permissions for local processing 
# Set safe file permissions for local processing
os.system("sudo chmod 600 /tmp/alerts_copy.json > /dev/null 2>&1")
        
        log_file = "/tmp/alerts_copy.json"
        
       # 2. Read the last 100 alerts
        with open(log_file, 'r') as f:
            lines = f.readlines()[-100:]
            
       # 3. Logic to check new alerts
        for line in reversed(lines):
            if not line.strip(): continue # Khali lines ignore karo
            
            alert = json.loads(line)
            rule_id = str(alert.get("rule", {}).get("id", ""))
            
            # Rule 60122 (Windows) ya 5712 (Linux)
            if rule_id in ["60122", "5712", "5710"]: 
                
                ip = alert.get("data", {}).get("srcip")
                if not ip:
                    ip = alert.get("data", {}).get("win", {}).get("eventdata", {}).get("ipAddress")
                
                if ip and ip != "127.0.0.1": 
                    print(f"[+] ALERT FOUND! MITRE T1110 Detected. Rule: {rule_id}")
                    print(f"[+] Attacker IP Extracted: {ip}")
                    return ip
                    
        print("[-] SAFE: No Brute Force attacks detected recently.")
        return None
        
    except Exception as e:
        print(f"[-] Wazuh Detection Error: {e}")
        return None
        
        # ==========================================
# 4. TELEGRAM NOTIFICATION
# ==========================================
TELEGRAM_TOKEN = "TELEGRAM_TOKEN_HERE"
TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID_TOKEN



def send_telegram_msg(attacker_ip, threat_score, ticket_id):
    print("[*] Sending Alert to Telegram...")
    
   # To get the current exact time
    current_time = datetime.now().strftime("%H:%M:%S")
    
    
    message = (
        f"🚨 Critical Alert: MITRE T1110 Detected\n"
        f"Attacker IP: {attacker_ip}\n"
        f"AbuseIPDB Score: {threat_score}% malicious\n"
        f"Action: IP Blocked via AWS\n"
        f"Ticket: #{ticket_id}\n"
        f"Created Time: {current_time}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
   
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }

    try:
        response = requests.post(url, json=payload, timeout=30, proxies=proxies)
        if response.status_code == 200:
            print("[+] SUCCESS: Telegram Notification Sent!")
        else:
            print(f"[-] Telegram Failed: {response.text}")
    except Exception as e:
        print(f"[-] Telegram Error: {e}")

# ==========================================
# 3. MAIN AUTOMATION ENGINE
# ==========================================
# ==========================================
# 3. MAIN AUTOMATION ENGINE
# ==========================================
# ==========================================
# MAIN AUTOMATION ENGINE
# ==========================================
if __name__ == "__main__":
    print("--- SOC AUTOMATION SCRIPT STARTED ---")
    
   # 1. Extract IP from Wazuh
    wazuh_detected_ip = get_wazuh_bruteforce_ip()
    
   # Proceed only if Wazuh has detected an attack!
    if wazuh_detected_ip:
        
        # 2. Threat Intel (AbuseIPDB)
        score = check_threat_intel(wazuh_detected_ip)
        
       # If the attacker's score is greater than 50
        if score >= 50:
            print("[!] DANGER: High Risk IP detected! Initiating Auto-Remediation...")
            
            # 3. AWS Block 
            is_blocked = block_ip_aws(wazuh_detected_ip)
            
            # 4. osTicket & Telegram 
            if is_blocked:
                create_osticket(wazuh_detected_ip, score)
                
                # Telegram function call 
               # "Auto" is written so that the ticket ID is displayed dynamically
                send_telegram_msg(wazuh_detected_ip, score, "Auto")
                
                print("\n[🏁] FULL AUTOMATION CYCLE COMPLETED SUCCESSFULLY!")
            else:
                print("[-] Skip: Ticket and Alert skipped because AWS block failed.")
        else:
            print("[✓] Threat Score low. Monitoring IP.")
            
    else:
        print("[✓] Script finished. No action required.")
