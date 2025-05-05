
from fastapi import APIRouter, HTTPException, Query, Response, FastAPI
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import json
import math
import os
from pathlib import Path
from datetime import datetime, timedelta

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if pd.isna(obj) or (isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj))):
                return 0.0
            return super().default(obj)
        except TypeError:
            return str(obj)

# Custom response class that uses our JSON encoder
class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomJSONEncoder,
        ).encode("utf-8")

router = APIRouter(tags=["MLB Predictions"])

class BettingConfidenceCalculator:
    def __init__(self):
        """Initialize the betting confidence calculator."""
        pass
    
    def calculate_total_confidence(self, predicted_total: float, line_total: float) -> float:
        confidence = 50 + (abs(predicted_total - line_total) * 25)
        return min(100, confidence)
    
    def calculate_spread_confidence(self, predicted_margin: float, spread_line: float) -> float:
        confidence = 50 + ((predicted_margin - spread_line) * 25)
        return min(100, max(0, confidence))
    
    def get_confidence_stars(self, confidence: float) -> str:
        if confidence >= 90:
            return "★★★★★"
        elif confidence >= 75:
            return "★★★★☆"
        elif confidence >= 60:
            return "★★★☆☆"
        elif confidence >= 50:
            return "★★☆☆☆"
        else:
            return "★☆☆☆☆"

def load_betting_lines(date_str: str) -> Dict:
    try:
        lines_path = f"data/betting_lines/{date_str}.json"
        if not os.path.exists(lines_path):
            return {}
            
        with open(lines_path, 'r') as f:
            betting_lines = json.load(f)
        
        lines_dict = {}
        for game in betting_lines:
            game_id = f"{game['away_team']}@{game['home_team']}"
            lines_dict[game_id] = {
                'spread_line': game.get('spread_line', 0),
                'total_line': game.get('total_line', 0)
            }
        
        return lines_dict
    except Exception as e:
        print(f"Error loading betting lines: {str(e)}")
        return {}

def load_finalscores_predictions(date_str: str) -> pd.DataFrame:
    try:
        artifacts_dir = Path("Artifacts/MLB_Artifacts/WeatherAdjustments")
        if not artifacts_dir.exists():
            raise FileNotFoundError(f"Directory {artifacts_dir} not found")

        pattern = f"weatheradjustments_{date_str}_*.csv"
        matching_files = list(artifacts_dir.glob(pattern))

        if not matching_files:
            yesterday_date = (datetime.strptime(date_str, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
            pattern_yesterday = f"weatheradjustments_{yesterday_date}_*.csv"
            matching_files = list(artifacts_dir.glob(pattern_yesterday))
            if not matching_files:
                raise FileNotFoundError(f"No predictions found for {date_str} or yesterday")

        def extract_timestamp(file_path):
            filename = file_path.stem
            parts = filename.split('_')
            if len(parts) >= 3:
                try:
                    return int(parts[2])
                except:
                    return 0
            return 0

        matching_files.sort(key=lambda x: extract_timestamp(x), reverse=True)
        latest_file = matching_files[0]

        df = pd.read_csv(latest_file)
        required_cols = ['game_time', 'home_team', 'away_team', 'adjusted_home', 'adjusted_away']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
                
        return df

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error loading predictions: {str(e)}")

# Helper function to ensure JSON serializability
def clean_float(value):
    """Convert numpy/pandas numeric types to Python float and handle NaN/Inf values."""
    if pd.isna(value) or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

@router.get("/mlb/finalscores", tags=["MLB Predictions"], response_class=CustomJSONResponse)
async def get_finalscores(date: Optional[str] = None):
    if not date:
        date = datetime.today().strftime("%Y%m%d")
    
    try:
        predictions_df = load_finalscores_predictions(date)
        betting_lines = load_betting_lines(date)
        calculator = BettingConfidenceCalculator()
        
        processed = []
        
        for _, row in predictions_df.iterrows():
            try:
                # Skip rows with missing critical values
                if pd.isna(row.get('adjusted_home')) or pd.isna(row.get('adjusted_away')):
                    continue
                
                game_id = f"{row['away_team']}@{row['home_team']}"
                game_lines = betting_lines.get(game_id, {'spread_line': -1.5, 'total_line': 8.5})
                
                # Clean all float values to ensure they're JSON serializable
                home_runs = clean_float(row['adjusted_home'])
                away_runs = clean_float(row['adjusted_away'])
                spread_line = clean_float(game_lines.get('spread_line', 0))
                total_line = clean_float(game_lines.get('total_line', 0))
                
                predicted_total = home_runs + away_runs
                predicted_margin = home_runs - away_runs
                
                # Calculate confidences and ensure they're clean floats
                spread_confidence = clean_float(calculator.calculate_spread_confidence(
                    predicted_margin, spread_line))
                total_confidence = clean_float(calculator.calculate_total_confidence(
                    predicted_total, total_line))
                
                # Create recommendations
                total_rec = f"OVER {total_line}" if predicted_total > total_line else f"UNDER {total_line}"
                spread_rec = (f"{row['home_team']} covers {spread_line}" 
                            if predicted_margin > spread_line 
                            else f"{row['away_team']} covers +{-spread_line}")
                
                # Ensure all string values have defaults
                weather_impact = str(row.get('weather_impact', '')) if not pd.isna(row.get('weather_impact')) else ''
                error_message = str(row.get('error', '')) if not pd.isna(row.get('error')) else ''
                
                game_entry = {
                    "game_time": str(row['game_time']),
                    "home_team": str(row['home_team']),
                    "away_team": str(row['away_team']),
                    "adjusted_scores": {
                        "home": round(home_runs, 2),
                        "away": round(away_runs, 2)
                    },
                    "metrics": {
                        "total_line": total_line,
                        "predicted_total": round(predicted_total, 2),
                        "total_confidence": round(total_confidence, 2),
                        "total_recommendation": total_rec,
                        "spread_line": spread_line,
                        "predicted_margin": round(predicted_margin, 2),
                        "spread_confidence": round(spread_confidence, 2),
                        "spread_recommendation": spread_rec
                    },
                    "weather": weather_impact,
                    "error": error_message
                }
                
                processed.append(game_entry)
                
            except Exception as e:
                print(f"Skipping game {row.get('home_team','')} due to error: {str(e)}")
        
        result = {
            "date": date,
            "games_processed": len(processed),
            "timestamp": datetime.now().isoformat(),
            "games": processed
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))