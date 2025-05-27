Download the ML Model for the Sentiment Analysis [here](https://drive.google.com/file/d/16W45YwmyasFFcUE05t-z1v3Y0iJMdjG3/view?usp=sharing)

Folder structure:
```
backend/
├── app/                          # Main application package
│   ├── api/                      # FastAPI routers
│   │   ├── __init__.py
│   │   ├── endpoints/            # Endpoint handler per fitur
│   │   │   ├── reviews.py
│   │   │   └── scraping.py
│   ├── core/                     # Konfigurasi (settings, logger, constants)
│   │   └── config.py
│   ├── ml/                       # Machine Learning model & utils
│   │   ├── __init__.py
│   │   ├── summarizer.py         # Ringkasan review
│   │   └── wordcloud_generator.py
│   ├── scrapers/                 # Web scraping logic
│   │   ├── __init__.py
│   │   └── gmaps_scraper.py
│   └── main.py                   # Entry point FastAPI
├── data/                         # File JSON hasil/penyimpanan lokal
│   ├── reviews.json
│   └── ...
├── ml_models/                    # Folder tempat file .pkl atau model ML lain
│   └── summarizer_model.pkl
├── requirements.txt              # Dependency
└── README.md
```


Create your own `Virtual Environment`:
```
python -m venv venv
```

Activate your `Virtual Environment`:
```
venv\Scripts\activate
```

Install the required dependencies:
```
pip install -r requirements.txt
```

Run the app:
```
uvicorn app.main:app --reload
```
