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
        if not os.path.exists(SUMMARY_JSON_DIR):
            main_result()
        

        with open(SUMMARY_JSON_DIR, "r", encoding="utf-8") as f:
            try:
                summary_results = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON file: {e}")
            
        # try:
        #     os.remove(SUMMARY_JSON_DIR)
        #     print(f"{SUMMARY_JSON_DIR} deleted after reading")
        # except Exception as e:
        #     print(f"Error deleting {SUMMARY_JSON_DIR}: {e}")

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