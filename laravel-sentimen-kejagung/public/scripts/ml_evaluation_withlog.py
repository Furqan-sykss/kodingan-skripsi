import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from deep_translator import GoogleTranslator
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re

# 🔄 Koneksi langsung ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db"
)

# === 1️⃣ Ambil 20% Data Mentah dari tabel komentar_sentimen_vader ===
query = """
    SELECT id, mentah_id, video_id, username, comment, tanggal_komentar, label_vader 
    FROM komentar_sentimen_vader
    WHERE comment IS NOT NULL
    ORDER BY RAND()
    LIMIT 320; 
"""
data_uji = pd.read_sql(query, engine)

print(f"🔎 Jumlah Data yang Diambil: {len(data_uji)}")
if len(data_uji) == 0:
    print("❌ Tidak ada data yang diambil dari database.")
    exit()

# === 2️⃣ Preprocessing Data (Sesuai sentiment_vader.py) ===


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
data_uji['cleaned_comment'] = data_uji['comment'].apply(bersihkan_teks)
data_uji['comment_translate'] = data_uji['cleaned_comment'].apply(
    translate_comment)

# === 3️⃣ Load model dan vectorizer ===
with open('public/scripts/tfidf_model.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

with open('public/scripts/ml_model.pkl', 'rb') as f:
    model = pickle.load(f)

# === 4️⃣ Vectorize Data Uji ===
X_test = vectorizer.transform(data_uji['comment_translate'])

# === 5️⃣ Prediksi menggunakan model ===
y_pred = model.predict(X_test)

# === 6️⃣ Evaluasi hasil prediksi ===
print("\n🔹 Confusion Matrix:\n", confusion_matrix(
    data_uji['label_vader'], y_pred))
print("\n🔹 Classification Report:\n", classification_report(
    data_uji['label_vader'], y_pred))
print("\n🔹 Accuracy Score:", accuracy_score(data_uji['label_vader'], y_pred))

# === 7️⃣ Plot Confusion Matrix ===
plt.figure(figsize=(6, 5))
matrix = confusion_matrix(data_uji['label_vader'], y_pred, labels=[
                          "positif", "netral", "negatif"])
sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=["positif", "netral", "negatif"],
            yticklabels=["positif", "netral", "negatif"])
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix - Machine Learning vs VADER')

# Simpan gambar
plt.savefig('public/scripts/confusion_matrix.png')
plt.show()
print("✅ Confusion Matrix berhasil disimpan sebagai 'confusion_matrix.png'")

# === 8️⃣ Logging Evaluasi ke Database ===
print("\n🔄 Menyimpan hasil evaluasi ke database...")

# Ambil metrik evaluasi
report = classification_report(
    data_uji['label_vader'], y_pred, output_dict=True)
accuracy = accuracy_score(data_uji['label_vader'], y_pred)
precision = report['weighted avg']['precision']
recall = report['weighted avg']['recall']
f1_score = report['weighted avg']['f1-score']
support = len(data_uji)

# Simpan hasil evaluasi ke tabel evaluation_logs
query = text("""
    INSERT INTO evaluation_logs (model_name, accuracy, precision_score, recall, f1_score, support)
    VALUES (:model_name, :accuracy, :precision, :recall, :f1_score, :support)
""")

# Eksekusi query dengan parameter
with engine.connect() as connection:
    connection.execute(query, {
        'model_name': 'RandomForest',
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'support': support
    })

print("✅ Log evaluasi berhasil disimpan di database.")
