# import nltk
# import logging
# import pandas as pd
# import re
# from datetime import datetime
# from sqlalchemy import text, create_engine
# from sqlalchemy.orm import sessionmaker
# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from deep_translator import GoogleTranslator

# # =================== 🔧 Logging ===================
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # =================== 🔎 VADER & NLTK ===================
# nltk.download("vader_lexicon")
# vader = SentimentIntensityAnalyzer()

# # =================== 🔧 Koneksi DB ===================
# engine = create_engine("mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")
# Session = sessionmaker(bind=engine)

# # =================== 🔧 Preprocessing ===================
# def bersihkan_teks(teks):
#     teks = re.sub(r"http\S+|@\S+|#\S+", "", teks)
#     teks = re.sub(r"\d+", "", teks)
#     teks = re.sub(r"[^\w\s]", " ", teks)
#     teks = teks.lower().strip()
#     teks = re.sub(r'\s+', ' ', teks)
#     return teks

# # =================== 🌐 Translasi ===================
# def translate(teks):
#     try:
#         return GoogleTranslator(source='auto', target='en').translate(teks)
#     except Exception as e:
#         logger.error(f"Translasi gagal: {e}")
#         return teks

# # =================== 🧠 Analisis Sentimen ===================
# def analyze_sentiment(teks):
#     scores = vader.polarity_scores(teks)
#     compound = scores['compound']
#     if compound >= 0.3:
#         label = "positif"
#     elif compound <= -0.3:
#         label = "negatif"
#     else:
#         label = "netral"
#     return scores['pos'], scores['neu'], scores['neg'], compound, label

# # =================== 🚀 Eksekusi Analisis ===================
# def run_vader_analysis(limit=500):
#     logger.info("🚀 Mulai analisis VADER tanpa kamus...")
#     select_query = f"""
#         SELECT id, video_id, username, comment, tanggal_komentar
#         FROM komentar_mentah
#         WHERE is_processed_vader = 0 AND is_processed_ml = 0
#         ORDER BY id LIMIT {limit}
#     """
#     insert_query = """
#         INSERT INTO komentar_sentimen_vader (
#             mentah_id, video_id, username, tanggal_komentar, comment,
#             cleaned_comment, comment_translate, vader_pos, vader_neu,
#             vader_neg, compound_score, label_vader, processed_at
#         ) VALUES (
#             :mentah_id, :video_id, :username, :tanggal_komentar, :comment,
#             :cleaned_comment, :comment_translate, :vader_pos, :vader_neu,
#             :vader_neg, :compound_score, :label_vader, :processed_at
#         )
#     """
#     update_query = "UPDATE komentar_mentah SET is_processed_vader = 1 WHERE id = :id"
#     processed = 0
#     skipped = 0

#     with Session() as session:
#         data = pd.read_sql(text(select_query), engine)
#         for _, row in data.iterrows():
#             try:
#                 cleaned = bersihkan_teks(row["comment"])
#                 translated = translate(cleaned)
#                 pos, neu, neg, compound, label = analyze_sentiment(translated)

#                 session.execute(text(insert_query), {
#                     "mentah_id": row["id"],
#                     "video_id": row["video_id"],
#                     "username": row["username"],
#                     "tanggal_komentar": row["tanggal_komentar"],
#                     "comment": row["comment"],
#                     "cleaned_comment": cleaned,
#                     "comment_translate": translated,
#                     "vader_pos": pos,
#                     "vader_neu": neu,
#                     "vader_neg": neg,
#                     "compound_score": compound,
#                     "label_vader": label,
#                     "processed_at": datetime.now()
#                 })
#                 session.execute(text(update_query), {"id": row["id"]})
#                 session.commit()
#                 logger.info(f"✅ Komentar ID {row['id']} diproses.")
#                 processed += 1
#             except Exception as e:
#                 logger.error(f"❌ Gagal proses ID {row['id']}: {e}")
#                 session.rollback()
#                 skipped += 1

#     logger.info("✅ Analisis selesai.")
#     return {"processed": processed, "skipped": skipped}
