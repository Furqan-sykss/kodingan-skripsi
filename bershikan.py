import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sqlalchemy import create_engine, text

# Unduh data NLTK jika belum
nltk.download('punkt')
nltk.download('stopwords')

# Koneksi DB
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# NLP tools
stop_words = set(stopwords.words('indonesian'))
stemmer = StemmerFactory().create_stemmer()

# Fungsi pembersih


def clean_comment(comment):
    comment = re.sub(r'[^a-zA-Z\s]', '', comment)  # Hapus simbol, angka, dll
    tokens = word_tokenize(comment.lower())
    tokens = [word for word in tokens if word not in stop_words]
    return stemmer.stem(' '.join(tokens))


# Proses komentar yang belum dibersihkan
with engine.connect() as conn:
    results = conn.execute(text("""
        SELECT id, comment FROM komentar_mentah
        WHERE cleaned_comment IS NULL 
        LIMIT 300
    """)).fetchall()

    for row in results:
        cleaned = clean_comment(row.comment)
        conn.execute(text("""
            UPDATE komentar_mentah
            SET cleaned_comment = :cleaned
            WHERE id = :id
        """), {"cleaned": cleaned, "id": row.id})

print("✅ Proses pembersihan komentar selesai.")
