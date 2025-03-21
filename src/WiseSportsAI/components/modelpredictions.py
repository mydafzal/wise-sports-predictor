import pandas as pd
import joblib
from typing import Dict

class ModelPredictor:
    def __init__(self, model_home_path: str, model_away_path: str, label_encoder_home_path: str, label_encoder_away_path: str):
        """Initialize the ModelPredictor with paths to models and label encoders."""
        self.xgb_home = joblib.load(model_home_path)
        self.xgb_away = joblib.load(model_away_path)
        self.label_encoders = {
            'home_team_name': joblib.load(label_encoder_home_path),
            'away_team_name': joblib.load(label_encoder_away_path),
        }

    def calculate_team_averages(self, df: pd.DataFrame, home_team_name: str, away_team_name: str) -> Dict:
        """Calculate average statistics for home and away teams, including H2H metrics."""
        # Filter home team data
        home_team_data = df[df['home_team_name'] == home_team_name]
        # Filter away team data
        away_team_data = df[df['away_team_name'] == away_team_name]

        # Home team statistics
        home_stats = {
            'home_team_score': home_team_data['home_team_score'].mean(),
            'home_team_FG': home_team_data['home_team_FG'].mean(),
            'home_team_FGA': home_team_data['home_team_FGA'].mean(),
            'home_team_FG%': home_team_data['home_team_FG%'].mean(),
            'home_team_3P': home_team_data['home_team_3P'].mean(),
            'home_team_3PA': home_team_data['home_team_3PA'].mean(),
            'home_team_3P%': home_team_data['home_team_3P%'].mean(),
            'home_team_2P': home_team_data['home_team_2P'].mean(),
            'home_team_2PA': home_team_data['home_team_2PA'].mean(),
            'home_team_2P%': home_team_data['home_team_2P%'].mean(),
            'home_team_eFG%': home_team_data['home_team_eFG%'].mean(),
            'home_team_FT': home_team_data['home_team_FT'].mean(),
            'home_team_FTA': home_team_data['home_team_FTA'].mean(),
            'home_team_FT%': home_team_data['home_team_FT%'].mean(),
            'home_team_ORB': home_team_data['home_team_ORB'].mean(),
            'home_team_DRB': home_team_data['home_team_DRB'].mean(),
            'home_team_TRB': home_team_data['home_team_TRB'].mean(),
            'home_team_AST': home_team_data['home_team_AST'].mean(),
            'home_team_STL': home_team_data['home_team_STL'].mean(),
            'home_team_BLK': home_team_data['home_team_BLK'].mean(),
            'home_team_TOV': home_team_data['home_team_TOV'].mean(),
            'home_team_PF': home_team_data['home_team_PF'].mean(),
            'home_team_Wins': home_team_data['home_team_Wins'].mean(),
            'home_team_Losses': home_team_data['home_team_Losses'].mean(),
            'home_team_Win/Loss %': home_team_data['home_team_Win/Loss %'].mean(),
            'home_team_SRS': home_team_data['home_team_SRS'].mean(),
            'home_team_Pace': home_team_data['home_team_Pace'].mean(),
            'home_team_Pace_Rel': home_team_data['home_team_Pace_Rel'].mean(),
            'home_team_ORtg': home_team_data['home_team_ORtg'].mean(),
            'home_team_Rel_ORtg': home_team_data['home_team_Rel_ORtg'].mean(),
            'home_team_DRtg': home_team_data['home_team_DRtg'].mean(),
            'home_team_Rel_DRtg': home_team_data['home_team_Rel_DRtg'].mean()
        }

        # Away team statistics
        away_stats = {
            'away_team_score': away_team_data['away_team_score'].mean(),
            'away_team_FG': away_team_data['away_team_FG'].mean(),
            'away_team_FGA': away_team_data['away_team_FGA'].mean(),
            'away_team_FG%': away_team_data['away_team_FG%'].mean(),
            'away_team_3P': away_team_data['away_team_3P'].mean(),
            'away_team_3PA': away_team_data['away_team_3PA'].mean(),
            'away_team_3P%': away_team_data['away_team_3P%'].mean(),
            'away_team_2P': away_team_data['away_team_2P'].mean(),
            'away_team_2PA': away_team_data['away_team_2PA'].mean(),
            'away_team_2P%': away_team_data['away_team_2P%'].mean(),
            'away_team_eFG%': away_team_data['away_team_eFG%'].mean(),
            'away_team_FT': away_team_data['away_team_FT'].mean(),
            'away_team_FTA': away_team_data['away_team_FTA'].mean(),
            'away_team_FT%': away_team_data['away_team_FT%'].mean(),
            'away_team_ORB': away_team_data['away_team_ORB'].mean(),
            'away_team_DRB': away_team_data['away_team_DRB'].mean(),
            'away_team_TRB': away_team_data['away_team_TRB'].mean(),
            'away_team_AST': away_team_data['away_team_AST'].mean(),
            'away_team_STL': away_team_data['away_team_STL'].mean(),
            'away_team_BLK': away_team_data['away_team_BLK'].mean(),
            'away_team_TOV': away_team_data['away_team_TOV'].mean(),
            'away_team_PF': away_team_data['away_team_PF'].mean(),
            'away_team_Wins': away_team_data['away_team_Wins'].mean(),
            'away_team_Losses': away_team_data['away_team_Losses'].mean(),
            'away_team_Win/Loss %': away_team_data['away_team_Win/Loss %'].mean(),
            'away_team_SRS': away_team_data['away_team_SRS'].mean(),
            'away_team_Pace': away_team_data['away_team_Pace'].mean(),
            'away_team_Pace_Rel': away_team_data['away_team_Pace_Rel'].mean(),
            'away_team_ORtg': away_team_data['away_team_ORtg'].mean(),
            'away_team_Rel_ORtg': away_team_data['away_team_Rel_ORtg'].mean(),
            'away_team_DRtg': away_team_data['away_team_DRtg'].mean(),
            'away_team_Rel_DRtg': away_team_data['away_team_Rel_DRtg'].mean()
        }
        # print(home_stats)
        # print(away_stats)
        
        h2h_stats = self.calculate_h2h_stats(df, home_team_name, away_team_name)

        # print(h2h_stats)

        return {**home_stats, **away_stats, **h2h_stats}

    def calculate_h2h_stats(self, df: pd.DataFrame, home_team_name: str, away_team_name: str) -> Dict:
        """Calculate head-to-head statistics between two teams."""
        h2h_games = df[
            ((df['home_team_name'] == home_team_name) & (df['away_team_name'] == away_team_name)) |
            ((df['home_team_name'] == away_team_name) & (df['away_team_name'] == home_team_name))
        ]
        if h2h_games.empty:
            return {
                'h2h_games_played': 0,
                'h2h_home_wins': 0,
                'h2h_away_wins': 0,
                'h2h_avg_home_score': 0,
                'h2h_avg_away_score': 0,
                'h2h_avg_point_diff': 0
            }
        h2h_games_played = len(h2h_games)
        h2h_home_wins = len(h2h_games[(h2h_games['home_team_name'] == home_team_name) & (h2h_games['home_team_score'] > h2h_games['away_team_score'])])
        h2h_away_wins = len(h2h_games[(h2h_games['away_team_name'] == home_team_name) & (h2h_games['away_team_score'] > h2h_games['home_team_score'])])
        h2h_avg_home_score = h2h_games[h2h_games['home_team_name'] == home_team_name]['home_team_score'].mean()
        h2h_avg_away_score = h2h_games[h2h_games['away_team_name'] == away_team_name]['away_team_score'].mean()
        h2h_avg_point_diff = h2h_avg_home_score - h2h_avg_away_score
        return {
            'h2h_games_played': h2h_games_played,
            'h2h_home_wins': h2h_home_wins,
            'h2h_away_wins': h2h_away_wins,
            'h2h_avg_home_score': h2h_avg_home_score,
            'h2h_avg_away_score': h2h_avg_away_score,
            'h2h_avg_point_diff': h2h_avg_point_diff
        }

    def preprocess_input(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess input data for model inference."""
        processed_data = data.copy()
        processed_data['Date'] = pd.to_datetime(processed_data['Date'])
        processed_data['year'] = processed_data['Date'].dt.year
        processed_data['month'] = processed_data['Date'].dt.month
        processed_data['day'] = processed_data['Date'].dt.day
        processed_data['day_of_week'] = processed_data['Date'].dt.dayofweek
        processed_data = processed_data.drop(columns=['Date'])
        for col in ['home_team_name', 'away_team_name']:
            if col in processed_data.columns:
                valid_teams = self.label_encoders[col].classes_
                processed_data[col] = processed_data[col].apply(lambda x: x if x in valid_teams else 'Unknown')
                processed_data[col] = self.label_encoders[col].transform(processed_data[col].astype(str))
        return processed_data

    def predict_scores(self, home_team_name: str, away_team_name: str, match_date: str, historical_data_df: pd.DataFrame) -> tuple:
        """Predict scores using team averages and H2H statistics."""
        team_stats = self.calculate_team_averages(historical_data_df, home_team_name, away_team_name)
        input_data = pd.DataFrame({
            'Date': [match_date],
            'home_team_name': [home_team_name],
            'away_team_name': [away_team_name],
            **{k: [v] for k, v in team_stats.items()}
        })
        processed_data = self.preprocess_input(input_data)
        # Predict home score
        home_model_features = self.xgb_home.feature_names_in_
        missing_home_features = set(home_model_features) - set(processed_data.columns)
        for feature in missing_home_features:
            processed_data[feature] = 0
        X_home = processed_data[home_model_features]
        home_score = self.xgb_home.predict(X_home)[0]
        # Predict away score
        processed_data['home_team_score'] = home_score
        away_model_features = self.xgb_away.feature_names_in_
        missing_away_features = set(away_model_features) - set(processed_data.columns)
        for feature in missing_away_features:
            processed_data[feature] = 0
        X_away = processed_data[away_model_features]
        away_score = self.xgb_away.predict(X_away)[0]
        return home_score, away_score