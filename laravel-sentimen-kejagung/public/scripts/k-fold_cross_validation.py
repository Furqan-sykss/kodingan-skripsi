import pandas as pd
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
import numpy as np
import joblib
import matplotlib.pyplot as plt

# ==== Koneksi Database ====
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# ==== Load Data dari Database ====
query = """
SELECT comment_translate, label_vader
FROM komentar_sentimen_vader
WHERE comment_translate IS NOT NULL AND label_vader IS NOT NULL
"""
df = pd.read_sql(query, engine)

# ==== Load TF-IDF ====
tfidf = joblib.load('public/scripts/tfidf_model.pkl')
X = tfidf.transform(df['comment_translate'])
y = df['label_vader'].str.lower().str.strip()

# ==== Model ====
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# ==== Setup K-Fold ===
n_splits = 10
n_repeats = 3

cv = RepeatedStratifiedKFold(
    n_splits=n_splits,
    n_repeats=n_repeats,
    random_state=999
)

# ==== Jalankan K-Fold ====
scores = cross_val_score(
    model, X, y,
    scoring='accuracy',
    cv=cv,
    n_jobs=-1
)

print(f"Akurasi tiap fold ({n_splits} Fold x {n_repeats} Repeat):")
print(scores)

# ==== Hitung Mean Tiap Pengulangan ====
scores_reshaped = scores.reshape(n_repeats, n_splits)
mean_per_repeat = scores_reshaped.mean(axis=1)

for i, mean_score in enumerate(mean_per_repeat, 1):
    print(f"Mean Akurasi Repeat ke-{i}: {mean_score:.4f}")

# ==== Hasil Keseluruhan ====
print(f"\nMean Akurasi Keseluruhan : {np.mean(scores):.4f}")
print(f"Standard Deviasi          : {np.std(scores):.4f}")

# ==== Visualisasi ====
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(scores)+1), scores, marker='o',
         color='orange', label='Akurasi Fold')
plt.hlines(np.mean(scores), xmin=1, xmax=len(scores),
           colors='blue', label='Mean Akurasi', linestyles='dashed')
plt.title('K-Fold Cross Validation Random Forest')
plt.xlabel('Fold ke-')
plt.ylabel('Akurasi')
plt.ylim(0.7, 1.0)
plt.grid(linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig('hasil_kfold_crossvalidation.png')
plt.show()
