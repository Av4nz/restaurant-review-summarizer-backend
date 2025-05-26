from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SUMMARY_JSON_DIR = BASE_DIR / "data" / "all_sentiments_keywords_summary.json"
MODEL_PATH = BASE_DIR / "ml_models" / "model.pth"
JSON_FILE = BASE_DIR / "data" / "google_maps_reviews.json"
SENTIMENT_JSON_FILE = BASE_DIR / "data" / "google_maps_reviews_with_sentiment.json"
PRETRAINED_MODEL = "indolem/indobert-base-uncased"
DATA_DIR = BASE_DIR / "data"

