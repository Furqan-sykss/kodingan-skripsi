import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

# 🔄 Koneksi langsung ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# Ambil data hasil translate VADER untuk di-vectorize
query = """
    SELECT comment_translate 
    FROM komentar_sentimen_vader
    WHERE comment_translate IS NOT NULL
"""
data = pd.read_sql(query, engine)

# Inisialisasi TF-IDF Vectorizer
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(data['comment_translate'])

# Simpan model TF-IDF ke file .pkl
with open('public/scripts/tfidf_model.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print("✅ TF-IDF Vectorizer berhasil dibuat dan disimpan sebagai tfidf_model.pkl")
