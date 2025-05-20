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
│   ├── models/                   # Pydantic schemas (request/response model)
│   │   └── review_model.py
│   ├── ml/                       # Machine Learning model & utils
│   │   ├── __init__.py
│   │   ├── summarizer.py         # Ringkasan review
│   │   └── wordcloud_generator.py
│   ├── scrapers/                 # Web scraping logic
│   │   ├── __init__.py
│   │   └── gmaps_scraper.py
│   ├── services/                 # Logic pemrosesan (menghubungkan scraping, ML, dll)
│   │   └── review_service.py
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
