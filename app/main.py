from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import scraping, summary, food_filter
from app.ml.model_downloader import ensure_model_downloaded

app = FastAPI()

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

ensure_model_downloaded()

app.include_router(scraping.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(food_filter.router, prefix="/api")