import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

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

print(f"📊 Jumlah data: {len(df)}")

# === 3️⃣ Preprocessing dan vectorizing TF-IDF ===
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(df['comment_translate'])
y = df['label_vader']

# === 4️⃣ Split Data (Train/Test) ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42, stratify=y)

# === 5️⃣ Training Model ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
print("🔁 Melakukan training model...")
model.fit(X_train, y_train)
print("✅ Model berhasil dilatih.")

# === 6️⃣ Simpan model dan vectorizer ==
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

# Simpan gambar
plt.savefig("public/scripts/confusion_matrix_training.png")
print("🖼️ Confusion Matrix disimpan sebagai 'confusion_matrix_training.png'")
