# ml/summarization.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd

model_name = "cahya/bert2bert-indonesian-summarization"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def summarize_reviews(csv_path):
    df = pd.read_csv(csv_path)
    reviews = df['review'].dropna().tolist()
    text = ' '.join(reviews)[:2048]  # truncate if needed
    inputs = tokenizer.encode("ringkaskan: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=200, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
