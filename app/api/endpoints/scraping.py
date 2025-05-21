from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from ...scrapper.gmaps_scraper import scrape_gmaps_reviews

router = APIRouter()

class ScrapeURL(BaseModel):
    url: str

    @field_validator("url")
    def validate_url(cls, v):
        if not v.startswith("https://www.google.com/maps/place/"):
            raise ValueError("URL must start with 'https://www.google.com/maps/place/'")
        return v

@router.post("/scrape")
def scrape_reviews(url: ScrapeURL):
    """
    Scrape reviews from Google Maps based on the provided url.
    """
    try:
        # Call the scraping function
        # reviews = scrape_gmaps_reviews(url)
        reviews = scrape_gmaps_reviews(url)
        return {"status": "success", "data": reviews}
    except Exception as e:
        return {"status": "error", "message": str(e)}