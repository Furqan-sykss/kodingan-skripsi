import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# 🔄 Koneksi Database
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db"
)

# ✅ Fungsi utama untuk menjalankan proses Hybrid


def run_hybrid_analysis():
    print("🚀 Memulai Analisis Hybrid...")

    # ✅ Query untuk mengambil data yang sudah diolah oleh VADER dan IndoBERT
    query_ids = """
        SELECT id FROM komentar_mentah
        WHERE is_processed_vader = 1 AND is_processed_indobert = 1
    """
    processed_ids = pd.read_sql(query_ids, engine)

    # ✅ Ambil data hasil analisis VADER dan IndoBERT
    vader = pd.read_sql("SELECT * FROM komentar_sentimen_vader", engine)
    bert = pd.read_sql("SELECT * FROM komentar_sentimen_indobert", engine)

    # ✅ Filter hanya data yang sudah diproses oleh keduanya
    vader = vader[vader['mentah_id'].isin(processed_ids['id'])]
    bert = bert[bert['mentah_id'].isin(processed_ids['id'])]

    # ✅ Merge berdasarkan mentah_id
    merged = pd.merge(vader, bert, on='mentah_id',
                      suffixes=('_vader', '_indobert'))

    # ✅ Cek kolom yang ada setelah merge
    print("Kolom yang ada pada DataFrame setelah merge:", merged.columns.tolist())

    # ✅ Fungsi untuk menentukan label hybrid
    def hybrid_label(row):
        if row['label_vader'] == row['indobert_sentiment_label']:
            return row['label_vader']
        return row['indobert_sentiment_label'] if row['indobert_confidence_score'] > 0.75 else row['label_vader']

    merged['final_hybrid_label'] = merged.apply(hybrid_label, axis=1)
    merged['confidence_average_score'] = (
        merged['compound_score'].abs() + merged['indobert_confidence_score']) / 2
    merged['processed_at'] = datetime.now()

    # ✅ Membuat DataFrame final dengan nama kolom yang tepat
    final_data = merged.loc[:, [
        'mentah_id',
        'video_id_vader',
        'username_vader',
        'tanggal_komentar_vader',
        'comment_vader',
        'cleaned_comment_vader',
        'cleaned_comment_indobert',
        'label_vader',
        'compound_score',
        'indobert_sentiment_label',
        'indobert_confidence_score',
        'final_hybrid_label',
        'confidence_average_score',
        'processed_at'
    ]]

    # ✅ Ganti nama kolom secara aman
    final_data = final_data.rename(columns={
        'video_id_vader': 'video_id',
        'username_vader': 'username',
        'tanggal_komentar_vader': 'tanggal_komentar',
        'comment_vader': 'comment',
        'cleaned_comment_vader': 'cleaned_comment_vader',
        'cleaned_comment_indobert': 'cleaned_comment_indobert',
        'label_vader': 'vader_label',
        'compound_score': 'vader_score',
        'indobert_sentiment_label': 'indobert_label',
        'indobert_confidence_score': 'indobert_score'
    })

    # ✅ Simpan ke database tanpa duplikasi
    with engine.begin() as conn:
        for _, row in final_data.iterrows():
            # Cek apakah sudah ada di database
            check_query = """
                SELECT COUNT(*) as total FROM komentar_sentimen_hybrid WHERE mentah_id = :mentah_id
            """
            result = conn.execute(text(check_query), {
                                  "mentah_id": row['mentah_id']}).fetchone()

            if result.total == 0:  # Jika belum ada, baru di-insert
                insert_query = """
                    INSERT INTO komentar_sentimen_hybrid (
                        mentah_id, video_id, username, tanggal_komentar, comment,
                        cleaned_comment_vader, cleaned_comment_indobert, vader_label, vader_score, 
                        indobert_label, indobert_score, final_hybrid_label, confidence_average_score, processed_at
                    ) 
                    VALUES (
                        :mentah_id, :video_id, :username, :tanggal_komentar, :comment,
                        :cleaned_comment_vader, :cleaned_comment_indobert, :vader_label, :vader_score, 
                        :indobert_label, :indobert_score, :final_hybrid_label, :confidence_average_score, :processed_at
                    )
                """

                conn.execute(text(insert_query), {
                    "mentah_id": row['mentah_id'],
                    "video_id": row['video_id'],
                    "username": row['username'],
                    "tanggal_komentar": row['tanggal_komentar'],
                    "comment": row['comment'],
                    "cleaned_comment_vader": row['cleaned_comment_vader'],
                    "cleaned_comment_indobert": row['cleaned_comment_indobert'],
                    "vader_label": row['vader_label'],
                    "vader_score": row['vader_score'],
                    "indobert_label": row['indobert_label'],
                    "indobert_score": row['indobert_score'],
                    "final_hybrid_label": row['final_hybrid_label'],
                    "confidence_average_score": row['confidence_average_score'],
                    "processed_at": row['processed_at']
                })

    print("✅ Analisis Hybrid selesai.")
