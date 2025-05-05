from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import date
import json

router = APIRouter()

PREDICTION_DATE = date.today().strftime('%Y-%m-%d')
PREDICTION_FILE_PATH = Path(f"Artifacts/MLB_Artifacts/Future_Predictions/predictions_{PREDICTION_DATE}.json")

@router.get("/mlb/modelpredictions", tags=["MLB Predictions"])
async def get_mlb_predictions():
    if not PREDICTION_FILE_PATH.exists():
        raise HTTPException(status_code=404, detail="Predictions not found for today")

    try:
        with open(PREDICTION_FILE_PATH, "r") as f:
            predictions = json.load(f)
        return JSONResponse(content=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading prediction file: {str(e)}")
