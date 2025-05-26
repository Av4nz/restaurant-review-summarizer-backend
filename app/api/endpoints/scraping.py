from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from app.scraper.gmaps_scraper import scrape_gmaps_reviews
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
    
def run_scraping(url: str):

    return scrape_gmaps_reviews(url)

@router.post("/scrape")
async def scrape_reviews(url: ScrapeURL):
    """
    Scrape reviews from Google Maps based on the provided url.
    Proses scraping dijalankan di thread pool agar endpoint tetap responsif.
    """
    try:
        loop = asyncio.get_running_loop()
        reviews = await loop.run_in_executor(None, run_scraping, url.url)
        return {"status": "success", "data": reviews}
    except Exception as e:
        return {"status": "error", "message": str(e)}