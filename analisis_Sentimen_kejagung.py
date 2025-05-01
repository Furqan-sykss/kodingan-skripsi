from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import pymysql
import time
import re
import datetime
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# --- Setup model IndoBERT ---
indobert_model_name = "w11wo/indonesian-roberta-base-sentiment-classifier"
indobert_tokenizer = AutoTokenizer.from_pretrained(indobert_model_name)
indobert_model = AutoModelForSequenceClassification.from_pretrained(
    indobert_model_name)

# --- VADER Sentiment ---
vader_analyzer = SentimentIntensityAnalyzer()

# --- Database Connection ---
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="analisis_sentimen_kejagung_db",
    charset='utf8mb4',
    connect_timeout=60
)
cursor = db.cursor()

# --- Setup Selenium ---
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# --- Cleaning Function ---


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

# --- Sentiment Analysis Functions ---


def vader_sentiment_analysis(comment):
    score = vader_analyzer.polarity_scores(comment)
    if score['compound'] >= 0.05:
        label = 'positif'
    elif score['compound'] <= -0.05:
        label = 'negatif'
    else:
        label = 'netral'
    return label, score['compound']


def indobert_sentiment_analysis(comment):
    inputs = indobert_tokenizer(
        comment, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = indobert_model(**inputs)
    prediction = outputs.logits.argmax(dim=1).item()
    confidence = outputs.logits.softmax(dim=1)[0][prediction].item()
    label = ['negatif', 'netral', 'positif'][prediction]
    return label, float(confidence)


def determine_final_sentiment(vader, indobert, conf):
    if vader == indobert:
        return indobert
    elif conf > 0.8:
        return indobert
    return 'netral'

# --- Check if video already processed ---


def video_sudah_ada(video_url):
    sql = "SELECT COUNT(*) FROM komentar_tiktok WHERE video_id = %s"
    cursor.execute(sql, (video_url,))
    result = cursor.fetchone()
    return result[0] > 0

# --- Save to Database ---


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
        data['video_id'],
        data['kata_kunci'],
        data['username'],
        data['user_id'],
        data['comment'],
        data['cleaned_comment'],
        data['likes'],
        data['replies'],
        data['date'],
        data['vader_sentiment'],
        data['vader_score'],
        data['indobert_sentiment'],
        data['indobert_confidence'],
        data['hybrid_sentiment']
    ))
    db.commit()

# --- Scrape TikTok videos and comments ---


def scrape_and_analyze(tagar, max_videos=3, max_comments=100):
    print(f"\n🔍 Scraping video untuk tagar #{tagar}")
    driver.get(f"https://www.tiktok.com/search?q=%23{tagar}")
    time.sleep(5)

    for _ in range(2):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)

    links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/video/"]')
    collected = set()

    for link in links:
        href = link.get_attribute("href")
        if "/video/" in href and href not in collected and not video_sudah_ada(href):
            collected.add(href)
        if len(collected) >= max_videos:
            break

    for video_url in collected:
        print(f"🎥 Memproses: {video_url}")
        try:
            parts = video_url.split("/video/")
            username = parts[0].split("/@")[-1]
            aweme_id = parts[1]
            api_url = f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={aweme_id}&cursor=0&count={max_comments}"
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json",
                "Referer": video_url
            }
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            comments = data.get('comments')

            if comments is None:
                print(f"❌ Tidak ada komentar ditemukan di video {aweme_id}")
                continue

            for item in comments:
                raw_comment = item.get('text', '')
                cleaned = clean_comment(raw_comment)
                user = item.get('user', {})
                user_nickname = user.get('nickname', 'unknown')
                user_id = user.get('id', 'unknown')
                # ← gunakan field yang benar untuk jumlah suka
                likes = item.get('digg_count', 0)
                unix_date = item.get('create_time', 0)
                replies = item.get('reply_comment_total', 0)

                if unix_date != 0:
                    date_normal = datetime.datetime.fromtimestamp(
                        unix_date).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date_normal = "Unknown"

                vader, vader_score = vader_sentiment_analysis(cleaned)
                indo, conf = indobert_sentiment_analysis(cleaned)
                final = determine_final_sentiment(vader, indo, conf)

                insert_to_db({
                    "video_id": f"@{username}/video/{aweme_id}",
                    "kata_kunci": tagar,
                    "username": user_nickname,
                    "user_id": user_id,
                    "comment": raw_comment,
                    "cleaned_comment": cleaned,
                    "likes": likes,
                    "replies": replies,
                    "date": date_normal,
                    "vader_sentiment": vader,
                    "vader_score": round(vader_score, 3),
                    "indobert_sentiment": indo,
                    "indobert_confidence": round(conf, 3),
                    "hybrid_sentiment": final
                })

            print(f"✅ Komentar berhasil diproses dari video {aweme_id}")
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error pada video {video_url}: {e}")
            continue


# --- Jalankan untuk semua tagar ---
hashtags = ["kejaksaanagung", "kinerjakejaksaanagung", "kejagung",
            "kejaksaan", "kejaksaan agung", "kinerja kejaksaan agung"]
for tagar in hashtags:
    scrape_and_analyze(tagar)

# --- Selesai ---
driver.quit()
print("\n✅ Semua scraping & analisis selesai.")
