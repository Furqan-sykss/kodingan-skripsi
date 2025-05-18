import pandas as pd
from sqlalchemy import create_engine
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import seaborn as sns
import matplotlib.pyplot as plt

# 🔄 Koneksi ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db"
)

# 🔍 Ambil data hasil prediksi dan label asli
query = """
    SELECT 
        label_vader AS prediksi,
        ground_truth_label AS aktual
    FROM 
        komentar_sentimen_vader
    WHERE 
        ground_truth_label IS NOT NULL
"""
df = pd.read_sql(query, engine)

# ✅ Tampilkan statistik dasar
print("Distribusi Data:")
print(df['aktual'].value_counts())
print("\nDistribusi Prediksi:")
print(df['prediksi'].value_counts())

# ✅ Evaluasi Akurasi
print("\n=== 📊 Evaluasi Model VADER ===")
print("Akurasi  :", accuracy_score(df['aktual'], df['prediksi']))
print("\n=== 📌 Classification Report ===")
print(classification_report(df['aktual'], df['prediksi']))

# ✅ Confusion Matrix
cm = confusion_matrix(df['aktual'], df['prediksi'])
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negatif', 'Netral', 'Positif'], yticklabels=['Negatif', 'Netral', 'Positif'])
plt.xlabel('Prediksi')
plt.ylabel('Aktual')
plt.title('Confusion Matrix - VADER Model')
plt.show()
