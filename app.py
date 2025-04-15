import os
import uvicorn
import pandas as pd
import numpy as np
import json
from datetime import date
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Optional
from datetime import datetime
from WiseSportsAI_NBA.components.modelpredictions import ModelPredictor
from WiseSportsAI_NBA.components.injuriesimpact import InjuriesImpact
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

BASE_DIR = Path("Artifacts/TeamStats")
HISTORICAL_PREDICTIONS_FILE = Path("Artifacts/FuturePredictions/historical_injuries_predictions.csv")

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    match_date: str

class DateSpecificPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    date: str  

class InjuryImpactResponse(BaseModel):
    home_team: str
    away_team: str
    original_home_score: float
    original_away_score: float
    initial_adjusted_home_score: float
    initial_adjusted_away_score: float
    final_adjusted_home_score: float
    final_adjusted_away_score: float
    home_net_impact: float
    away_net_impact: float
    home_injured_players: List[Dict]
    away_injured_players: List[Dict]
    cross_impact_home_boost: float
    cross_impact_away_boost: float

class TeamStatsResponse(BaseModel):
    team_name: str
    team_abbreviation: str
    team_id: str
    stats: Dict

class DateSpecificPredictionResponse(BaseModel):
    date: str
    home_team: str
    away_team: str
    original_home_score: int
    original_away_score: int
    adjusted_home_score: int
    adjusted_away_score: int
    home_net_impact: int
    away_net_impact: int
    home_injured_players: int
    away_injured_players: int
    home_injury_details: List[Dict]
    away_injury_details: List[Dict]
    cross_impact_home_boost: float
    cross_impact_away_boost: float
    note: Optional[str] = None


model_home_path = "Artifacts/TrainedModels/xgb_home_score_model.pkl"
model_away_path = "Artifacts/TrainedModels/xgb_away_score_model.pkl"
label_encoder_home_path = "Artifacts/LabelEncoderhome_team_name.pkl"
label_encoder_away_path = "Artifacts/LabelEncoderaway_team_name.pkl"
historical_data = pd.read_csv("Artifacts/DataScraping/MergedDataSet.csv")

predictor = ModelPredictor(model_home_path, model_away_path, label_encoder_home_path, label_encoder_away_path)
injuries_analyzer = InjuriesImpact()

def safe_float_convert(value, default=0.0):
    """Safely convert value to float with default fallback"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def load_historical_predictions() -> pd.DataFrame:
    """Load historical predictions data"""
    if not HISTORICAL_PREDICTIONS_FILE.exists():
        raise FileNotFoundError(f"Historical predictions file not found at {HISTORICAL_PREDICTIONS_FILE}")
    return pd.read_csv(HISTORICAL_PREDICTIONS_FILE)

@app.post("/nba/predictions")
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

@app.post("/nba/futurepredict")
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
    

@app.post("/nba/injuries_predictions", response_model=List[InjuryImpactResponse])
async def get_injuries_predictions():
    try:
        file_path = "Artifacts/FuturePredictions/future_injuries_predictions.csv"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="No injury-adjusted predictions found. Run injuries analysis first.")

        predictions_df = pd.read_csv(file_path)
        
        predictions_df['home_injury_details'] = predictions_df['home_injury_details'].apply(
            lambda x: eval(x) if isinstance(x, str) else []
        )
        predictions_df['away_injury_details'] = predictions_df['away_injury_details'].apply(
            lambda x: eval(x) if isinstance(x, str) else []
        )
        
        results = []
        for _, row in predictions_df.iterrows():
            results.append({
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "original_home_score": safe_float_convert(row["original_home_score"]),
                "original_away_score": safe_float_convert(row["original_away_score"]),
                "initial_adjusted_home_score": safe_float_convert(row.get("initial_adjusted_home_score", row["adjusted_home_score"])),
                "initial_adjusted_away_score": safe_float_convert(row.get("initial_adjusted_away_score", row["adjusted_away_score"])),
                "final_adjusted_home_score": safe_float_convert(row["adjusted_home_score"]),
                "final_adjusted_away_score": safe_float_convert(row["adjusted_away_score"]),
                "home_net_impact": safe_float_convert(row["home_net_impact"]),
                "away_net_impact": safe_float_convert(row["away_net_impact"]),
                "home_injured_players": row["home_injury_details"],
                "away_injured_players": row["away_injury_details"],
                "cross_impact_home_boost": safe_float_convert(row.get("cross_impact_home_boost", 0)),
                "cross_impact_away_boost": safe_float_convert(row.get("cross_impact_away_boost", 0))
            })
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
@app.post("/nba/injuries/predictions", response_model=DateSpecificPredictionResponse)
async def get_date_specific_prediction(request: DateSpecificPredictionRequest):
    """Get prediction for specific date with injury impact analysis"""
    try:
        # Validate date format
        datetime.strptime(request.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    try:
        df = load_historical_predictions()
        df['date_dt'] = pd.to_datetime(df['date'])
        request_date = pd.to_datetime(request.date)
        
        date_diff = (df['date_dt'] - request_date).abs()
        closest_date = df.loc[date_diff.idxmin(), 'date']
        
        prediction = df[
            (df['date'] == closest_date) & 
            (df['home_team'] == request.home_team) & 
            (df['away_team'] == request.away_team)
        ]
        
        if prediction.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No prediction found for {request.home_team} vs {request.away_team} on or near {request.date}"
            )
        
        result = prediction.iloc[0].to_dict()
        
        result.pop('date_dt', None)
        
        home_injuries = eval(result['home_injury_details']) if isinstance(result['home_injury_details'], str) else []
        away_injuries = eval(result['away_injury_details']) if isinstance(result['away_injury_details'], str) else []
        
        response_data = {
            "date": result["date"],
            "home_team": result["home_team"],
            "away_team": result["away_team"],
            "original_home_score": int(result["original_home_score"]),
            "original_away_score": int(result["original_away_score"]),
            "adjusted_home_score": int(result["adjusted_home_score"]),
            "adjusted_away_score": int(result["adjusted_away_score"]),
            "home_net_impact": int(result["home_net_impact"]),
            "away_net_impact": int(result["away_net_impact"]),
            "home_injured_players": len(home_injuries),
            "away_injured_players": len(away_injuries),
            "home_injury_details": home_injuries,
            "away_injury_details": away_injuries,
            "cross_impact_home_boost": safe_float_convert(result.get("cross_impact_home_boost", 0)),
            "cross_impact_away_boost": safe_float_convert(result.get("cross_impact_away_boost", 0))
        }
        
        if closest_date != request.date:
            response_data["note"] = f"Using prediction from {closest_date} (no prediction available for {request.date})"
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# +++++++++++++++++++++ MLB Routes +++++++++++++++++++++++
PREDICTION_DATE = date.today().strftime('%Y-%m-%d')
PREDICTION_FILE_PATH = Path(f"Artifacts/MLB_Artifacts/Future_Predictions/predictions_{PREDICTION_DATE}.json")

@app.get("/mlb/predictions")
async def get_mlb_predictions():
    if not PREDICTION_FILE_PATH.exists():
        raise HTTPException(status_code=404, detail="Predictions not found for today")

    try:
        with open(PREDICTION_FILE_PATH, "r") as f:
            predictions = json.load(f)
        return JSONResponse(content=predictions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading prediction file: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)