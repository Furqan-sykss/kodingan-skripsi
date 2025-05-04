import re
import json
import time
import datetime
import requests
import pymysql
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Unduh resources NLTK
nltk.download('stopwords')
nltk.download('punkt')

# Koneksi ke database
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="analisis_sentimen_kejagung_db",
    charset='utf8mb4'
)
cursor = db.cursor()

stop_words = set(stopwords.words('indonesian'))

kata_penting = {
    'tidak', 'bukan', 'jangan', 'kurang', 'belum', 'gagal', 'buruk', 'salah', 'lemah', 'lambat',
    'baik', 'bagus', 'puas', 'hebat', 'mantap', 'berhasil', 'cepat', 'terbaik',
    'kecewa', 'senang', 'sedih', 'benci', 'suka', 'marah', 'malu', 'bosan', 'aneh', 'menyenangkan', 'mengecewakan',
    'terlalu', 'parah', 'kacau', 'payah', 'hancur', 'terburuk', 'tercepat', 'terlambat',
    'support', 'dukungan', 'cinta', 'percaya', 'bohong', 'kinerja', 'kerja', 'adil', 'tegas', 'korupsi', 'tindak', 'nyata'
}

stop_words -= kata_penting

# Fungsi preprocessing


def bersihkan_komentar(teks):
    teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
    teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
    teks = teks.lower()
    tokens = word_tokenize(teks)
    bersih = [t for t in tokens if t not in stop_words and len(t) > 1]
    return " ".join(bersih)

# Cek apakah video sudah ada


def video_sudah_ada(video_url):
    sql = "SELECT COUNT(*) FROM komentar_mentah WHERE video_id = %s"
    cursor.execute(sql, (video_url,))
    result = cursor.fetchone()
    return result[0] > 0

# Simpan komentar ke DB


def simpan_komentar(data):
    sql = """
        INSERT INTO komentar_mentah (
            video_id, kata_kunci, username, user_id, comment,
            cleaned_comment, likes, replies, date, is_processed, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, NOW())
    """
    cursor.execute(sql, (
        data['video_id'],
        data['kata_kunci'],
        data['username'],
        data['user_id'],
        data['comment'],
        data['cleaned_comment'],
        data['likes'],
        data['replies'],
        data['date']
    ))
    db.commit()

# Load cookie dari file JSON


def load_cookies(driver, cookie_file):
    with open(cookie_file, "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            cookie.pop("storeId", None)
            cookie.pop("id", None)
            if "sameSite" in cookie:
                if cookie["sameSite"].lower() in ["no_restriction", "unspecified"]:
                    cookie["sameSite"] = "None"
            if cookie.get("domain", "").startswith("."):
                cookie["domain"] = cookie["domain"].lstrip(".")
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Gagal tambah cookie: {cookie.get('name')} - {e}")

# Fungsi scraping berdasarkan hashtag


def scraping_by_hashtag(tagar, max_videos=3, max_comments=100):
    print(f"\n🔍 Scraping untuk tagar: #{tagar}")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.tiktok.com")
    time.sleep(5)
    load_cookies(driver, "tiktok_cookies.json")
    driver.get(f"https://www.tiktok.com/search?q=%23{tagar}")
    time.sleep(5)

    for _ in range(2):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)

    links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
    collected = set()
    for link in links:
        href = link.get_attribute("href")
        if "/video/" in href and not video_sudah_ada(href):
            collected.add(href)
        if len(collected) >= max_videos:
            break

    for video_url in collected:
        print(f"🎥 Memproses: {video_url}")
        try:
            parts = video_url.split("/video/")
            username = parts[0].split("/@")[-1]
            aweme_id = parts[1]

            url = f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={aweme_id}&cursor=0&count={max_comments}"
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "Referer": video_url
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            comments = data.get('comments', [])

            if not comments:
                print(f"❌ Tidak ada komentar pada {video_url}")
                continue

            for item in comments:
                raw_comment = item.get('text', '')
                user = item.get('user', {})
                user_nickname = user.get('nickname', 'unknown')
                user_id = user.get('id', 'unknown')
                likes = item.get('digg_count', 0)
                replies = item.get('reply_comment_total', 0)
                unix_date = item.get('create_time', 0)

                date_normal = datetime.datetime.fromtimestamp(unix_date).strftime(
                    '%Y-%m-%d %H:%M:%S') if unix_date else None

                simpan_komentar({
                    "video_id": f"@{username}/video/{aweme_id}",
                    "kata_kunci": tagar,
                    "username": user_nickname,
                    "user_id": user_id,
                    "comment": raw_comment,
                    "cleaned_comment": bersihkan_komentar(raw_comment),
                    "likes": likes,
                    "replies": replies,
                    "date": date_normal
                })

            print(f"✅ Selesai simpan komentar untuk video {aweme_id}")
            time.sleep(2)

        except Exception as e:
            print(f"❌ Gagal proses video {video_url}: {e}")
            continue

    driver.quit()


# Jalankan program
if __name__ == '__main__':
    hashtags = ["kinerja kejaksaan agung", "kinerjakejaksaanagung",
                "kejaksaanagung", "kejagung", "kejaksaan"]
    for tag in hashtags:
        scraping_by_hashtag(tag)
    print("\n✅ Semua komentar berhasil disimpan ke database (komentar_mentah).")
