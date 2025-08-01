#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import random
import logging
import datetime
import requests
import pymysql
from typing import List, Set
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------------------------------------------
# 1. Setup Logger
# ------------------------------------------------------------------------------
logger = logging.getLogger("tiktok_url_crawler")
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

fh = logging.FileHandler("crawling_by_url.log", encoding="utf-8")
fh.setFormatter(fmt)
logger.addHandler(fh)

sh = logging.StreamHandler()
sh.setFormatter(fmt)
logger.addHandler(sh)

# ------------------------------------------------------------------------------
# 2. Load environment variables
# ------------------------------------------------------------------------------
load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USERNAME")
DB_PASS = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_DATABASE")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE_PATH = os.path.join(SCRIPT_DIR, "tiktok_cookies.json")

# ------------------------------------------------------------------------------
# 3. List of video URLs to crawl
# ------------------------------------------------------------------------------
VIDEO_URLS = [
    # contoh URL TikTok; ganti dengan daftar yang kamu butuhkan
    "https://www.tiktok.com/@some_user/video/7123456789012345678",
    "https://www.tiktok.com/@another_user/video/7987654321098765432",
]

# ------------------------------------------------------------------------------
# 4. Utility functions
# ------------------------------------------------------------------------------


def komentar_valid(teks: str) -> bool:
    teks = teks.strip()
    return len(teks.split()) >= 2 and not re.fullmatch(r"[^\w\s]+", teks)


def get_db_connection() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )


def get_selenium_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # gunakan UA default Chrome agar lebih legit
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(120)
    return driver


def load_cookies_to_driver(driver: webdriver.Chrome, path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        driver.get("https://www.tiktok.com")
        time.sleep(3)
        for cookie in cookies:
            for k in ("storeId", "id", "hostOnly", "session", "expirationDate"):
                cookie.pop(k, None)
            if cookie.get("domain", "").startswith("."):
                cookie["domain"] = cookie["domain"].lstrip(".")
            if "sameSite" in cookie:
                s = cookie["sameSite"].lower()
                if s in ("unspecified", "no_restriction"):
                    cookie.pop("sameSite", None)
            driver.add_cookie(cookie)
        logger.debug("✅ Cookies dimuat ke driver")
        return True
    except Exception as e:
        logger.error(f"❌ Gagal load cookies: {e}")
        return False


def build_session_from_driver(driver: webdriver.Chrome) -> requests.Session:
    sess = requests.Session()
    # tiru cookies
    for c in driver.get_cookies():
        sess.cookies.set(c["name"], c["value"], domain=c["domain"])
    # tiru User-Agent asli dari browser
    ua = driver.execute_script("return navigator.userAgent;")
    sess.headers.update({
        "User-Agent": ua,
        "Accept": "application/json"
    })
    return sess


def fetch_all_comments(
    session: requests.Session,
    aweme_id: str,
    referer_url: str,
    max_retries: int = 3
) -> List[dict]:
    """
    Paginate lewat API TikTok hingga has_more=0.
    Sertakan Referer & UA asli, retry jika gagal.
    """
    api_url = "https://www.tiktok.com/api/comment/list/"
    all_comments: List[dict] = []
    cursor = 0

    while True:
        params = {
            "aid": 1988,
            "aweme_id": aweme_id,
            "cursor": cursor,
            "count": 100
        }
        headers = {
            "Referer": referer_url
        }

        for attempt in range(1, max_retries + 1):
            try:
                resp = session.get(api_url, params=params,
                                   headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt}/{max_retries} gagal: {e}")
                time.sleep(attempt * 2)
        else:
            logger.error(f"Gagal fetch aweme_id={aweme_id} cursor={cursor}")
            return all_comments

        comments = data.get("comments", [])
        all_comments.extend(comments)

        has_more = data.get("has_more", 0)
        next_cursor = data.get("cursor", 0)
        logger.debug(
            f"Fetched batch {len(comments)} | total so far {len(all_comments)} | "
            f"has_more={has_more} | cursor={cursor}->{next_cursor}"
        )

        if not has_more:
            break

        cursor = next_cursor
        time.sleep(random.uniform(1, 2))

    return all_comments


def get_existing_comments(
    cursor: pymysql.cursors.DictCursor,
    video_url: str
) -> Set[str]:
    sql = "SELECT comment FROM komentar_mentah_url WHERE video_id = %s"
    cursor.execute(sql, (video_url,))
    return {row["comment"] for row in cursor.fetchall()}


def insert_comments(
    db: pymysql.connections.Connection,
    cursor: pymysql.cursors.DictCursor,
    video_url: str,
    comments: List[dict]
) -> int:
    existing = get_existing_comments(cursor, video_url)
    sql = """
        INSERT INTO komentar_mentah_url (
            video_id, username, comment,
            likes, replies, tanggal_komentar,
            is_processed_vader, is_processed_ml, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, 0, 0, NOW())
    """
    saved = 0

    for item in comments:
        teks = item.get("text", "").strip()
        if not komentar_valid(teks) or teks in existing:
            continue

        uname = item.get("user", {}).get("nickname", "unknown")
        likes = item.get("digg_count", 0)
        replies = item.get("reply_comment_total", 0)
        ts = item.get("create_time", 0)
        tanggal = datetime.datetime.fromtimestamp(
            ts).strftime("%Y-%m-%d %H:%M:%S") if ts else None

        try:
            cursor.execute(
                sql, (video_url, uname, teks, likes, replies, tanggal))
            saved += 1
            existing.add(teks)
        except pymysql.MySQLError as e:
            logger.error(f"DB insert gagal: {e}")

    db.commit()
    return saved

# ------------------------------------------------------------------------------
# 5. Main workflow
# ------------------------------------------------------------------------------


def crawl_videos(video_urls: List[str]):
    driver = get_selenium_driver()
    if not load_cookies_to_driver(driver, COOKIE_FILE_PATH):
        logger.error("Abort karena cookies tidak valid.")
        driver.quit()
        return

    session = build_session_from_driver(driver)
    driver.quit()

    db = get_db_connection()
    cursor = db.cursor()
    total_new = 0

    for url in video_urls:
        logger.info(f"➡️ Memproses: {url}")
        parts = url.rstrip("/").split("/video/")
        if len(parts) < 2:
            logger.warning(f"URL invalid, dilewati: {url}")
            continue
        aweme_id = parts[1]

        comments = fetch_all_comments(session, aweme_id, url)
        logger.info(f"Total komentar di-fetch: {len(comments)}")

        new_count = insert_comments(db, cursor, url, comments)
        logger.info(f"✨ {new_count} komentar baru disimpan untuk {url}")
        total_new += new_count

        # jeda antar video
        time.sleep(random.uniform(2, 4))

    cursor.close()
    db.close()
    logger.info(f"✔️ Selesai semua video. Total komentar baru: {total_new}")


if __name__ == "__main__":
    crawl_videos(VIDEO_URLS)
