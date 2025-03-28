import os
import uvicorn
import pandas as pd
import numpy as np
import json
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Optional
from WiseSportsAI.components.modelpredictions import ModelPredictor
from WiseSportsAI.components.injuriesimpact import InjuriesImpact
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

# Configuration
BASE_DIR = Path("Artifacts/TeamStats")
TEAM_MAPPING_FILE = Path("Artifacts/TeamInfo/team_mapping.csv")

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    match_date: str

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

TEAM_ABBREVIATIONS = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN", "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE", "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET", "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "LA Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM", "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP", "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA", "Washington Wizards": "WAS"
}

ESPN_TO_FASTAPI_MAPPING = {"PHX": "PHO", "CHA": "CHO", "BKN": "BRK"}

# Initialize mappings
ABBREVIATION_TO_ID = {}
TEAM_ABBREVIATIONS_REVERSED = {v: k for k, v in TEAM_ABBREVIATIONS.items()}

# Initialize models and data
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

def load_team_mapping() -> Dict[str, str]:
    """Load team abbreviation to ID mapping"""
    if not TEAM_MAPPING_FILE.exists():
        raise FileNotFoundError(f"Team mapping file not found at {TEAM_MAPPING_FILE}")
    
    df = pd.read_csv(TEAM_MAPPING_FILE)
    global ABBREVIATION_TO_ID
    
    # Create mapping from abbreviation to team ID
    for _, row in df.iterrows():
        team_name = row['team_name']
        if team_name in TEAM_ABBREVIATIONS:
            abbrev = TEAM_ABBREVIATIONS[team_name]
            ABBREVIATION_TO_ID[abbrev] = row['team_id']
    
    return ABBREVIATION_TO_ID

@app.on_event("startup")
async def startup_event():
    """Initialize application state"""
    # Ensure the team stats directory exists
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load team mappings
    try:
        load_team_mapping()
    except Exception as e:
        print(f"Failed to load team mapping: {e}")

# Existing routes
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

# Team stats routes
@app.get("/team/{team_abbrev}", response_model=TeamStatsResponse)
async def get_team_stats_by_abbrev(team_abbrev: str):
    """Get stats for a team by abbreviation (e.g., GSW, LAL)"""
    try:
        # Handle any abbreviation mappings
        team_abbrev = team_abbrev.upper()
        team_abbrev = ESPN_TO_FASTAPI_MAPPING.get(team_abbrev, team_abbrev)
        
        if team_abbrev not in ABBREVIATION_TO_ID:
            raise HTTPException(status_code=404, detail="Team abbreviation not found")
        
        team_id = ABBREVIATION_TO_ID[team_abbrev]
        stats_file = BASE_DIR / f"{team_id}.json"
        
        if not stats_file.exists():
            raise HTTPException(status_code=404, detail="Team stats not available")
        
        with open(stats_file, 'r') as f:
            stats_data = json.load(f)
        
        return {
            "team_name": TEAM_ABBREVIATIONS_REVERSED.get(team_abbrev, team_abbrev),
            "team_abbreviation": team_abbrev,
            "team_id": team_id,
            "stats": stats_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/abbreviations", response_class=JSONResponse)
async def list_team_abbreviations():
    """List all available team abbreviations"""
    try:
        return {
            "abbreviations": list(ABBREVIATION_TO_ID.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)