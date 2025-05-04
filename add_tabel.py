from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Enum, Float
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy_utils import database_exists, create_database

# Konfigurasi koneksi
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "analisis_sentimen_kejagung_db"
}

# Buat engine database
db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(db_url)
metadata = MetaData()

# Buat database jika belum ada
if not database_exists(engine.url):
    create_database(engine.url)

# Tabel komentar_mentah
komentar_mentah = Table(
    'komentar_mentah', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('video_id', String(100)),
    Column('kata_kunci', String(100)),
    Column('username', String(100)),
    Column('user_id', String(100)),
    Column('comment', Text),
    Column('likes', Integer, default=0),
    Column('replies', Integer, default=0),
    Column('date', DateTime),
    Column('is_processed', TINYINT(1), default=0),
    Column('created_at', DateTime)
)

# Tabel komentar_final (dengan komentar mentah juga)
komentar_final = Table(
    'komentar_final', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('mentah_id', Integer),  # foreign key ke komentar_mentah
    # komentar mentah (copied from komentar_mentah.comment)
    Column('original_comment', Text),
    Column('cleaned_comment', Text),
    Column('vader_sentiment', Enum('positif', 'netral', 'negatif')),
    Column('vader_score', Float(5, 3)),
    Column('indobert_sentiment', Enum('positif', 'netral', 'negatif')),
    Column('indobert_confidence', Float(5, 3)),
    Column('hybrid_sentiment', Enum('positif', 'netral', 'negatif')),
    Column('processed_at', DateTime)
)

# Buat ulang semua tabel
metadata.drop_all(engine, checkfirst=True)
metadata.create_all(engine)

print("✅ Tabel komentar_mentah dan komentar_final berhasil dibuat ulang.")
