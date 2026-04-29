# Automated-SOC-Home-Lab
# SOC Home Lab — AWS Environment

## Overview
I built a complete SOC home lab on AWS over 4 weeks.
Simulated real attacks, detected them with Wazuh SIEM,
responded with Python automation, and documented 
everything using NIST SP 800-61 framework.

## Tools & Technologies
- **SIEM:** Wazuh
- **Attack Simulation:** Kali Linux, Hydra, Mimikatz
- **Ticketing:** osTicket
- **Automation:** Python, Boto3, Telegram Bot API
- **Threat Intel:** AbuseIPDB, VirusTotal
- **Network:** AWS EC2, Active Directory, Sysmon
- **Framework:** MITRE ATT&CK, NIST SP 800-61

## Lab Architecture
- Windows Server 2019 (Domain Controller) — dubaihq.local
- Windows 10 (Employee Endpoint)
- Ubuntu Server (Wazuh SIEM)
- Kali Linux (Attack Machine)
- All hosted on AWS EC2 Free Tier

## Incidents Documented
| Incident | MITRE ID | Status |
|----------|----------|--------|
| RDP Brute Force | T1110 | Resolved |
| Credential Dumping | T1003 | Resolved |

## Key Skills Demonstrated
- Wazuh SIEM deployment and false positive tuning
- MITRE ATT&CK attack simulation
- Python automation for incident response
- Threat intelligence integration (AbuseIPDB)
- NIST SP 800-61 incident reporting
- AWS EC2 and Security Group management
