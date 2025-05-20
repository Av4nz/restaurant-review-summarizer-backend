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
