import os
from fastapi import APIRouter, HTTPException
from models.schemas import InjuryImpactResponse, DateSpecificPredictionRequest, DateSpecificPredictionResponse
from utils.helpers import safe_float_convert, load_historical_predictions
import pandas as pd
from datetime import datetime

router = APIRouter()

@router.post("/nba/injuries_predictions", response_model=list[InjuryImpactResponse])
async def get_injuries_predictions():
    try:
        file_path = "Artifacts/FuturePredictions/future_injuries_predictions.csv"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="No injury-adjusted predictions found.")

        df = pd.read_csv(file_path)
        df['home_injury_details'] = df['home_injury_details'].apply(lambda x: eval(x) if isinstance(x, str) else [])
        df['away_injury_details'] = df['away_injury_details'].apply(lambda x: eval(x) if isinstance(x, str) else [])

        return [{
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
        } for _, row in df.iterrows()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nba/injuries/predictions", response_model=DateSpecificPredictionResponse)
async def get_date_specific_prediction(request: DateSpecificPredictionRequest):
    try:
        datetime.strptime(request.date, "%Y-%m-%d")
        df = load_historical_predictions()
        df['date_dt'] = pd.to_datetime(df['date'])
        request_date = pd.to_datetime(request.date)
        closest_date = df.loc[(df['date_dt'] - request_date).abs().idxmin(), 'date']

        prediction = df[
            (df['date'] == closest_date) & 
            (df['home_team'] == request.home_team) & 
            (df['away_team'] == request.away_team)
        ]

        if prediction.empty:
            raise HTTPException(status_code=404, detail="Prediction not found.")

        row = prediction.iloc[0].to_dict()
        row.pop('date_dt', None)
        home_injuries = eval(row['home_injury_details']) if isinstance(row['home_injury_details'], str) else []
        away_injuries = eval(row['away_injury_details']) if isinstance(row['away_injury_details'], str) else []

        result = {
            "date": row["date"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "original_home_score": int(row["original_home_score"]),
            "original_away_score": int(row["original_away_score"]),
            "adjusted_home_score": int(row["adjusted_home_score"]),
            "adjusted_away_score": int(row["adjusted_away_score"]),
            "home_net_impact": int(row["home_net_impact"]),
            "away_net_impact": int(row["away_net_impact"]),
            "home_injured_players": len(home_injuries),
            "away_injured_players": len(away_injuries),
            "home_injury_details": home_injuries,
            "away_injury_details": away_injuries,
            "cross_impact_home_boost": safe_float_convert(row.get("cross_impact_home_boost", 0)),
            "cross_impact_away_boost": safe_float_convert(row.get("cross_impact_away_boost", 0)),
        }

        if row["date"] != request.date:
            result["note"] = f"Using prediction from {row['date']} (closest match found)."

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
