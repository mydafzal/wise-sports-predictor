from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from utils.helpers import get_latest_file_by_pattern
import json, csv

router = APIRouter()

@router.get("/mlb/teamsadjustedpredictions", tags=["MLB Predictions"])
async def get_mlb_adjusted_predictions():
    adjusted_dir = Path("Artifacts/MLB_Artifacts/Adjusted_Predictions")
    latest_file = get_latest_file_by_pattern(adjusted_dir, "adjusted_predictions_*.json")

    if not latest_file:
        raise HTTPException(status_code=404, detail="No valid adjusted predictions found")

    try:
        with open(latest_file, "r") as f:
            predictions = json.load(f)

        processed = []
        for game in predictions:
            try:
                pred = game["prediction"]
                adj = pred.get("pitching_adjustment", {})
                adj_scores = adj.get("adjusted_scores", {})
                processed.append({
                    "game_time": game["game_time"],
                    "teams": f"{game['away_abbr']} @ {game['home_abbr']}",
                    "original_prediction": {
                        "home_runs": pred["predicted_home_runs"],
                        "away_runs": pred["predicted_away_runs"],
                        "winner": pred.get("predicted_winner", "N/A")
                    },
                    "adjusted_prediction": {
                        "home_runs": adj_scores.get("adjusted_home_runs", "N/A"),
                        "away_runs": adj_scores.get("adjusted_away_runs", "N/A"),
                        "winner": adj_scores.get("adjusted_winner", "N/A"),
                        "spread": adj.get("spread", "N/A"),
                        "total": adj.get("adjusted_total", "N/A")
                    },
                    "adjustment_details": {
                        "home_adjustment": adj.get("home_adjustment", 0),
                        "away_adjustment": adj.get("away_adjustment", 0),
                        "timestamp": game.get("adjustment_timestamp", "N/A")
                    }
                })
            except KeyError:
                continue

        return JSONResponse(content={
            "metadata": {
                "file_date": latest_file.stem.split("_")[-2:],
                "total_games": len(processed),
                "valid_games": len([g for g in processed if g["adjusted_prediction"]["home_runs"] != "N/A"])
            },
            "predictions": processed
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing predictions: {str(e)}")


@router.get("/mlb/pitchersadjustedpredictions", tags=["MLB Predictions"])
async def get_pitcher_adjusted_predictions():
    dir_path = Path("Artifacts/MLB_Artifacts/StartingPitcherAdjustments")
    latest_file = get_latest_file_by_pattern(dir_path, "starterpitcheradjusted_*.json")

    if not latest_file:
        raise HTTPException(status_code=404, detail="No valid pitcher-adjusted predictions found")

    try:
        with open(latest_file, "r") as f:
            predictions = json.load(f)

        processed = []
        for game in predictions:
            try:
                pred = game["prediction"]
                adj = pred["pitching_adjustment"]["pitcher_adjustments"]
                final_scores = adj.get("final_scores", {})
                processed.append({
                    "game_time": game["game_time"],
                    "home_team": game["home_team"],
                    "home_abbr": game["home_abbr"],
                    "away_team": game["away_team"],
                    "away_abbr": game["away_abbr"],
                    "pitcher_impacts": {
                        "home_pitcher_impact": adj.get("home_pitcher_impact", 0),
                        "away_pitcher_impact": adj.get("away_pitcher_impact", 0)
                    },
                    "final_scores": {
                        "home_runs": final_scores.get("home_runs", "N/A"),
                        "away_runs": final_scores.get("away_runs", "N/A"),
                        "winner": final_scores.get("winner", "N/A")
                    }
                })
            except KeyError:
                continue

        return JSONResponse(content={
            "metadata": {
                "file_date": latest_file.stem.split("_")[-2:],
                "total_games": len(processed),
                "valid_games": len([g for g in processed if g["final_scores"]["home_runs"] != "N/A"])
            },
            "predictions": processed
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing pitcher adjustments: {str(e)}")


@router.get("/mlb/weatheradjustedpredictions", tags=["MLB Predictions"])
async def get_weather_adjusted_predictions():
    dir_path = Path("Artifacts/MLB_Artifacts/WeatherAdjustments")
    latest_file = get_latest_file_by_pattern(dir_path, "weatheradjustments_*.csv")

    if not latest_file:
        raise HTTPException(status_code=404, detail="No valid weather-adjusted predictions found")

    try:
        processed = []
        with open(latest_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    processed.append({
                        "game_time": row["game_time"],
                        "home_team": row["home_team"],
                        "away_team": row["away_team"],
                        "original_prediction": {
                            "home_runs": float(row["original_home"]) if row["original_home"] else None,
                            "away_runs": float(row["original_away"]) if row["original_away"] else None
                        },
                        "adjusted_prediction": {
                            "home_runs": float(row["adjusted_home"]) if row["adjusted_home"] else None,
                            "away_runs": float(row["adjusted_away"]) if row["adjusted_away"] else None
                        },
                        "weather_impact": row["weather_impact"],
                        "error": row["error"] if row["error"] else None
                    })
                except (KeyError, ValueError):
                    continue

        return JSONResponse(content={
            "metadata": {
                "file_date": latest_file.stem.split("_")[-2:],
                "total_games": len(processed),
                "valid_games": len([g for g in processed if g["error"] is None])
            },
            "predictions": processed
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading weather CSV: {str(e)}")
