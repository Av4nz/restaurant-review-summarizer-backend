from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from app.scraper.gmaps_scraper import scrape_gmaps_reviews
from app.ml.sentiment_analysis import process_reviews_json
import asyncio

router = APIRouter()

class ScrapeURL(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        allowed_prefixes = [
            "https://www.google.com/maps/place/",
            "https://maps.app.goo.gl/"
        ]
        if not any(v.startswith(prefix) for prefix in allowed_prefixes):
            raise ValueError("URL must start with 'https://www.google.com/maps/place/' or 'https://maps.app.goo.gl/'")
        return v
    
def run_scraping_and_sentiment(url: str):
    scrape_gmaps_reviews(url)

    sentiment_results = process_reviews_json()
    return sentiment_results

@router.post("/scrape")
async def scrape_and_analyze(url: ScrapeURL):
    """
    Scrape reviews from Google Maps based on the provided url.
    Proses scraping dijalankan di thread pool agar endpoint tetap responsif.
    """
    try:
        loop = asyncio.get_running_loop()
        sentiment_results = await loop.run_in_executor(None, run_scraping_and_sentiment, url.url)
        return {"status": "success", 
                "message": "Scraping dan sentiment analysis selesai.","sentiment_results": sentiment_results[:3]}
    except Exception as e:
        return {"status": "error", "message": str(e)}