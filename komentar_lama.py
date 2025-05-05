import pymysql
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK resources
nltk.download('stopwords')
nltk.download('punkt')

# Setup database connection
db = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="",
    database="analisis_sentimen_kejagung_db",
    charset='utf8mb4'
)
cursor = db.cursor()

# Stopwords + sentiment words
stop_words = set(stopwords.words('indonesian'))
kata_penting = {
    'tidak', 'jangan', 'belum', 'kurang', 'bukan',
    'baik', 'buruk', 'bagus', 'jelek', 'puas', 'kecewa', 'senang', 'sedih',
    'marah', 'bosan', 'suka', 'benci', 'hebat', 'parah', 'mantap', 'payah',
    'lambat', 'cepat', 'menyenangkan', 'mengecewakan', 'luar biasa', 'aneh',
    'malu', 'terlalu', 'gagal', 'berhasil', 'hancur', 'terbaik', 'terburuk',
    'tercepat', 'terlambat', 'salah', 'benar', 'kacau'
}
stop_words -= kata_penting

# Function for cleaning text
def bersihkan_komentar(teks):
    teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
    teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
    teks = teks.lower()
    tokens = word_tokenize(teks)
    bersih = [t for t in tokens if t not in stop_words and len(t) > 1]
    return " ".join(bersih)

# Ambil komentar yang belum memiliki cleaned_comment
cursor.execute("SELECT id, comment FROM komentar_mentah WHERE cleaned_comment IS NULL")
data = cursor.fetchall()

for row in data:
    komentar_id = row[0]
    komentar_asli = row[1]
    komentar_bersih = bersihkan_komentar(komentar_asli)

    # Update cleaned_comment ke database
    cursor.execute(
        "UPDATE komentar_mentah SET cleaned_comment = %s WHERE id = %s",
        (komentar_bersih, komentar_id)
    )
    print(f"✅ ID {komentar_id} berhasil dibersihkan.")

db.commit()
db.close()
print("\n🚀 Selesai membersihkan komentar lama.")
