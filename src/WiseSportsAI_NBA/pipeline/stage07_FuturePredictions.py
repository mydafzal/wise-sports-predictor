import requests
import pandas as pd
import os
from WiseSportsAI_NBA.components.futurepredictions import FuturePredictions
from WiseSportsAI_NBA.logging import logger
from datetime import datetime

FASTAPI_URL = "http://0.0.0.0:8080/nba/predictions"
PREDICTIONS_FILE = "Artifacts/FuturePredictions/future_predictions.csv"

def main():
    print("\n<------------------ 🚀 Stage07: Started Future Predictions ------------------>")
    logger.info("<------------------ 🚀 Stage07: Started Future Predictions ------------------>")

    try:
        future_predictions = FuturePredictions()
        tomorrow_games = future_predictions.fetch_tomorrows_games()
        predictions = []

        if tomorrow_games:
            print(f"\nFound {len(tomorrow_games)} NBA games for {future_predictions.target_date}:")
            for game in tomorrow_games:
                print(f"  - {game['away_team']} @ {game['home_team']}")
                
                payload = {
                    "home_team": game["home_team"],
                    "away_team": game["away_team"],
                    "match_date": game["date"]
                }
                try:
                    response = requests.post(FASTAPI_URL, json=payload)
                    if response.status_code == 200:
                        prediction = response.json()
                        predictions.append({
                            "home_team": game["home_team"],
                            "away_team": game["away_team"],
                            "match_date": game["date"],
                            "predicted_home_score": prediction["predicted_home_score"],
                            "predicted_away_score": prediction["predicted_away_score"]
                        })
                        print(f"    ✅ Prediction successful")
                    else:
                        print(f"    ❌ Prediction failed: {response.text}")
                except Exception as e:
                    print(f"    ❌ Prediction error: {str(e)}")
            
            # Save predictions
            if predictions:
                os.makedirs(os.path.dirname(PREDICTIONS_FILE), exist_ok=True)
                pd.DataFrame(predictions).to_csv(PREDICTIONS_FILE, index=False)
                print(f"\nSaved predictions to {PREDICTIONS_FILE}")
        else:
            print(f"\nNo NBA games found for {future_predictions.target_date}")

    except Exception as e:
        logger.error(f"Error in future predictions: {str(e)}")
        print(f"\n❌ Error occurred: {str(e)}")

    print("\n<------------------ ✅ Future Predictions Completed ------------------>")
    logger.info("<------------------ ✅ Future Predictions Completed ------------------>")

if __name__ == "__main__":
    main()