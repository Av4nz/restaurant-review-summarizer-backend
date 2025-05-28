import os
from pathlib import Path
from app.core.config import MODEL_PATH

def ensure_ml_models_folder_exists():
    """Ensure the 'ml_models' folder exists. If not, create it."""
    ml_models_folder = Path(MODEL_PATH).parent
    if not ml_models_folder.exists():
        print(f"Folder '{ml_models_folder}' does not exist. Creating...")
        ml_models_folder.mkdir(parents=True, exist_ok=True)
        print(f"Folder '{ml_models_folder}' created.")
    else:
        print(f"Folder '{ml_models_folder}' already exists.")

def download_model_from_gdrive(dest_path):
    import gdown
    url = "https://drive.google.com/uc?id=16W45YwmyasFFcUE05t-z1v3Y0iJMdjG3"
    gdown.download(url, str(dest_path), quiet=False)
    
def ensure_model_downloaded():
    """Ensure the model is downloaded from Google Drive."""
    ensure_ml_models_folder_exists()
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Downloading...")
        download_model_from_gdrive(MODEL_PATH)
        print("Model downloaded successfully.")
    else:
        print(f"Model already exists at {MODEL_PATH}. No need to download.")