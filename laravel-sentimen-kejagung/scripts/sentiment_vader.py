from sqlalchemy import create_engine, text
from deep_translator import GoogleTranslator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import nltk

# Unduh lexicon VADER jika belum ada
nltk.download("vader_lexicon")
analyzer = SentimentIntensityAnalyzer()

# Konfigurasi koneksi database
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "analisis_sentimen_kejagung_db"
}
db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(db_url)

# Ambil komentar mentah yang belum dianalisis oleh VADER
select_query = """
    SELECT id, video_id, username, comment, tanggal_komentar
    FROM komentar_mentah
    WHERE is_processed_vader = 0
    LIMIT 100
"""

# Fungsi sederhana untuk preprocessing dasar
def bersihkan_teks(teks):
    import re
    teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
    teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
    teks = teks.lower()
    return teks.strip()

# Proses setiap komentar
with engine.begin() as conn:
    rows = conn.execute(text(select_query)).fetchall()

    for row in rows:
        try:
            mentah_id = row.id
            video_id = row.video_id
            username = row.username
            original_comment = row.comment
            tanggal_komentar = row.tanggal_komentar
            cleaned_comment = bersihkan_teks(original_comment)

            # Translate ke bahasa Inggris
            translated_comment = GoogleTranslator(source='auto', target='en').translate(cleaned_comment)

            # Analisis sentimen
            scores = analyzer.polarity_scores(translated_comment)
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

            # Simpan ke komentar_sentimen_vader
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
            conn.execute(text(insert_query), {
                "mentah_id": mentah_id,
                "video_id": video_id,
                "username": username,
                "tanggal_komentar": tanggal_komentar,
                "original_comment": original_comment,
                "cleaned_comment": cleaned_comment,
                "translated_comment": translated_comment,
                "score_positif": pos,
                "score_netral": neu,
                "score_negatif": neg,
                "compound_score": compound,
                "vader_sentiment": vader_label,
                "created_at": datetime.now()
            })

            # Update status komentar mentah
            conn.execute(text("UPDATE komentar_mentah SET is_processed_vader = 1 WHERE id = :id"), {
                "id": mentah_id
            })

            print(f"Komentar ID {mentah_id} berhasil diproses dengan VADER.")

        except Exception as e:
            print(f"Terjadi error saat memproses komentar ID {row.id}: {e}")
