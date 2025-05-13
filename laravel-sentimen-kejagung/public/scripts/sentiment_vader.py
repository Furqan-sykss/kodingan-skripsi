from sqlalchemy import create_engine, text
from deep_translator import GoogleTranslator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import nltk
import logging

# 🔄 Setup logging
logging.basicConfig(filename='vader_analysis_log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("🚀 Memulai proses analisis VADER...")

# 🔄 Unduh lexicon VADER jika belum ada
nltk.download("vader_lexicon")
analyzer = SentimentIntensityAnalyzer()

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

# 🔄 Query untuk mengambil komentar yang belum dianalisis
select_query = """
    SELECT id, video_id, username, comment, tanggal_komentar
    FROM komentar_mentah
    WHERE is_processed_vader = 0
    LIMIT 100
"""

# ✅ Fungsi untuk membersihkan teks


def bersihkan_teks(teks):
    import re
    teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
    teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
    teks = teks.lower()
    return teks.strip()

# ✅ Fungsi untuk menterjemahkan komentar ke Bahasa Inggris


def translate_comment(teks):
    try:
        translated = GoogleTranslator(
            source='auto', target='en').translate(teks)
        logging.info(f"📝 Terjemahan berhasil: {translated}")
        return translated
    except Exception as e:
        logging.error(f"❌ Terjadi kesalahan saat translate: {e}")
        return teks  # Jika gagal, kembalikan teks asli

# ✅ Fungsi untuk melakukan analisis sentimen


def analyze_sentiment(teks):
    scores = analyzer.polarity_scores(teks)
    pos = scores['pos']
    neu = scores['neu']
    neg = scores['neg']
    compound = scores['compound']

    # Label sentimen
    if compound >= 0.05:
        vader_label = 'positif'
    elif compound <= -0.05:
        vader_label = 'negatif'
    else:
        vader_label = 'netral'

    return {
        "positif": pos,
        "netral": neu,
        "negatif": neg,
        "compound": compound,
        "label": vader_label
    }

# ✅ Fungsi untuk menyimpan hasil analisis ke database


def save_to_database(conn, data):
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
        conn.execute(text(insert_query), data)
        logging.info(f"✅ Data berhasil disimpan untuk ID: {data['mentah_id']}")
    except Exception as e:
        logging.error(f"❌ Gagal menyimpan ke database: {e}")

# ✅ Fungsi untuk mengupdate status di database


def update_status(conn, mentah_id):
    update_query = """
        UPDATE komentar_mentah
        SET is_processed_vader = 1
        WHERE id = :id
    """
    try:
        result = conn.execute(text(update_query), {"id": mentah_id})
        conn.commit()
        if result.rowcount > 0:
            logging.info(
                f"✅ Status is_processed_vader = 1 untuk ID {mentah_id}")
        else:
            logging.warning(f"⚠️ ID {mentah_id} tidak ditemukan untuk update.")
    except Exception as e:
        logging.error(f"❌ Gagal update status: {e}")

# ✅ Fungsi utama yang akan dipanggil oleh Flask API


def run_vader_analysis():
    print("🚀 Memulai Analisis VADER...")
    logging.info("🚀 Memulai Analisis VADER...")

    with engine.begin() as conn:
        rows = conn.execute(text(select_query)).fetchall()

        for row in rows:
            try:
                # Ambil data komentar
                mentah_id = row.id
                video_id = row.video_id
                username = row.username
                original_comment = row.comment
                tanggal_komentar = row.tanggal_komentar

                # Preprocessing dan Translate
                cleaned_comment = bersihkan_teks(original_comment)
                translated_comment = translate_comment(cleaned_comment)

                # Analisis Sentimen
                sentiment_result = analyze_sentiment(translated_comment)

                # Data untuk diinsert ke database
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

                # ✅ Simpan ke database
                save_to_database(conn, data_to_save)

                # ✅ Update status komentar
                update_status(conn, mentah_id)

            except Exception as e:
                logging.error(
                    f"❌ Terjadi error saat memproses komentar ID {row.id}: {e}")
    print("✅ Analisis VADER selesai.")
    logging.info("✅ Analisis VADER selesai.")
