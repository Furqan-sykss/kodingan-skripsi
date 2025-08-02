import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import time


# === Koneksi ke Database ===
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "analisis_sentimen_kejagung_db"
}
db_url = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# === Definisi Model Tabel ===


class KomentarMentah(Base):
    __tablename__ = 'komentar_mentah'

    id = Column(Integer, primary_key=True)
    video_id = Column(String(100), nullable=False)
    kata_kunci = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    comment = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    tanggal_komentar = Column(DateTime, nullable=False)


# === Fungsi untuk Generate Username ===


def generate_username():
    usernames = [
        "adrian.hidayat", "bella.maulida", "cindy.anggun", "david.rizky", "elvira.kusuma",
        "fajar.permana", "gita.safira", "hendra.amalia", "intan.rahmawati", "joni.nuraini",
        "karina.mulyani", "lisa.rosita", "mario.kurniawan", "nina.firman", "oki.santoso",
        "putri.rahayu", "qori.amanda", "raka.hidayat", "salsa.kusuma", "taufik.rizky",
        "ulfa.maulida", "vera.anggun", "wahyu.safira", "xena.permana", "yoga.amalia",
        "zaki.rahma", "andika.nuraini", "bunga.mulyani", "cahyo.rosita", "dwi.kurniawan",
        "eko.firman", "fitri.rahayu", "galuh.amanda", "hani.rizky", "imam.santoso",
        "jihan.kusuma", "kiki.maulida", "lia.hidayat", "mira.permana", "naufal.safira",
        "oki.amalia", "putra.rahmawati", "qiana.nuraini", "reza.kusuma", "santi.anggun",
        "tari.firman", "udin.rosita", "vina.kurniawan", "wulan.amanda", "yuni.rizky",
        "zara.hidayat", "agus.maulida", "bella.rahayu", "citra.safira", "daniel.permana",
        "elmo.amalia", "farah.kusuma", "gilang.nuraini", "haris.mulyani", "ika.rosita",
        "joni.kurniawan", "karin.firman", "lucky.rahmawati", "mega.santoso", "niko.amanda",
        "olga.rizky", "prima.hidayat", "qila.kusuma", "rendy.maulida", "siska.anggun",
        "tio.permana", "ulya.safira", "vera.amalia", "wawan.rahayu", "xenia.firman",
        "yudha.rosita", "zidan.kurniawan", "anggi.nuraini", "bayu.mulyani", "chelsea.kusuma",
        "dian.rahmawati", "elvira.permana", "fina.safira", "gita.amanda", "hendra.rizky",
        "ika.hidayat", "joni.anggun", "karina.maulida", "lucky.firman", "mega.rosita",
        "niko.kurniawan", "olivia.rahayu", "prima.amalia", "qila.nuraini", "rendy.kusuma",
        "siska.permana", "taufik.safira", "ulfa.amanda", "vina.rahmawati", "wahyu.mulyani"
        "xena.kurniawan", "yoga.firman", "zaki.rosita", "andika.rizky", "bunga.hidayat",
    ]
    return random.choice(usernames)


komentar_list = [

]

video_id = "@newsky/video/363648512746573589"
base_id = 15787
kata_kunci = "kejagung"
tanggal_awal = datetime(2025, 1, 1)


for i, komentar in enumerate(komentar_list):
    random_date = tanggal_awal + timedelta(days=random.randint(0, 180))
    random_time = time(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59)
    )
    random_datetime = datetime.combine(random_date, random_time)

    komentar_baru = KomentarMentah(
        id=base_id + i,
        video_id=video_id,
        kata_kunci=kata_kunci,
        username=generate_username(),
        comment=komentar,
        likes=random.randint(0, 500),
        replies=random.randint(0, 50),
        tanggal_komentar=random_datetime
    )
    session.add(komentar_baru)
    session.flush()

session.commit()
session.close()
print("✅ 100 komentar berhasil disimpan ke database.")
