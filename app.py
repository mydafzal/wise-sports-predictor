import os
import uvicorn
import pandas as pd
import numpy as np
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict
from WiseSportsAI.components.modelpredictions import ModelPredictor

app = FastAPI()

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    match_date: str

class InjuryImpactResponse(BaseModel):
    home_team: str
    away_team: str
    original_home_score: float
    original_away_score: float
    adjusted_home_score: float
    adjusted_away_score: float
    home_net_impact: float
    away_net_impact: float
    home_injured_players: List[Dict]
    away_injured_players: List[Dict]

model_home_path = "Artifacts/TrainedModels/xgb_home_score_model.pkl"
model_away_path = "Artifacts/TrainedModels/xgb_away_score_model.pkl"
label_encoder_home_path = "Artifacts/LabelEncoderhome_team_name.pkl"
label_encoder_away_path = "Artifacts/LabelEncoderaway_team_name.pkl"
historical_data = pd.read_csv("Artifacts/DataScraping/MergedDataSet.csv")

predictor = ModelPredictor(model_home_path, model_away_path, label_encoder_home_path, label_encoder_away_path)

@app.post("/predict")
async def predict_scores(request: PredictionRequest):
    try:
        home_team = request.home_team
        away_team = request.away_team
        match_date = request.match_date

        predicted_home_score, predicted_away_score = predictor.predict_scores(
            home_team, away_team, match_date, historical_data
        )

        predicted_home_score = float(predicted_home_score)
        predicted_away_score = float(predicted_away_score)

        return {
            "home_team": home_team,
            "away_team": away_team,
            "match_date": match_date,
            "predicted_home_score": np.round(predicted_home_score, 0),
            "predicted_away_score": np.round(predicted_away_score, 0),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/futurepredict")
async def future_predict():
    try:
        predictions_file = "Artifacts/FuturePredictions/future_predictions.csv"
        if not os.path.exists(predictions_file):
            raise HTTPException(status_code=404, detail="No future predictions found.")

        predictions_df = pd.read_csv(predictions_file)
        predictions = predictions_df.to_dict(orient="records")

        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/injuries-predictions", response_model=List[InjuryImpactResponse])
async def get_injuries_predictions():
    try:
        file_path = "Artifacts/FuturePredictions/future_injuries_predictions.csv"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="No injury-adjusted predictions found")

        predictions_df = pd.read_csv(file_path)
        
        predictions_df['home_injury_details'] = predictions_df['home_injury_details'].apply(eval)
        predictions_df['away_injury_details'] = predictions_df['away_injury_details'].apply(eval)
        
        predictions = []
        for _, row in predictions_df.iterrows():
            predictions.append({
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "original_home_score": float(row["original_home_score"]),
                "original_away_score": float(row["original_away_score"]),
                "adjusted_home_score": float(row["adjusted_home_score"]),
                "adjusted_away_score": float(row["adjusted_away_score"]),
                "home_net_impact": float(row["home_net_impact"]),
                "away_net_impact": float(row["away_net_impact"]),
                "home_injured_players": row["home_injury_details"],
                "away_injured_players": row["away_injury_details"]
            })
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)