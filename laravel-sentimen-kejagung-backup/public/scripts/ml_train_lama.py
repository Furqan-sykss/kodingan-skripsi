import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === 🔄 Koneksi ke database ===
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# === 1️⃣ Ambil data hasil VADER yang sudah ditranslate ===
query = """
    SELECT comment_translate, label_vader 
    FROM komentar_sentimen_vader
    WHERE comment_translate IS NOT NULL AND label_vader IS NOT NULL
"""
data = pd.read_sql(query, engine)

print(f"🔍 Jumlah data: {len(data)}")

# === 2️⃣ TF-IDF Vectorization ===
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(data['comment_translate'])
y = data['label_vader']

# Simpan vectorizer
with open('public/scripts/tfidf_model.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
    print("✅ TF-IDF Vectorizer disimpan sebagai tfidf_model.pkl")

# === 3️⃣ Split data: 80% training, 20% testing ===
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42, stratify=y
)

# === 4️⃣ Training model Random Forest ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
print("🔄 Melakukan training model...")
model.fit(X_train, y_train)
print("✅ Model berhasil dilatih.")

# Simpan model
with open('public/scripts/ml_model.pkl', 'wb') as f:
    pickle.dump(model, f)
    print("✅ Model disimpan sebagai ml_model.pkl")

# === 5️⃣ Evaluasi Model ===
y_pred = model.predict(X_test)
print("\n🔍 Evaluasi Model:")
print(classification_report(y_test, y_pred))
print("Akurasi:", accuracy_score(y_test, y_pred))

# === 6️⃣ Visualisasi Confusion Matrix ===
plt.figure(figsize=(6, 5))
cm = confusion_matrix(y_test, y_pred, labels=["positif", "netral", "negatif"])
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=["positif", "netral", "negatif"],
            yticklabels=["positif", "netral", "negatif"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - Random Forest")
plt.tight_layout()
plt.savefig("public/scripts/confusion_matrix_training.png")
plt.show()
print("📊 Confusion Matrix disimpan sebagai 'confusion_matrix_training.png'")
