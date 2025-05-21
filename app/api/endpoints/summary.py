from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
def reviews_summary():
    return