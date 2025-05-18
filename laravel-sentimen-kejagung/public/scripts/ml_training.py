import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
import pickle

# 🔄 Koneksi langsung ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# Ambil data komentar dan label hasil VADER
query = """
    SELECT comment_translate, label_vader 
    FROM komentar_sentimen_vader
    WHERE comment_translate IS NOT NULL AND label_vader IS NOT NULL
"""
data = pd.read_sql(query, engine)

# Load vectorizer
with open('public/scripts/tfidf_model.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Vectorize data
X = vectorizer.transform(data['comment_translate'])
y = data['label_vader']

# Inisialisasi model Machine Learning
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Training model
print("🔄 Melakukan Training Model...")
model.fit(X, y)
print("✅ Model berhasil dilatih.")

# Simpan model ke file .pkl
with open('public/scripts/ml_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Model berhasil disimpan sebagai ml_model.pkl")
