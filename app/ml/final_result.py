import json
from collections import Counter
import re
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("cahya/t5-base-indonesian-summarization-cased")
model = T5ForConditionalGeneration.from_pretrained("cahya/t5-base-indonesian-summarization-cased")

# Download nltk resources
nltk.download('punkt')
nltk.download('stopwords')

# Load Indonesian stopwords
stop_words = set(stopwords.words('indonesian'))

# Load stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()
stopword_factory = StopWordRemoverFactory()
indo_stopwords = set(stopword_factory.get_stop_words())


def summarize_reviews(data):
    reviews = [item.get('text', '') for item in data if item.get('text')]
    text = '. '.join(reviews)
    input_ids = tokenizer.encode(text, return_tensors='pt')
    summary_ids = model.generate(
        input_ids,
        min_length=50,
        max_length=200,
        num_beams=10,
        repetition_penalty=2.5,
        length_penalty=1.0,
        early_stopping=True,
        no_repeat_ngram_size=2,
        use_cache=True,
        do_sample=True,
        temperature=0.8,
        top_k=50,
        top_p=0.95
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Regex to clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text

# Preprocess text: clean, stem, remove stopwords
def preprocess_text(text):
    # Tokenize
    tokens = word_tokenize(clean_text(text))
    # Remove stopwords, stem, remove words less than 3 letters
    filtered = [
        stemmer.stem(word)
        for word in tokens
        if word not in (stop_words or indo_stopwords) and word.isalpha() and len(word) >= 3
    ]
    return filtered

# Load reviews from JSON
def load_reviews(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Process reviews by sentiment
def process_reviews_by_sentiment(data):
    sentiment_groups = {'positive': [], 'neutral': [], 'negative': []}
    for item in data:
        sentiment = item.get('sentiment')
        review = item.get('text')
        if sentiment in sentiment_groups:
            sentiment_groups[sentiment].append(review)
    return sentiment_groups

# Generate keyword JSON format
def generate_keyword_json(words, top_n=30):
    counter = Counter(words)
    most_common = counter.most_common(top_n)
    return [{"keyword": word, "count": count} for word, count in most_common]

# Main function
def main_result():
    data = load_reviews("data/reviews_with_sentiment.json")
    sentiment_groups = process_reviews_by_sentiment(data)

    results = {}
    for sentiment, reviews in sentiment_groups.items():
        all_words = []
        for review in reviews:
            all_words.extend(preprocess_text(review))
        results[sentiment] = generate_keyword_json(all_words)

    # Generate summaries for each sentiment
    summaries = {}
    for sentiment, reviews in sentiment_groups.items():
        summaries[sentiment] = summarize_reviews([{"text": r} for r in reviews])

    # Save all keywords and summaries in one JSON file
    output = {
        "summary": {
            "positive : "+ summaries.get("positive", "")+". "+
            "neutral : "+ summaries.get("neutral", "")+". "+
            "negative : "+ summaries.get("negative", "")+". ",
        },
        "positive": {
            "keywords": results.get("positive", [])
        },
        "neutral": {
            "keywords": results.get("neutral", [])
        },
        "negative": {
            "keywords": results.get("negative", [])
        }
    }
    with open('data/all_sentiments_keywords_summary.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("Keyword JSON files generated for each sentiment.")

