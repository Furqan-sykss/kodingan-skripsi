import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Koneksi ke Database
db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE"),
    charset='utf8mb4'
)
cursor = db.cursor()

# Test Insert
cursor.execute("INSERT INTO komentar_mentah (video_id, kata_kunci, username, comment, likes, replies, tanggal_komentar, is_processed_vader, is_processed_indobert, created_at) VALUES ('12345', 'test_tagar', 'test_user', 'test_comment', 10, 0, NOW(), 0, 0, NOW())")
db.commit()

# Cek hasil
cursor.execute(
    "SELECT * FROM komentar_mentah ORDER BY created_at DESC LIMIT 5")
for row in cursor.fetchall():
    print(row)

cursor.close()
db.close()
