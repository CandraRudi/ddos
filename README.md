# 🚀 Full Bypass Cloudflare + CAPTCHA Attack Script (`gas_2505.py`)

Script Python ini digunakan untuk melakukan pengujian keamanan terhadap website yang dilindungi oleh **Cloudflare** dan **JavaScript Challenge**, termasuk **reCAPTCHA** dan **Turnstile CAPTCHA**.

Script ini:
- Menggunakan **Playwright** headless browser (bukan request biasa)
- Mendukung proxy dengan autentikasi (user:pass)
- Deteksi otomatis challenge, solve CAPTCHA via **CapMonster** & **2Captcha**
- Auto-crawl path berat dari halaman utama (untuk overload)
- Auto buka banyak tab untuk simulasi traffic real-user
- Mendukung stealth dan bypass fingerprint anti-bot

---

## 📦 Requirements

Python 3.8+  
Pastikan sudah install dependencies berikut:

```bash
pip install -r gas_2505requirements.txt
playwright install
```

---

## 📁 File

- `gas_2505.py` → Script utama
- `gas_2505requirements.txt` → Berisi:
  ```
  playwright==1.44.0
  httpx==0.27.0
  psutil==5.9.8
  ```

---

## ⚙️ Cara Instal Otomatis (VPS)

Copy dan paste ini ke VPS ( PASTIKAN SUDAH PUBLIC ):

```bash
cd /root && \
wget -q https://raw.githubusercontent.com/CandraRudi/ddos/main/gas_2505.py && \
wget -q https://raw.githubusercontent.com/CandraRudi/ddos/main/gas_2505requirements.txt && \
pip3 install -r gas_2505requirements.txt && \
playwright install && \
python3 gas_2505.py
```

---

## ✨ Fitur Unggulan

- 🔐 **Stealth Mode** (headless + fingerprint evasion)
- 🤖 **CAPTCHA Auto Solve** (reCAPTCHA + Turnstile)
- 🌐 **Proxy Full Auth Support** (ip:port:user:pass)
- 🔎 Auto crawl endpoint berat (kategori, tag, author)
- 💣 Real-user behavior (click, scroll, multi-tab brute)
- 📊 Log serangan lengkap tersimpan di `log_attack.json`
- 🧠 AI decision: skip serangan jika CPU > 90%

---

## 📝 Contoh Proxy Format

Masukkan ke file `/var/www/html/proxy_new.txt`

```
ip:port:username:password
```

Contoh:

```
194.113.119.228:6902:ayoungcyber:ganasbro
```

---

## 📂 File `log_attack.json` (Hasil Serangan)

Tersimpan otomatis di:
```
/var/www/html/log_attack.json
```

Berisi:
```json
{
  "timestamp": "2025-05-25 14:40:31",
  "target": "https://target.com",
  "success": 87,
  "fail": 13,
  "captcha_2captcha": 2,
  "captcha_capmonster": 5,
  "captcha_jschallenge": true,
  "captcha_sitekey_found": true
}
```

---

## 🧩 Note

- Pastikan **CapMonster** atau **2Captcha** aktif (ganti API key di dalam file)
- Gunakan VPS 2–4 core minimal agar bisa multi-tab
- Proxies sangat mempengaruhi hasil (gunakan yang fresh dan aktif)

---

## ⚠️ Disclaimer

Script ini dibuat untuk keperluan **pengujian keamanan internal**.  
**DILARANG** digunakan untuk tindakan ilegal tanpa izin.
