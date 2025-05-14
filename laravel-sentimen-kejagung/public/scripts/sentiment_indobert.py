def run_indobert_analysis():
    print("🚀 Memulai Analisis IndoBERT...")
    # Pindahkan semua kode yang sudah ada ke dalam fungsi ini
    # (mulai dari koneksi database sampai selesai update status)

    from datetime import datetime
    import torch
    from torch.nn.functional import softmax
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    from sqlalchemy import create_engine, text
    import pandas as pd

    engine = create_engine(
        "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

    df = pd.read_sql(
        "SELECT id, video_id, username, comment, tanggal_komentar FROM komentar_mentah WHERE is_processed_vader = 1 AND is_processed_indobert = 0 LIMIT 200",
        engine
    )

    model_name = "w11wo/indonesian-roberta-base-sentiment-classifier"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    results = []

    def preprocess_teks(teks):
        import re
        teks = re.sub(r"http\S+|@\S+|#[A-Za-z0-9_]+", "", teks)
        teks = re.sub(r"[^a-zA-Z\s]", " ", teks)
        teks = teks.lower()
        return teks.strip()

    for _, row in df.iterrows():
        original_comment = row["comment"]
        cleaned_comment = preprocess_teks(original_comment)

        inputs = tokenizer(cleaned_comment, return_tensors="pt",
                           truncation=True, max_length=512)
        inputs = {k: v.long() for k, v in inputs.items()}

        with torch.no_grad():
            logits = model(**inputs).logits
            probs = softmax(logits, dim=1).squeeze()

        label_index = torch.argmax(probs).item()
        label = ["negatif", "netral", "positif"][label_index]
        confidence = float(probs[label_index].item())

        results.append({
            "mentah_id": row["id"],
            "video_id": row["video_id"],
            "username": row["username"],
            "tanggal_komentar": row["tanggal_komentar"],
            "comment": original_comment,
            "cleaned_comment": cleaned_comment,
            "indobert_sentiment_label": label,
            "indobert_confidence_score": confidence,
            "processed_at": datetime.now()
        })

    pd.DataFrame(results).to_sql("komentar_sentimen_indobert",
                                 con=engine, if_exists="append", index=False)

    with engine.begin() as conn:
        for row in results:
            conn.execute(text("UPDATE komentar_mentah SET is_processed_indobert = 1 WHERE id = :id"), {
                         "id": row["mentah_id"]})

    print("✅ Analisis IndoBERT selesai.")
