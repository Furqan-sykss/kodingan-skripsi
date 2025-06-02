from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from deep_translator import GoogleTranslator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import nltk
import logging
import json
import re
import os

# 🔄 Setup logging
logging.basicConfig(filename='vader_analysis_log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("🚀 Memulai proses analisis VADER...")

# 🔄 Unduh lexicon VADER
nltk.download("vader_lexicon")
analyzer = SentimentIntensityAnalyzer()

# ✅ Load kamus normalisasi
with open("public/scripts/kamus_normalisasi.json", "r", encoding="utf-8") as file:
    normalization_dict = json.load(file)

# 🔄 Konfigurasi koneksi database
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "analisis_sentimen_kejagung_db"
}
db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)

# 🔄 Query komentar mentah
select_query = """
    SELECT id, video_id, username, comment, tanggal_komentar
    FROM komentar_mentah
    WHERE is_processed_vader = 0 AND is_processed_ml = 0
    LIMIT 300
"""

# ✅ Fungsi pembersihan teks


def bersihkan_teks(teks):
    teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
    teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
    teks = re.sub(r'\s+', ' ', teks)
    return teks.lower().strip()

# ✅ Fungsi normalisasi dengan kamus


def normalisasi_kata(teks):
    kata_list = teks.split()
    hasil = [normalization_dict.get(kata, kata) for kata in kata_list]
    return " ".join(hasil)

# ✅ Fungsi translasi


def translate_comment(teks):
    try:
        translated = GoogleTranslator(
            source='auto', target='en').translate(teks)
        logging.info(f"📝 Translasi berhasil: {translated}")
        return translated
    except Exception as e:
        logging.error(f"❌ Gagal translasi: {e}")
        return teks

# ✅ Fungsi analisis sentimen dengan VADER


def analyze_sentiment(teks):
    scores = analyzer.polarity_scores(teks)
    compound = scores['compound']

    label = 'netral'
    if compound >= 0.05:
        label = 'positif'
    elif compound <= -0.05:
        label = 'negatif'

    return {
        "positif": scores['pos'],
        "netral": scores['neu'],
        "negatif": scores['neg'],
        "compound": compound,
        "label": label
    }

# ✅ Simpan ke database


def save_to_database(session, data):
    insert_query = """
        INSERT INTO komentar_sentimen_vader (
            mentah_id, video_id, username, tanggal_komentar, comment,
            cleaned_comment, comment_translate, vader_pos, vader_neu,
            vader_neg, compound_score, label_vader, processed_at
        ) VALUES (
            :mentah_id, :video_id, :username, :tanggal_komentar, :original_comment,
            :cleaned_comment, :translated_comment, :score_positif, :score_netral,
            :score_negatif, :compound_score, :vader_sentiment, :created_at
        )
    """
    try:
        session.execute(text(insert_query), data)
        logging.info(f"✅ Data berhasil disimpan untuk ID: {data['mentah_id']}")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan ke database: {e}")
        raise

# ✅ Update status komentar


def update_status(session, mentah_id):
    update_query = """
        UPDATE komentar_mentah
        SET is_processed_vader = 1
        WHERE id = :id
    """
    try:
        result = session.execute(text(update_query), {"id": mentah_id})
        if result.rowcount > 0:
            logging.info(
                f"✅ Status is_processed_vader = 1 untuk ID {mentah_id}")
        else:
            logging.warning(f"⚠️ ID {mentah_id} tidak ditemukan.")
    except Exception as e:
        logging.error(f"❌ Gagal update status: {e}")
        raise

# ✅ Fungsi utama


def run_vader_analysis():
    print("🚀 Memulai Analisis VADER...")
    logging.info("🚀 Memulai Analisis VADER...")

    session = Session()
    try:
        rows = session.execute(text(select_query)).fetchall()
        for row in rows:
            try:
                mentah_id = row.id
                video_id = row.video_id
                username = row.username
                original_comment = row.comment
                tanggal_komentar = row.tanggal_komentar

                cleaned_comment = bersihkan_teks(original_comment)
                normalized_comment = normalisasi_kata(cleaned_comment)
                translated_comment = translate_comment(normalized_comment)
                sentiment_result = analyze_sentiment(translated_comment)

                data_to_save = {
                    "mentah_id": mentah_id,
                    "video_id": video_id,
                    "username": username,
                    "tanggal_komentar": tanggal_komentar,
                    "original_comment": original_comment,
                    "cleaned_comment": cleaned_comment,
                    "translated_comment": translated_comment,
                    "score_positif": sentiment_result["positif"],
                    "score_netral": sentiment_result["netral"],
                    "score_negatif": sentiment_result["negatif"],
                    "compound_score": sentiment_result["compound"],
                    "vader_sentiment": sentiment_result["label"],
                    "created_at": datetime.now()
                }

                save_to_database(session, data_to_save)
                update_status(session, mentah_id)
                session.commit()

                print(f"✅ Berhasil memproses komentar ID {mentah_id}")
                logging.info(f"✅ Komentar ID {mentah_id} selesai")

            except Exception as e:
                logging.error(f"❌ Error komentar ID {row.id}: {e}")
                session.rollback()
                print(f"❌ Error komentar ID {row.id}: {e}")
    finally:
        session.close()
        print("✅ Analisis VADER selesai.")
        logging.info("✅ Analisis VADER selesai.")
