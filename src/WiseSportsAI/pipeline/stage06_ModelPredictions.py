import pandas as pd
from WiseSportsAI.components.modelpredictions import ModelPredictor

def main():
    model_home_path = "Artifacts/TrainedModels/xgb_home_score_model.pkl"
    model_away_path = "Artifacts/TrainedModels/xgb_away_score_model.pkl"
    label_encoder_home_path = "Artifacts/LabelEncoderhome_team_name.pkl"
    label_encoder_away_path = "Artifacts/LabelEncoderaway_team_name.pkl"

    print("<------------------ 🚀 Stage06: Started Model Predictions ------------------>")

    predictor = ModelPredictor(model_home_path, model_away_path, label_encoder_home_path, label_encoder_away_path)

    historical_data = pd.read_csv("Artifacts/DataScraping/MergedDataSet.csv")

    home_team = "MEM"
    away_team = "LAL"
    match_date = "2025-03-17"

    predicted_home_score, predicted_away_score = predictor.predict_scores(home_team, away_team, match_date, historical_data)

    print(f"Predicted score for {home_team} vs {away_team} on {match_date}:")
    print(f"{home_team} (Home): {predicted_home_score:.0f}")
    print(f"{away_team} (Away): {predicted_away_score:.0f}")

    print("<------------------ ✅ Model Predictions Completed ------------------>\n\n")

if __name__ == "__main__":
    main()