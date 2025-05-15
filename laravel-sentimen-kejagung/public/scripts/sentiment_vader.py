from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
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
Session = sessionmaker(bind=engine)

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
    return teks.lower().strip()

# ✅ Fungsi untuk menterjemahkan komentar ke Bahasa Inggris


def translate_comment(teks):
    try:
        translated = GoogleTranslator(
            source='auto', target='en').translate(teks)
        logging.info(f"📝 Terjemahan berhasil: {translated}")
        return translated
    except Exception as e:
        logging.error(f"❌ Terjadi kesalahan saat translate: {e}")
        return teks

# ✅ Fungsi untuk melakukan analisis sentimen


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

# ✅ Fungsi untuk menyimpan hasil analisis ke database


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

# ✅ Fungsi untuk mengupdate status di database


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
            logging.warning(f"⚠️ ID {mentah_id} tidak ditemukan untuk update.")
    except Exception as e:
        logging.error(f"❌ Gagal update status: {e}")
        raise

# ✅ Fungsi utama yang akan dipanggil oleh Flask API


def run_vader_analysis():
    print("🚀 Memulai Analisis VADER...")
    logging.info("🚀 Memulai Analisis VADER...")

    # ✅ Mulai sesi SQLAlchemy
    session = Session()

    try:
        rows = session.execute(text(select_query)).fetchall()

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

                # Data untuk disimpan ke database
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

                # ✅ Simpan hasil analisis
                save_to_database(session, data_to_save)

                # ✅ Update status komentar
                update_status(session, mentah_id)

                # ✅ Commit setelah selesai per baris
                session.commit()

                logging.info(f"✅ Berhasil memproses komentar ID {mentah_id}")
                print(f"✅ Berhasil memproses komentar ID {mentah_id}")

            except Exception as e:
                logging.error(
                    f"❌ Error saat memproses komentar ID {row.id}: {e}")
                session.rollback()
                print(f"❌ Error saat memproses komentar ID {row.id}: {e}")

    finally:
        session.close()
        print("✅ Analisis VADER selesai.")
        logging.info("✅ Analisis VADER selesai.")
