import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# 🔄 Koneksi ke database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# 🔍 Ambil data label dari tabel komentar_sentimen_vader
query = "SELECT label_vader FROM komentar_sentimen_vader WHERE label_vader IS NOT NULL"
df = pd.read_sql(query, engine)

# 📊 Hitung jumlah tiap label
label_counts = df['label_vader'].value_counts().reindex(
    ['positif', 'netral', 'negatif'], fill_value=0)

# 📈 Plot batang
colors = ['skyblue', 'sandybrown', 'lightgreen']
plt.figure(figsize=(8, 5))
bars = plt.bar(label_counts.index, label_counts.values, color=colors)

# Tambahkan angka jumlah di atas tiap batang
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height +
             5, str(height), ha='center', fontsize=10)

plt.title("Distribusi Sentimen Berdasarkan Label VADER")
plt.xlabel("Kelas Sentimen")
plt.ylabel("Jumlah Komentar")
plt.tight_layout()
plt.show()
