import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# 1. Koneksi database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# 2. Ambil mentah_id yang sudah diproses oleh keduanya
query_ids = """
    SELECT id FROM komentar_mentah
    WHERE is_processed_vader = 1 AND is_processed_indobert = 1
"""
processed_ids = pd.read_sql(query_ids, engine)

# 3. Ambil data dari tabel sentimen
vader = pd.read_sql("SELECT * FROM komentar_sentimen_vader", engine)
bert = pd.read_sql("SELECT * FROM komentar_sentimen_indobert", engine)

# 4. Filter data yang sudah diproses dua-duanya
vader = vader[vader['mentah_id'].isin(processed_ids['id'])]
bert = bert[bert['mentah_id'].isin(processed_ids['id'])]

# 5. Merge data berdasarkan mentah_id
merged = pd.merge(vader, bert, on='mentah_id',
                  suffixes=('_vader', '_indobert'))

# 6. Tentukan final_hybrid_label


def hybrid_label(row):
    if row['label_vader'] == row['indobert_sentiment_label']:
        return row['label_vader']
    return row['indobert_sentiment_label'] if row['indobert_confidence_score'] > 0.75 else row['label_vader']


merged['final_hybrid_label'] = merged.apply(hybrid_label, axis=1)
merged['confidence_average_score'] = (
    merged['compound_score'].abs() + merged['indobert_confidence_score']) / 2
merged['processed_at'] = datetime.now()

# 7. Siapkan data akhir sesuai struktur komentar_sentimen_hybrid
final_data = merged[[
    'mentah_id',
    'video_id_vader',
    'username_vader',
    'tanggal_komentar_vader',
    'comment_vader',
    'cleaned_comment_vader',
    'cleaned_comment_indobert',
    'label_vader',
    'compound_score',
    'indobert_sentiment_label',
    'indobert_confidence_score',
    'final_hybrid_label',
    'confidence_average_score',
    'processed_at'
]]

# 8. Rename kolom agar match dengan struktur tabel komentar_sentimen_hybrid
final_data.rename(columns={
    'video_id_vader': 'video_id',
    'username_vader': 'username',
    'tanggal_komentar_vader': 'tanggal_komentar',
    'comment_vader': 'comment',
    'label_vader': 'vader_label',
    'compound_score': 'vader_score',
    'indobert_sentiment_label': 'indobert_label',
    'indobert_confidence_score': 'indobert_score'
}, inplace=True)

# 9. Simpan ke database
final_data.to_sql("komentar_sentimen_hybrid", con=engine,
                  if_exists="append", index=False)
print("✅ Hybrid berhasil disimpan ke DB.")
