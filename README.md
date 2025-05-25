# 🚀 gas\_2505 – Headless Web Overload Simulator (Cloudflare Bypass Ready)

> By AyoungCyber – Powered by Playwright + CapMonster + Auto Endpoint Crawler

## 📦 What Is This?

`gas_2505.py` is a fully automated stealth headless browser engine that simulates real browser interactions using authenticated proxies, bypasses JS Challenges, Turnstile & reCAPTCHA, and auto-attacks heavy endpoints based on content load.

️⃣ Ideal for:

* 🔥 Cloudflare-bypassed simulations
* 🧠 Auto crawling and endpoint targeting
* 👁️ Realistic traffic & load testing

---

## 📁 Files

* `gas_2505.py`: Main headless engine (Playwright + async)
* `gas_2505requirements.txt`: Required Python packages

---

## ⚙️ Installation on VPS (1 Line Setup)

```bash
cd /root && wget -q https://raw.githubusercontent.com/namalo/gas/main/gas_2505.py && wget -q https://raw.githubusercontent.com/namalo/gas/main/gas_2505requirements.txt && pip3 install -r gas_2505requirements.txt && python3 gas_2505.py
```

> 💡 Replace the link above with your actual GitHub raw URL!

---

## 📌 Requirements

* Python 3.8+
* Debian/Ubuntu with APT support
* Playwright dependencies:

```bash
sudo apt install wget curl unzip -y
pip3 install playwright
playwright install
playwright install-deps
```

---

## 🧠 Features

* ✅ Auto-scrape & use proxy from file (support `ip:port:user:pass`)
* ✅ Stealth mode with full anti-bot bypass
* ✅ Support Turnstile, reCAPTCHA (via CapMonster / 2Captcha)
* ✅ Multi-tab attack simulation with random delay, mouse movement, etc
* ✅ Auto scan heavy endpoint (`/search`, `/tag`, `/category`, `/author`)
* ✅ CPU overload prevention & safe-mode
* ✅ Live stats + log recorder (`log_attack.json`)

---

## 💻 Proxy Format

```
ip:port:username:password
```

Save to:

```
/var/www/html/proxy_new.txt
```

---

## 🛡️ Cloudflare Detection Example

Script automatically detects Cloudflare JS challenge and solves using CapMonster or 2Captcha.

---

## 📊 Output Sample

```bash
✅ Proxy aktif: 84
📱 Server: LiteSpeed (via Cloudflare)
🔥 Endpoint berat: /tag/ekonomi/, /category/nasional/
✅ [SUCCESS] Accessed with 123.123.123.123:8080
📈 Ronde selesai – Level: TINGGI
```

---

## 🔀 Auto Loop with Cronjob (Optional)

Edit crontab:

```bash
crontab -e
```

Add this line to run every 5 mins:

```bash
*/5 * * * * /usr/bin/python3 /root/gas_2505.py
```

---

## ⚠️ Legal Notice

This project is for educational and stress-test research on your **own systems only**. Misuse for unauthorized access or DDoS is strictly prohibited and illegal.

---

## ❤️ Credit

Built by: **AyoungCyber**
Made with ❤️ for automation freaks.
