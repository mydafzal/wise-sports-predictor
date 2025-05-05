
import os
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from models.schemas import PredictionRequest
from utils.helpers import predictor, historical_data


router = APIRouter()

@router.post("/nba/predictions")
async def predict_scores(request: PredictionRequest):
    try:
        home_team = request.home_team
        away_team = request.away_team
        match_date = request.match_date

        predicted_home_score, predicted_away_score = predictor.predict_scores(
            home_team, away_team, match_date, historical_data
        )

        return {
            "home_team": home_team,
            "away_team": away_team,
            "match_date": match_date,
            "predicted_home_score": np.round(float(predicted_home_score), 0),
            "predicted_away_score": np.round(float(predicted_away_score), 0),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/nba/futurepredict")
async def future_predict():
    try:
        predictions_file = "Artifacts/FuturePredictions/future_predictions.csv"
        if not os.path.exists(predictions_file):
            raise HTTPException(status_code=404, detail="No future predictions found.")

        predictions_df = pd.read_csv(predictions_file)
        return {"predictions": predictions_df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))