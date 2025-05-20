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

# from transformers import T5Tokenizer, T5ForConditionalGeneration
# import pandas as pd
# tokenizer = T5Tokenizer.from_pretrained("cahya/t5-base-indonesian-summarization-cased")
# model = T5ForConditionalGeneration.from_pretrained("cahya/t5-base-indonesian-summarization-cased")

# def summarize_article(csv_path):
#     df = pd.read_csv(csv_path)
#     reviews = df['review'].dropna().tolist()
#     text = ' '.join(reviews)
#     input_ids = tokenizer.encode("ringkaskan: " + text, return_tensors='pt')
#     summary_ids = model.generate(input_ids,
#                 min_length=50,
#                 max_length=200,
#                 num_beams=10,
#                 repetition_penalty=2.5,
#                 length_penalty=1.0,
#                 early_stopping=True,
#                 no_repeat_ngram_size=2,
#                 use_cache=True,
#                 do_sample = True,
#                 temperature = 0.8,
#                 top_k = 50,
#                 top_p = 0.95)

#     return tokenizer.decode(summary_ids[0], skip_special_tokens=True)