from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()
DATA_FILE = 'data/review_summary.json'

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/review-summary")
async def get_review_summary():
    """
    Get the review summary from the JSON file.
    """
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail="Review summary not found")

    with open(DATA_FILE, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error decoding JSON")

    return data