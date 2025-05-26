from fastapi import APIRouter

router = APIRouter()

@router.get("/summary-results")
def reviews_summary():
    return