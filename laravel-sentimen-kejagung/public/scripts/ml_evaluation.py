import pandas as pd
from sqlalchemy import create_engine
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

# 🔄 Koneksi langsung ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# Ambil 20% Data Uji secara acak dari hasil VADER
query = """
    SELECT id, mentah_id, video_id, username, comment, tanggal_komentar, comment_translate, label_vader 
    FROM komentar_sentimen_vader
    WHERE comment_translate IS NOT NULL
    ORDER BY RAND()
"""
# LIMIT 320;  -- 20% dari 1600 data
data_uji = pd.read_sql(query, engine)

# Load model dan vectorizer
with open('public/scripts/tfidf_model.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

with open('public/scripts/ml_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Vectorize Data Uji
X_test = vectorizer.transform(data_uji['comment_translate'])
y_test = data_uji['label_vader']

# Prediksi menggunakan model
y_pred = model.predict(X_test)

# Evaluasi hasil prediksi
print("\n🔹 Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\n🔹 Classification Report:\n", classification_report(y_test, y_pred))
print("\n🔹 Accuracy Score:", accuracy_score(y_test, y_pred))
# === Plot Confusion Matrix ===
plt.figure(figsize=(6, 5))
matrix = confusion_matrix(y_test, y_pred, labels=[
                          "positif", "netral", "negatif"])
sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues', xticklabels=[
            "positif", "netral", "negatif"], yticklabels=["positif", "netral", "negatif"])
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix - Machine Learning vs VADER')

# Simpan gambar
plt.savefig('public/scripts/confusion_matrix.png')
plt.show()

print("✅ Confusion Matrix berhasil disimpan sebagai 'confusion_matrix.png'")
