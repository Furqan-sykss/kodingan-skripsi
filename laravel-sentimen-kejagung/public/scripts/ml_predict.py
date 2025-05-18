import pandas as pd
from sqlalchemy import create_engine, text
from deep_translator import GoogleTranslator
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
from datetime import datetime
import re

# 🔄 Koneksi langsung ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db"
)

# === 1️⃣ Ambil 400 Data Mentah yang Belum Diproses oleh VADER dan ML ===
query = """
    SELECT id, video_id, username, comment, tanggal_komentar 
    FROM komentar_mentah
    WHERE is_processed_ml = 0 AND is_processed_vader = 0
    LIMIT 400
"""
data_mentah = pd.read_sql(query, engine)

print(f"🔎 Jumlah Data yang Diambil: {len(data_mentah)}")
if len(data_mentah) == 0:
    print("❌ Tidak ada data yang diambil dari database.")
    exit()

# === 2️⃣ Preprocessing Data (Sesuai ml_evaluation_with_log.py) ===


def bersihkan_teks(teks):
    # Hapus URL, mention, dan hashtag
    teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
    # Hapus simbol, angka, dan karakter khusus
    teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
    # Lowercase dan hapus spasi di awal/akhir
    teks = teks.lower().strip()
    # Hapus spasi berlebih
    teks = re.sub(r'\s+', ' ', teks)
    return teks


def translate_comment(teks):
    try:
        translated = GoogleTranslator(
            source='auto', target='en').translate(teks)
        return translated
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat translate: {e}")
        return teks


# Proses preprocessing dan translate
data_mentah['cleaned_comment'] = data_mentah['comment'].apply(bersihkan_teks)
data_mentah['comment_translate'] = data_mentah['cleaned_comment'].apply(
    translate_comment)

# === 3️⃣ Load model dan vectorizer ===
with open('public/scripts/tfidf_model.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

with open('public/scripts/ml_model.pkl', 'rb') as f:
    model = pickle.load(f)

# === 4️⃣ Vectorize Data Mentah ===
X_test = vectorizer.transform(data_mentah['comment_translate'])

# === 5️⃣ Prediksi menggunakan model ===
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)

# Mapping indeks ke label
label_mapping = model.classes_

# Tambahkan hasil prediksi dan confidence ke DataFrame
data_mentah['predicted_label'] = y_pred
data_mentah['confidence_score'] = [
    max(proba) for proba in y_proba
]

# === 6️⃣ Simpan hasil prediksi ke Database ===
print("\n🔄 Menyimpan hasil prediksi ke database...")
for index, row in data_mentah.iterrows():
    query_insert = text("""
        INSERT INTO komentar_sentimen_ml (
            mentah_id, video_id, username, comment, tanggal_komentar, 
            cleaned_comment, comment_translate, predicted_label, confidence_score, created_at
        ) VALUES (
            :mentah_id, :video_id, :username, :comment, :tanggal_komentar, 
            :cleaned_comment, :comment_translate, :predicted_label, :confidence_score, :created_at
        )
    """)

    # Eksekusi query
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            connection.execute(query_insert, {
                'mentah_id': row['id'],
                'video_id': row['video_id'],
                'username': row['username'],
                'comment': row['comment'],
                'tanggal_komentar': row['tanggal_komentar'],
                'cleaned_comment': row['cleaned_comment'],
                'comment_translate': row['comment_translate'],
                'predicted_label': row['predicted_label'],
                'confidence_score': row['confidence_score'],
                'created_at': datetime.now()
            })
            trans.commit()
            print(f"✅ Berhasil di-commit ke database (ID: {row['id']})")
        except Exception as e:
            trans.rollback()
            print(f"❌ Gagal menyimpan ke database: {e}")

# === 7️⃣ Update Status di Tabel komentar_mentah ===
print("\n🔄 Update status is_processed_ml di tabel komentar_mentah...")

update_query = text("""
    UPDATE komentar_mentah 
    SET is_processed_ml = 1 
    WHERE id = :id
""")

# 🚀 Sekarang kita pakai transaction dan commit juga
with engine.connect() as connection:
    trans = connection.begin()
    try:
        for id_mentah in data_mentah['id']:
            print(f"🔄 Update ID: {id_mentah}")
            connection.execute(update_query, {'id': id_mentah})
        trans.commit()
        print("✅ Semua status is_processed_ml berhasil di-update!")
    except Exception as e:
        trans.rollback()
        print(f"❌ Terjadi kesalahan saat update status: {e}")
