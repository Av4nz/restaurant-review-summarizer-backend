import json
from collections import Counter
import re
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

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
def main():
    data = load_reviews('data/reviews_with_sentiment.json')
    sentiment_groups = process_reviews_by_sentiment(data)

    results = {}
    for sentiment, reviews in sentiment_groups.items():
        all_words = []
        for review in reviews:
            all_words.extend(preprocess_text(review))
        results[sentiment] = generate_keyword_json(all_words)

    # Save each sentiment to its own JSON file
    for sentiment, keywords in results.items():
        with open(f'data/{sentiment}_keywords.json', 'w', encoding='utf-8') as f:
            json.dump({"keywords": keywords}, f, ensure_ascii=False, indent=2)

    print("Keyword JSON files generated for each sentiment.")

