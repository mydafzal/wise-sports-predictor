import pandas as pd
import pickle
import os
from typing import Dict, Optional
from box import ConfigBox
from WiseSportsAI_MLB.logging import logger

class BaseballRunPredictor:
    def __init__(self, artifacts_path: str = "Artifacts/MLB_Artifacts"):
        self.artifacts_path = os.path.join(artifacts_path, "MLBProcessed_Artifacts")
        self.model_artifacts_path = os.path.join(artifacts_path, "Model_Artifacts") 
        self._load_artifacts()

    def _load_artifacts(self) -> None:

        try:
            self.label_encoders = {}
            encoder_files = [
                'HomeTeam_encoder.pkl', 'AwayTeam_encoder.pkl',
                'Result_encoder.pkl', 'GB_encoder.pkl',
                'D_N_encoder.pkl', 'Attendance_encoder.pkl',
                'HomeTeamBatting_cWPA_encoder.pkl', 'HomeTeamPitching_cWPA_encoder.pkl',
                'AwayTeamBatting_cWPA_encoder.pkl', 'AwayTeamPitching_cWPA_encoder.pkl'
            ]
            
            for enc_file in encoder_files:
                col_name = enc_file.replace('_encoder.pkl', '')
                enc_path = os.path.join(self.artifacts_path, enc_file)
                with open(enc_path, "rb") as f:
                    self.label_encoders[col_name] = pickle.load(f)

            with open(os.path.join(self.artifacts_path, "processing_artifacts.pkl"), "rb") as f:
                processing_artifacts = pickle.load(f)
                self.original_home_teams = processing_artifacts['original_home_teams']
                self.original_away_teams = processing_artifacts['original_away_teams']

            with open("Artifacts/MLB_Artifacts/df_original.pkl", "rb") as f:
                self.df_original = pickle.load(f)
                
            with open("Artifacts/MLB_Artifacts/matchup_stats.pkl", "rb") as f:
                self.matchup_stats = pickle.load(f)

            with open(os.path.join(self.model_artifacts_path, "home_runs_model.pkl"), "rb") as f:
                self.home_model = pickle.load(f)
                
            with open(os.path.join(self.model_artifacts_path, "away_runs_model.pkl"), "rb") as f:
                self.away_model = pickle.load(f)
                
            with open(os.path.join(self.model_artifacts_path, "scaler.pkl"), "rb") as f:
                self.scaler = pickle.load(f)
                
            with open(os.path.join(self.model_artifacts_path, "feature_names.pkl"), "rb") as f:
                self.feature_names = pickle.load(f)

            logger.info("All artifacts loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Missing artifact file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading artifacts: {e}")
            raise

    def validate_inputs(self, home_team: str, away_team: str) -> bool:
        if home_team not in self.original_home_teams:
            raise ValueError(f"Home team '{home_team}' not found in training data")
        
        if away_team not in self.original_away_teams:
            raise ValueError(f"Away team '{away_team}' not found in training data")
        
        return True

    def get_matchup_features(self, home_team: str, away_team: str) -> Dict:

        if home_team in self.matchup_stats and away_team in self.matchup_stats[home_team]:
            stats = self.matchup_stats[home_team][away_team]
            return {
                'historical_home_runs': stats['home_avg_runs'],
                'historical_away_runs': stats['away_avg_runs'],
                'home_win_pct': stats['home_win_pct'],
                'matchup_games_played': stats['games_played']
            }
        else:
            return {
                'historical_home_runs': self.df_original['HomeTeamRuns'].mean(),
                'historical_away_runs': self.df_original['AwayTeamRuns'].mean(),
                'home_win_pct': 0.5,
                'matchup_games_played': 0
            }

    def prepare_features(self, home_team: str, away_team: str, game_date: str) -> Optional[pd.DataFrame]:

        try:
            self.validate_inputs(home_team, away_team)
            
            game_date = pd.to_datetime(game_date, format='%d-%m-%Y')
            
            matchup_id = f"{home_team}_vs_{away_team}"
            
            home_encoded = self.label_encoders['HomeTeam'].transform([home_team])[0]
            away_encoded = self.label_encoders['AwayTeam'].transform([away_team])[0]
            
            matchup_features = self.get_matchup_features(home_team, away_team)
            
            home_stats = self.df_original[self.df_original['HomeTeam'] == home_team].mean(numeric_only=True)
            away_stats = self.df_original[self.df_original['AwayTeam'] == away_team].mean(numeric_only=True)
            
            feature_row = pd.DataFrame(columns=self.feature_names, index=[0])
            feature_row = feature_row.fillna(0).infer_objects(copy=False)
            
            feature_row['HomeTeam'] = home_encoded
            feature_row['AwayTeam'] = away_encoded
            
            if 'MatchupID' in feature_row.columns:
                if matchup_id in self.label_encoders['MatchupID'].classes_:
                    feature_row['MatchupID'] = self.label_encoders['MatchupID'].transform([matchup_id])[0]
                else:
                    feature_row['MatchupID'] = 0
            
            feature_row['Day'] = game_date.day
            feature_row['Month'] = game_date.month
            feature_row['Year'] = game_date.year
            feature_row['DayOfWeek'] = game_date.dayofweek
            feature_row['IsWeekend'] = 1 if game_date.dayofweek >= 5 else 0
            
            for key, value in matchup_features.items():
                if key in feature_row.columns:
                    feature_row[key] = value
            
            for col in home_stats.index:
                if col in feature_row.columns:
                    feature_row[col] = home_stats[col]
                    
            for col in away_stats.index:
                if col in feature_row.columns and col not in ['HomeTeam', 'AwayTeam']:
                    feature_row[col] = away_stats[col]
            
            for col in self.label_encoders:
                if col in feature_row.columns and col not in ['HomeTeam', 'AwayTeam', 'MatchupID']:
                    if col in self.df_original.columns:
                        most_common = self.df_original[col].mode()[0]
                        encoded_val = self.label_encoders[col].transform([str(most_common)])[0]
                        feature_row[col] = encoded_val
            
            return self.scaler.transform(feature_row)
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None

    def predict_runs(self, home_team: str, away_team: str, game_date: str) -> ConfigBox:

        result = ConfigBox({
            'status': False,
            'home_team': home_team,
            'away_team': away_team,
            'game_date': game_date,
            'error': None
        })
        
        try:
            features = self.prepare_features(home_team, away_team, game_date)
            if features is None:
                raise ValueError("Could not prepare features for prediction")
            
            predicted_home_runs = self.home_model.predict(features)[0]
            predicted_away_runs = self.away_model.predict(features)[0]
            
            matchup_info = self.get_matchup_features(home_team, away_team)
            
            result.update({
                'status': True,
                'predicted_home_runs': round(predicted_home_runs, 2),  
                'predicted_away_runs': round(predicted_away_runs, 2),  
                'predicted_winner': home_team if predicted_home_runs > predicted_away_runs else away_team,
                'historical_matchup': ConfigBox({
                    'games_played': matchup_info['matchup_games_played'],
                    'home_win_pct': round(matchup_info['home_win_pct'] * 100, 2),
                    'avg_home_runs': round(matchup_info['historical_home_runs'], 2),  
                    'avg_away_runs': round(matchup_info['historical_away_runs'], 2)  
                })
            })
            
            logger.info(f"Prediction successful for {home_team} vs {away_team} on {game_date}")
            return result
            
        except Exception as e:
            error_msg = f"Prediction error: {str(e)}"
            logger.error(error_msg)
            result['error'] = error_msg
            return result