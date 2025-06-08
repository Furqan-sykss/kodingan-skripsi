import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import numpy as np

# === 1️⃣ Koneksi ke database ===
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# === 2️⃣ Ambil data hasil analisis VADER ===
query = """
    SELECT comment_translate, label_vader 
    FROM komentar_sentimen_vader
    WHERE comment_translate IS NOT NULL AND label_vader IS NOT NULL
"""
df = pd.read_sql(query, engine)

# Normalisasi label untuk menghindari kesalahan klasifikasi
df['label_vader'] = df['label_vader'].str.lower().str.strip()

# Tampilkan distribusi label
print("\n🔍 Distribusi label:")
print(df['label_vader'].value_counts())
print(f"\n📊 Jumlah data: {len(df)}")

# === 3️⃣ Preprocessing dan vectorizing TF-IDF ===
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(df['comment_translate'])
y = df['label_vader']

# === 4️⃣ Split Data (Train/Test) ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# === 5️⃣ Training Model ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
print("\n🔁 Melakukan training model...")
model.fit(X_train, y_train)
print("✅ Model berhasil dilatih.")

# === 6️⃣ Simpan model dan vectorizer ===
with open('public/scripts/tfidf_model.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

with open('public/scripts/ml_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("💾 Model & Vectorizer disimpan sebagai 'ml_model.pkl' dan 'tfidf_model.pkl'")

# === 7️⃣ Evaluasi ===
y_pred = model.predict(X_test)
print("\n📋 Evaluasi Model:")
print(classification_report(y_test, y_pred))
print("🎯 Akurasi:", accuracy_score(y_test, y_pred))
print("🎯 F1 Score (macro):", f1_score(y_test, y_pred, average='macro'))
print("🎯 F1 Score (micro):", f1_score(y_test, y_pred, average='micro'))

# Simpan laporan evaluasi ke file
with open("public/scripts/evaluation_report.txt", "w", encoding="utf-8") as f:
    f.write(classification_report(y_test, y_pred))
    f.write("\nAkurasi: {:.4f}".format(accuracy_score(y_test, y_pred)))
    f.write("\nF1 Score (macro): {:.4f}".format(
        f1_score(y_test, y_pred, average='macro')))
    f.write("\nF1 Score (micro): {:.4f}".format(
        f1_score(y_test, y_pred, average='micro')))

# === 8️⃣ Plot Confusion Matrix ===
plt.figure(figsize=(6, 5))
matrix = confusion_matrix(y_test, y_pred, labels=[
                          "positif", "netral", "negatif"])
sns.heatmap(matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=["positif", "netral", "negatif"],
            yticklabels=["positif", "netral", "negatif"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Random Forest")
plt.tight_layout()
plt.savefig("public/scripts/confusion_matrix_training.png")
print("🖼️ Confusion Matrix disimpan sebagai 'confusion_matrix_training.png'")

# === 9️⃣ Tampilkan 10 fitur terpenting ===
feature_names = vectorizer.get_feature_names_out()
importances = model.feature_importances_
top_indices = np.argsort(importances)[-10:][::-1]

print("\n🔎 Top 10 Fitur TF-IDF Paling Berpengaruh:")
for i in top_indices:
    print(f"{feature_names[i]}: {importances[i]:.4f}")
