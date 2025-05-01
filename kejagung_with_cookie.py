# py kejagung_with_cookie.py

# TikTok Scraping & Sentiment Full Automation with Login Cookie
import os
import time
import json
import re
import datetime
import pymysql
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# --- Setup IndoBERT ---
indobert_model_name = "w11wo/indonesian-roberta-base-sentiment-classifier"
indobert_tokenizer = AutoTokenizer.from_pretrained(indobert_model_name)
indobert_model = AutoModelForSequenceClassification.from_pretrained(
    indobert_model_name)

# --- Setup VADER ---
vader_analyzer = SentimentIntensityAnalyzer()

# --- Setup DB ---
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="analisis_sentimen_kejagung_db",
    charset='utf8mb4'
)
cursor = db.cursor()

# --- Cleaning function ---


def clean_comment(text):
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"
                               u"\u3030"
                               "]", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- Sentiment logic ---


def vader_sentiment(comment):
    score = vader_analyzer.polarity_scores(comment)
    if score['compound'] >= 0.05:
        return 'positif', score['compound']
    elif score['compound'] <= -0.05:
        return 'negatif', score['compound']
    else:
        return 'netral', score['compound']


def indobert_sentiment(comment):
    inputs = indobert_tokenizer(
        comment, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = indobert_model(**inputs)
    prediction = outputs.logits.argmax(dim=1).item()
    confidence = outputs.logits.softmax(dim=1)[0][prediction].item()
    label = ['negatif', 'netral', 'positif'][prediction]
    return label, confidence


def hybrid_sentiment(vader_label, vader_score, indo_label, indo_conf):
    if vader_label == indo_label:
        return indo_label
    elif indo_conf >= 0.90:
        return indo_label
    elif indo_conf >= 0.75 and abs(vader_score) >= 0.3 and vader_label == indo_label:
        return indo_label
    return 'netral'

# --- Simpan ke DB ---


def insert_to_db(data):
    sql = """
        INSERT INTO komentar_tiktok (
            video_id, kata_kunci, username, user_id, comment,
            cleaned_comment, likes, replies, date,
            vader_sentiment, vader_score,
            indobert_sentiment, indobert_confidence,
            hybrid_sentiment
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        data['video_id'], data['kata_kunci'], data['username'], data['user_id'],
        data['comment'], data['cleaned_comment'], data['likes'], data['replies'], data['date'],
        data['vader_sentiment'], data['vader_score'],
        data['indobert_sentiment'], data['indobert_confidence'],
        data['hybrid_sentiment']
    ))
    db.commit()

# --- Cek apakah video sudah ada ---


def video_sudah_ada(video_url):
    sql = "SELECT COUNT(*) FROM komentar_tiktok WHERE video_id = %s"
    cursor.execute(sql, (video_url,))
    result = cursor.fetchone()
    return result[0] > 0

# --- Cookie handling ---


def save_cookies(driver, filepath):
    with open(filepath, 'w') as file:
        json.dump(driver.get_cookies(), file)


def load_cookies(driver, filepath):
    with open(filepath, 'r') as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)


# --- Selenium Driver ---
options = Options()
# options.add_argument ("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

# --- Login TikTok dan load cookie jika tersedia ---
# jksaagung@gmail.com
# Ni24#ggA4F4orAn
cookie_file = 'tiktok_cookies.json'
if not os.path.exists(cookie_file):
    driver.get("https://www.tiktok.com/login")
    print("Silakan login manual di browser yang terbuka...")
    input("Tekan Enter setelah selesai login...")
    save_cookies(driver, cookie_file)
else:
    driver.get("https://www.tiktok.com")
    load_cookies(driver, cookie_file)
    driver.refresh()
    time.sleep(3)

# --- Fungsi scraping ---


def scrape_tiktok_by_hashtag(tag):
    driver.get(f"https://www.tiktok.com/search?q=%23{tag}")
    time.sleep(5)
    for _ in range(2):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)
    links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
    video_urls = []
    for link in links:
        href = link.get_attribute("href")
        if "/video/" in href and not video_sudah_ada(href):
            video_urls.append(href)
        if len(video_urls) >= 3:
            break
    return video_urls

# --- Ambil komentar dan proses ---


def proses_video(video_url, tagar):
    print(f"▶️ Memproses: {video_url}")
    try:
        parts = video_url.split("/video/")
        username = parts[0].split("/@")[-1]
        aweme_id = parts[1]
        api_url = f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={aweme_id}&cursor=0&count=100"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Referer": video_url
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        comments = data.get('comments')
        if not comments:
            return
        for item in comments:
            raw = item.get('text', '')
            cleaned = clean_comment(raw)
            if len(cleaned.split()) < 4:
                continue
            user = item.get('user', {})
            likes = item.get('digg_count', 0)
            date = datetime.datetime.fromtimestamp(
                item.get('create_time', 0)).strftime('%Y-%m-%d %H:%M:%S')
            vader_label, vader_score = vader_sentiment(cleaned)
            indo_label, indo_conf = indobert_sentiment(cleaned)
            final = hybrid_sentiment(
                vader_label, vader_score, indo_label, indo_conf)
            insert_to_db({
                "video_id": f"@{username}/video/{aweme_id}",
                "kata_kunci": tagar,
                "username": user.get('nickname', 'unknown'),
                "user_id": user.get('id', 'unknown'),
                "comment": raw,
                "cleaned_comment": cleaned,
                "likes": likes,
                "replies": item.get('reply_comment_total', 0),
                "date": date,
                "vader_sentiment": vader_label,
                "vader_score": round(vader_score, 3),
                "indobert_sentiment": indo_label,
                "indobert_confidence": round(indo_conf, 3),
                "hybrid_sentiment": final
            })
        print(f"✅ Komentar berhasil disimpan dari video {aweme_id}")
    except Exception as e:
        print(f"❌ Error: {e}")


# --- Eksekusi utama ---
hashtags = ["kejaksaanagung", "kinerjakejaksaanagung", "kejagung",
            "kejaksaan", "kejaksaan agung", "kinerja kejaksaan agung"]
for tag in hashtags:
    urls = scrape_tiktok_by_hashtag(tag)
    for url in urls:
        proses_video(url, tag)

driver.quit()
print("\n✅ Semua proses selesai.")
