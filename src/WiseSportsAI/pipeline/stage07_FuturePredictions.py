import requests
from WiseSportsAI.components.futurepredictions import FuturePredictions

FASTAPI_URL = "http://0.0.0.0:8080/predict"

def main():
    
    print("<------------------ 🚀 Stage07: Started Future Predictions ------------------>")

    future_predictions = FuturePredictions()

    tomorrow_games = future_predictions.fetch_tomorrows_games()

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
                else:
                    print(f"Failed to get prediction for {game['away_team']} vs {game['home_team']}: {response.text}")
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("No NBA games scheduled for tomorrow.")

    print("<------------------ ✅ Future Predictions Completed ------------------>\n\n")

if __name__ == "__main__":
    main()