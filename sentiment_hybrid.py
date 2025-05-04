import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# Koneksi DB
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# Gabungkan berdasarkan mentah_id
vader = pd.read_sql("SELECT * FROM komentar_vader", engine)
bert = pd.read_sql("SELECT * FROM komentar_indobert", engine)

merged = pd.merge(vader, bert, on="mentah_id", suffixes=('_vader', '_bert'))

# Hybrid: mayoritas / confidence


def hybrid_label(row):
    if row['label_vader'] == row['label_bert']:
        return row['label_vader']
    return row['label_bert'] if row['confidence'] > 0.75 else row['label_vader']


merged['hybrid'] = merged.apply(hybrid_label, axis=1)

final_data = merged[[
    'mentah_id',
    'comment_original_vader',
    'translated_comment',
    'cleaned_comment_vader',
    'label_vader',
    'compound',
    'label_bert',
    'confidence',
    'hybrid'
]]
final_data['processed_at'] = datetime.now()

# Simpan ke komentar_final
final_data.to_sql("komentar_final", con=engine,
                  if_exists="append", index=False)
print("✅ Hybrid selesai.")
