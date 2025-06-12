# -*- coding: utf-8 -*-
import re
import json
import time
import datetime
import requests
import pymysql
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv

# ✅ Logging
logging.basicConfig(
    filename='scraping_log.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logging.debug("🚀 Memulai proses scraping...")

# ✅ Load .env
load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(os.path.dirname(__file__)), '.env'))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(SCRIPT_DIR, 'chromedriver.exe')
COOKIE_FILE_PATH = os.path.join(SCRIPT_DIR, 'tiktok_cookies.json')

# ✅ Validasi komentar


def komentar_valid(teks):
    teks = teks.strip()
    if len(teks.split()) < 2:
        return False
    if re.fullmatch(r"[^\w\s]+", teks):
        return False
    return True


def load_cookies(driver, cookie_path):
    try:
        with open(cookie_path, "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                cookie.pop("storeId", None)
                cookie.pop("id", None)
                if "sameSite" in cookie and cookie["sameSite"].lower() in ["no_restriction", "unspecified"]:
                    cookie["sameSite"] = "None"
                if cookie.get("domain", "").startswith("."):
                    cookie["domain"] = cookie["domain"].lstrip(".")
                driver.add_cookie(cookie)
        logging.debug("✅ Cookies dimuat.")
    except Exception as e:
        logging.error(f"❌ Gagal memuat cookies: {e}")


def scraping_by_hashtag(tagar, db, cursor, max_videos=5, max_comments=100):
    logging.debug(f"\n🔍 Scraping untuk tagar: #{tagar}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0')

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(240)

    komentar_disimpan = 0

    try:
        driver.get("https://www.tiktok.com")
        time.sleep(5)
        load_cookies(driver, COOKIE_FILE_PATH)
        driver.get(f"https://www.tiktok.com/search?q=%23{tagar}")
        time.sleep(5)

        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
        collected = set()
        for link in links:
            href = link.get_attribute("href")
            if "/video/" in href:
                collected.add(href)
            if len(collected) >= max_videos:
                break

        for video_url in collected:
            logging.debug(f"🎥 Memproses: {video_url}")
            parts = video_url.split("/video/")
            if len(parts) < 2:
                continue
            aweme_id = parts[1]

            api_url = f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={aweme_id}&cursor=0&count={max_comments}"
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "Referer": video_url
            }

            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            comments = data.get('comments', [])

            for item in comments:
                raw_comment = item.get('text', '')
                if not komentar_valid(raw_comment):
                    continue

                user_nickname = item.get('user', {}).get('nickname', 'unknown')
                likes = item.get('digg_count', 0)
                replies = item.get('reply_comment_total', 0)
                unix_date = item.get('create_time', 0)

                tanggal_komentar = datetime.datetime.fromtimestamp(unix_date).strftime(
                    '%Y-%m-%d %H:%M:%S') if unix_date else None

                try:
                    sql = """
                        INSERT INTO komentar_mentah (
                            video_id, kata_kunci, username, comment, likes, replies, tanggal_komentar,
                            is_processed_vader, is_processed_ml, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 0, NOW())
                    """
                    cursor.execute(sql, (
                        video_url, tagar, user_nickname, raw_comment,
                        likes, replies, tanggal_komentar
                    ))
                    db.commit()
                    komentar_disimpan += 1
                    logging.debug(f"✅ Disimpan: {raw_comment[:40]}...")
                except Exception as e:
                    logging.error(f"❌ Gagal simpan DB: {e}")

    except Exception as e:
        logging.error(f"❌ Gagal scraping: {e}")
    finally:
        driver.quit()
        logging.debug("🛑 Driver ditutup")

    return komentar_disimpan


# ✅ Main untuk dipanggil Flask
def run_scraping():
    try:
        db = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        logging.debug("✅ Koneksi database berhasil.")
    except Exception as e:
        logging.error(f"❌ Koneksi database gagal: {e}")
        return 0

    hashtags = ["kejaksaan agung", "kejagung"]
    total_berhasil = 0
    for tag in hashtags:
        total_berhasil += scraping_by_hashtag(tag, db, cursor)

    db.close()
    logging.debug("🛑 Koneksi database ditutup")
    return total_berhasil
