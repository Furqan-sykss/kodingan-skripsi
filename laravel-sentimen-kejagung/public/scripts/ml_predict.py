import pandas as pd
from sqlalchemy import create_engine, text
from deep_translator import GoogleTranslator
import pickle
from datetime import datetime
import re
import os
import json
import sys

# === Load kamus normalisasi ===
kamus_path = os.path.join(os.getcwd(), "public/scripts/kamus_normalisasi.json")
with open(kamus_path, 'r', encoding='utf-8') as f:
    normalization_dict = json.load(f)

# === Fungsi preprocessing (gabungan dari sentiment_vader.py) ===


def bersihkan_teks(teks):
    teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
    teks = re.sub(r"\d+", "", teks)
    teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
    teks = teks.lower().strip()
    teks = re.sub(r'\s+', ' ', teks)
    return teks


def normalisasi_kata(teks):
    kata_list = teks.split()
    hasil = [normalization_dict.get(kata, kata) for kata in kata_list]
    return " ".join(hasil)


def apply_idioms(teks):
    idiom_dict = {
        "maung": "hero", "jos": "awesome", "gass": "go",
        "mantap": "great", "di tangan": "in the hands of"
    }
    for k, v in idiom_dict.items():
        teks = teks.replace(k, v)
    return teks


def translate(teks):
    try:
        teks = apply_idioms(teks)
        return GoogleTranslator(source='auto', target='en').translate(teks)
    except:
        return teks

# === Fungsi utama untuk Flask/API atau manual run ===


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

# === Script utama ===


def exec_main_script():
    engine = create_engine(
        "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

    # 1️⃣ Ambil data komentar mentah
    query = """
        SELECT id, video_id, username, comment, tanggal_komentar 
        FROM komentar_mentah
        WHERE is_processed_ml = 0 AND is_processed_vader = 0
        LIMIT 800
    """
    data_mentah = pd.read_sql(query, engine)

    print(f"🔎 Jumlah Data: {len(data_mentah)}")
    if data_mentah.empty:
        print("❌ Tidak ada data yang perlu diproses.")
        exit()

    # 2️⃣ Preprocessing
    data_mentah['cleaned_comment'] = data_mentah['comment'].apply(
        bersihkan_teks)
    data_mentah['normalized_comment'] = data_mentah['cleaned_comment'].apply(
        normalisasi_kata)
    data_mentah['comment_translate'] = data_mentah['normalized_comment'].apply(
        translate)

    # 3️⃣ Load model dan vectorizer
    with open('public/scripts/tfidf_model.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('public/scripts/ml_model.pkl', 'rb') as f:
        model = pickle.load(f)

    # 4️⃣ Vectorize dan prediksi
    X = vectorizer.transform(data_mentah['comment_translate'])
    y_pred = model.predict(X)
    y_proba = model.predict_proba(X)

    data_mentah['predicted_label'] = y_pred
    data_mentah['confidence_score'] = [max(p) for p in y_proba]

    # 5️⃣ Simpan hasil ke database
    for _, row in data_mentah.iterrows():
        insert_query = text("""
            INSERT INTO komentar_sentimen_ml (
                mentah_id, video_id, username, comment, tanggal_komentar,
                cleaned_comment, comment_translate, predicted_label,
                confidence_score, created_at
            ) VALUES (
                :mentah_id, :video_id, :username, :comment, :tanggal_komentar,
                :cleaned_comment, :comment_translate, :predicted_label,
                :confidence_score, :created_at
            )
        """)
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                conn.execute(insert_query, {
                    "mentah_id": row['id'],
                    "video_id": row['video_id'],
                    "username": row['username'],
                    "comment": row['comment'],
                    "tanggal_komentar": row['tanggal_komentar'],
                    "cleaned_comment": row['normalized_comment'],
                    "comment_translate": row['comment_translate'],
                    "predicted_label": row['predicted_label'],
                    "confidence_score": row['confidence_score'],
                    "created_at": datetime.now()
                })
                trans.commit()
                print(f"✅ Prediksi disimpan untuk ID: {row['id']}")
            except Exception as e:
                trans.rollback()
                print(f"❌ Gagal menyimpan ID {row['id']}: {e}")

    # 6️⃣ Update status
    update_query = text(
        "UPDATE komentar_mentah SET is_processed_ml = 1 WHERE id = :id")
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for id_ in data_mentah['id']:
                conn.execute(update_query, {'id': id_})
            trans.commit()
            print("✅ Status is_processed_ml berhasil di-update.")
        except Exception as e:
            trans.rollback()
            print(f"❌ Gagal update status: {e}")


# ✅ Jalankan manual jika tidak lewat Flask
if __name__ == "__main__":
    exec_main_script()
