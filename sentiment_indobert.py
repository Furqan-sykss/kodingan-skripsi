from datetime import datetime
import torch
from torch.nn.functional import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sqlalchemy import create_engine
import pandas as pd

# Koneksi DB
engine = create_engine(
    "mysql+pymysql://root:@localhost/analisis_sentimen_kejagung_db")

# Load komentar mentah
df = pd.read_sql(
    "SELECT * FROM komentar_mentah WHERE is_processed=0 LIMIT 200", engine)

# Load IndoBERT
model = AutoModelForSequenceClassification.from_pretrained(
    "w11wo/indonesian-roberta-base-sentiment-classifier")
tokenizer = AutoTokenizer.from_pretrained(
    "w11wo/indonesian-roberta-base-sentiment-classifier")

results = []

for _, row in df.iterrows():
    inputs = tokenizer(row['comment'], return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = softmax(logits, dim=1).squeeze()
    label_index = torch.argmax(probs).item()
    label = ["negatif", "netral", "positif"][label_index]
    confidence = probs[label_index].item()

    results.append({
        "mentah_id": row['id'],
        "comment_original": row['comment'],
        "cleaned_comment": row['comment'].lower(),
        "label": label,
        "confidence": confidence,
        "processed_at": datetime.now()
    })

pd.DataFrame(results).to_sql("komentar_indobert",
                             con=engine, if_exists="append", index=False)
print("✅ IndoBERT selesai.")
