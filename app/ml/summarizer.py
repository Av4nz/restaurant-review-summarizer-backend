from transformers import T5Tokenizer, T5ForConditionalGeneration
import pandas as pd

tokenizer = T5Tokenizer.from_pretrained("cahya/t5-base-indonesian-summarization-cased")
model = T5ForConditionalGeneration.from_pretrained("cahya/t5-base-indonesian-summarization-cased")

# Funsi masih memanggil .csv dan me-return teks string
# aku masih bingung apakah path hasil scraping disini bakal berganti atau tetap
# bisa diganti ID di .json yang ingin di summarize
def summarize_reviews(path):
    df = pd.read_csv(path)
    reviews = df['review'].dropna().tolist()
    text = '. '.join(reviews)
    input_ids = tokenizer.encode(text, return_tensors='pt')
    summary_ids = model.generate(input_ids,
                min_length=50,
                max_length=200,
                num_beams=10,
                repetition_penalty=2.5,
                length_penalty=1.0,
                early_stopping=True,
                no_repeat_ngram_size=2,
                use_cache=True,
                do_sample = True,
                temperature = 0.8,
                top_k = 50,
                top_p = 0.95)

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)