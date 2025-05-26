import pandas as pd
from sqlalchemy import create_engine, text
from deep_translator import GoogleTranslator
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
from datetime import datetime
import re
import sys
import os
import json

# === 🔄 Load kamus normalisasi JSON ===
kamus_path = os.path.join(os.getcwd(), "public/scripts/kamus_normalisasi.json")
with open(kamus_path, 'r', encoding='utf-8') as f:
    normalization_dict = json.load(f)

# === Fungsi untuk Flask API ===


def run_ML_analysis():
    original_stdout = sys.stdout
    try:
        from io import StringIO
        captured_output = StringIO()
        sys.stdout = captured_output

        exec_main_script()

        sys.stdout = original_stdout
        output = captured_output.getvalue()
        print(output)
        return {"status": "success", "message": "Analisis ML berhasil!", "output": output}

    except SystemExit:
        sys.stdout = original_stdout
        return {"status": "warning", "message": "Tidak ada data untuk diproses"}
    except Exception as e:
        sys.stdout = original_stdout
        print(f"❌ Error: {str(e)}")
        raise e

# === Fungsi utama ===


def exec_main_script():
    engine = create_engine(
        "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

    # === 1️⃣ Ambil Data Mentah ===
    query = """
        SELECT id, video_id, username, comment, tanggal_komentar 
        FROM komentar_mentah
        WHERE is_processed_ml = 0 AND is_processed_vader = 0
        LIMIT 50
    """
    data_mentah = pd.read_sql(query, engine)

    print(f"🔎 Jumlah Data yang Diambil: {len(data_mentah)}")
    if len(data_mentah) == 0:
        print("❌ Tidak ada data yang diambil dari database.")
        exit()

    # === 2️⃣ Preprocessing ===
    def bersihkan_teks(teks):
        # Hapus URL, mention, dan hashtag
        teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
        # Hapus simbol, angka, dan karakter khusus
        teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
        # Lowercase dan hapus spasi di awal/akhir
        teks = teks.lower().strip()
        # Hapus spasi berlebih
        teks = re.sub(r'\s+', ' ', teks)
        return teks

    def normalisasi_kata(teks):
        kata_list = teks.split()
        hasil = [normalization_dict.get(kata, kata) for kata in kata_list]
        return " ".join(hasil)

    def translate_comment(teks):
        try:
            translated = GoogleTranslator(
                source='auto', target='en').translate(teks)
            return translated
        except Exception as e:
            print(f"❌ Terjadi kesalahan saat translate: {e}")
            return teks

    # Lakukan preprocessing
    data_mentah['cleaned_comment'] = data_mentah['comment'].apply(
        bersihkan_teks)
    data_mentah['normalized_comment'] = data_mentah['cleaned_comment'].apply(
        normalisasi_kata)
    data_mentah['comment_translate'] = data_mentah['normalized_comment'].apply(
        translate_comment)

    # === 3️⃣ Load model dan vectorizer ===
    with open('public/scripts/tfidf_model.pkl', 'rb') as f:
        vectorizer = pickle.load(f)

    with open('public/scripts/ml_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # === 4️⃣ Vectorize data translate ===
    X_test = vectorizer.transform(data_mentah['comment_translate'])

    # === 5️⃣ Prediksi dengan model ===
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    label_mapping = model.classes_

    data_mentah['predicted_label'] = y_pred
    data_mentah['confidence_score'] = [max(p) for p in y_proba]

    # === 6️⃣ Simpan ke komentar_sentimen_ml ===
    print("\n🔄 Menyimpan hasil prediksi ke database...")
    for _, row in data_mentah.iterrows():
        query_insert = text("""
            INSERT INTO komentar_sentimen_ml (
                mentah_id, video_id, username, comment, tanggal_komentar, 
                cleaned_comment, comment_translate, predicted_label, confidence_score, created_at
            ) VALUES (
                :mentah_id, :video_id, :username, :comment, :tanggal_komentar, 
                :cleaned_comment, :comment_translate, :predicted_label, :confidence_score, :created_at
            )
        """)
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                conn.execute(query_insert, {
                    'mentah_id': row['id'],
                    'video_id': row['video_id'],
                    'username': row['username'],
                    'comment': row['comment'],
                    'tanggal_komentar': row['tanggal_komentar'],
                    'cleaned_comment': row['normalized_comment'],
                    'comment_translate': row['comment_translate'],
                    'predicted_label': row['predicted_label'],
                    'confidence_score': row['confidence_score'],
                    'created_at': datetime.now()
                })
                trans.commit()
                print(f"✅ Berhasil simpan ke DB (ID: {row['id']})")
            except Exception as e:
                trans.rollback()
                print(f"❌ Gagal simpan ke DB: {e}")

    # === 7️⃣ Update is_processed_ml ===
    print("\n🔄 Update status is_processed_ml di komentar_mentah...")
    update_query = text(
        "UPDATE komentar_mentah SET is_processed_ml = 1 WHERE id = :id")

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for id_mentah in data_mentah['id']:
                print(f"🔄 Update ID: {id_mentah}")
                conn.execute(update_query, {'id': id_mentah})
            trans.commit()
            print("✅ Semua status is_processed_ml berhasil di-update!")
        except Exception as e:
            trans.rollback()
            print(f"❌ Error saat update status: {e}")


# === Untuk eksekusi langsung tanpa Flask ===
if __name__ == "__main__":
    exec_main_script()
