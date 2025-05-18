import pandas as pd
from sqlalchemy import create_engine

# 🔄 Koneksi ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db"
)

# 🔍 Ambil data hasil prediksi dan label asli
query = """
    SELECT 
        cleaned_comment,
        vader_pos,
        vader_neu,
        vader_neg,
        compound_score,
        ground_truth_label
    FROM 
        komentar_sentimen_vader
    WHERE 
        ground_truth_label IS NOT NULL
"""
df = pd.read_sql(query, engine)

# ✅ Tampilkan data sample
print(df.head())

# ✅ Simpan sebagai CSV
df.to_csv('vader_labeled_data.csv', index=False)
print("\nData berhasil diekstraksi dan disimpan sebagai 'vader_labeled_data.csv'")
