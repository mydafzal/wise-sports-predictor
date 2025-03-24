import pandas as pd
import os
from WiseSportsAI.components.injuriesimpact import InjuriesImpact
from WiseSportsAI.logging import logger

PREDICTIONS_FILE = "Artifacts/FuturePredictions/future_predictions.csv"
OUTPUT_FILE = "Artifacts/FuturePredictions/future_injuries_predictions.csv"

def main():
    print("<------------------ 🚀 Stage08: Started Injuries Impact Analysis ------------------>")
    logger.info("<------------------ 🚀 Stage08: Started Injuries Impact Analysis ------------------>")

    if not os.path.exists(PREDICTIONS_FILE):
        print("No predictions found. Run Stage07 first.")
        logger.error("No predictions found. Run Stage07 first.")
        return

    predictions_df = pd.read_csv(PREDICTIONS_FILE)
    injuries_analyzer = InjuriesImpact()
    adjusted_predictions = []

    for _, row in predictions_df.iterrows():
        home_impact = injuries_analyzer.calculate_impact(row["home_team"], row["predicted_home_score"])
        away_impact = injuries_analyzer.calculate_impact(row["away_team"], row["predicted_away_score"])

        adjusted_predictions.append({
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "original_home_score": row["predicted_home_score"],
            "original_away_score": row["predicted_away_score"],
            "home_net_impact": home_impact["net_impact"],
            "away_net_impact": away_impact["net_impact"],
            "adjusted_home_score": home_impact["adjusted_score"],
            "adjusted_away_score": away_impact["adjusted_score"],
            "home_injured_players": len(home_impact["injured_players"]),
            "away_injured_players": len(away_impact["injured_players"]),
            "home_injury_details": home_impact["injured_players"],
            "away_injury_details": away_impact["injured_players"]
        })

        print(f"\nGame: {row['away_team']} @ {row['home_team']}")
        print(f"Original: {row['home_team']} {row['predicted_home_score']:.1f} - {row['away_team']} {row['predicted_away_score']:.1f}")
        print(f"Adjusted: {row['home_team']} {home_impact['adjusted_score']:.1f} - {row['away_team']} {away_impact['adjusted_score']:.1f}")
        
        if home_impact["injured_players"]:
            print(f"{row['home_team']} Injuries:")
            for player in home_impact["injured_players"]:
                print(f"- {player['name']} ({player['position']}): {player['ppg']:.1f} PPG, Status: {player['status']}")
        
        if away_impact["injured_players"]:
            print(f"{row['away_team']} Injuries:")
            for player in away_impact["injured_players"]:
                print(f"- {player['name']} ({player['position']}): {player['ppg']:.1f} PPG, Status: {player['status']}")

    adjusted_df = pd.DataFrame(adjusted_predictions)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    adjusted_df["home_injury_details"] = adjusted_df["home_injury_details"].apply(lambda x: str(x))
    adjusted_df["away_injury_details"] = adjusted_df["away_injury_details"].apply(lambda x: str(x))
    
    adjusted_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nAdjusted predictions saved to {OUTPUT_FILE}")

    print("<------------------ ✅ Injuries Impact Analysis Completed ------------------>")
    logger.info("<------------------ ✅ Injuries Impact Analysis Completed ------------------>")

if __name__ == "__main__":
    main()