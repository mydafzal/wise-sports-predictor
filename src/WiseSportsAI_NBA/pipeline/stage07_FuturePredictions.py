import requests
import pandas as pd
import os
from WiseSportsAI_NBA.components.futurepredictions import FuturePredictions
from WiseSportsAI_NBA.logging import logger
from WiseSportsAI_NBA.utils.utils import read_yaml

FASTAPI_URL = "http://0.0.0.0:8080/predict"
PREDICTIONS_FILE = "Artifacts/FuturePredictions/future_predictions.csv"

def main():
    print("<------------------ 🚀 Stage07: Started Future Predictions ------------------>")
    logger.info("<------------------ 🚀 Stage07: Started Future Predictions ------------------>")

    future_predictions = FuturePredictions()
    tomorrow_games = future_predictions.fetch_tomorrows_games()

    predictions = []

    if tomorrow_games:
        print(f"NBA Games for {future_predictions.tomorrow} with Predictions:")
        for game in tomorrow_games:
            payload = {
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "match_date": game["date"]
            }
            try:
                response = requests.post(FASTAPI_URL, json=payload)
                if response.status_code == 200:
                    prediction = response.json()
                    print(f"{game['away_team']} vs {game['home_team']} on {game['date']}")
                    print(f"Predicted Score -> {game['home_team']}: {prediction['predicted_home_score']}, {game['away_team']}: {prediction['predicted_away_score']}")
                    print("-" * 40)

                    # Store prediction in a list
                    predictions.append({
                        "home_team": game["home_team"],
                        "away_team": game["away_team"],
                        "match_date": game["date"],
                        "predicted_home_score": prediction["predicted_home_score"],
                        "predicted_away_score": prediction["predicted_away_score"]
                    })
                else:
                    print(f"Failed to get prediction for {game['away_team']} vs {game['home_team']}: {response.text}")
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("No NBA games scheduled for tomorrow.")

    # Save predictions to a file
    if predictions:
        os.makedirs(os.path.dirname(PREDICTIONS_FILE), exist_ok=True)
        predictions_df = pd.DataFrame(predictions)
        predictions_df.to_csv(PREDICTIONS_FILE, index=False)
        print(f"Predictions saved to {PREDICTIONS_FILE}")

    print("<------------------ ✅ Future Predictions Completed ------------------>\n\n")
    logger.info("<------------------ ✅ Future Predictions Completed ------------------>")

if __name__ == "__main__":
    main()