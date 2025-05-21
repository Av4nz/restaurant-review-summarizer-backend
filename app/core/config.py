from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SUMMARY_JSON_DIR = BASE_DIR / "data" / "summary.json"
MODEL_PATH = BASE_DIR / "ml_models" / "model.pth"
JSON_FILE = BASE_DIR / "data" / "data.json"
PRETRAINED_MODEL = "indolem/indobert-base-uncased"
DATA_DIR = BASE_DIR / "data"