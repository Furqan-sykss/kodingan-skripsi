from sqlalchemy import create_engine
import pandas as pd

# Koneksi ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db"
)

# Ambil 20% data secara acak dari tabel komentar_sentimen_vader
query = """
    SELECT id, mentah_id, video_id, username, comment, tanggal_komentar, sentiment_label 
    FROM komentar_sentimen_vader
    ORDER BY RAND()
    LIMIT 320;  -- 20% dari 1600 data
"""
data_uji = pd.read_sql(query, engine)

# Lihat data
print(data_uji.head())
