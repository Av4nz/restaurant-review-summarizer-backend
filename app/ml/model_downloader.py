import os
import requests
from pathlib import Path
from app.core.config import MODEL_PATH

def download_model_from_gdrive(dest_path):
    url = "https://drive.google.com/file/d/16W45YwmyasFFcUE05t-z1v3Y0iJMdjG3/view?usp=sharing"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        raise Exception("Failed to download model from Google Drive")
    
def ensure_model_downloaded():
    """Ensure the model is downloaded from Google Drive."""
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Downloading...")
        download_model_from_gdrive(MODEL_PATH)
        print("Model downloaded successfully.")
    else:
        print(f"Model already exists at {MODEL_PATH}. No need to download.")