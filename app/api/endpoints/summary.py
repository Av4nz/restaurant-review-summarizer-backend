from fastapi import APIRouter
from app.ml.final_result import main_result
from app.core.config import SUMMARY_JSON_DIR
import json
import os
import asyncio

router = APIRouter()

@router.get("/summary-results")
def reviews_summary():
    try:
        # Pastikan file summary sudah ada, jika belum bisa generate dulu
        if not os.path.exists(SUMMARY_JSON_DIR):
            main_result()  # generate summary jika file belum ada

        with open(SUMMARY_JSON_DIR, "r", encoding="utf-8") as f:
            summary_results = json.load(f)

        return {
            "status": "success",
            "message": "Summary results loaded successfully.",
            "summary_results": summary_results
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }