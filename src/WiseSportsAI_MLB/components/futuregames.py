import requests
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional
from box import ConfigBox
from pytz import timezone
import pandas as pd
from WiseSportsAI_MLB.logging import logger
from WiseSportsAI_MLB.components.modelprediction import BaseballRunPredictor

class MLBFutureGamesPredictor:
    def __init__(self, artifacts_path: str = "Artifacts/MLB_Artifacts"):
        self.artifacts_path = artifacts_path
        self.predictor = BaseballRunPredictor(artifacts_path)
        self.et = timezone('America/New_York')
        self.team_id_map = {}
        self.team_abbr_map = {}

    def fetch_team_data(self) -> bool:
        """Fetch MLB team data and map to abbreviations"""
        url = "https://statsapi.mlb.com/api/v1/teams?season=2025&sportId=1"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch team data: Status {response.status_code}")
                return False

            data = response.json()
            self.team_abbr_map = {}
            self.team_id_map = {}

            for team in data['teams']:
                if 'abbreviation' in team and team['abbreviation']:
                    self.team_abbr_map[team['name']] = team['abbreviation']
                    self.team_id_map[team['id']] = team['abbreviation']

            logger.info(f"Loaded data for {len(self.team_abbr_map)} MLB teams")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching team data: {e}")
            return False

    def get_todays_games(self) -> List[Dict]:
        """Fetch today's scheduled games from MLB API in Eastern Time"""
        today = datetime.now(self.et).strftime("%Y-%m-%d")
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch games: Status {response.status_code}")
                return []

            data = response.json()
            return data.get('dates', [{}])[0].get('games', [])
            
        except Exception as e:
            logger.error(f"Error fetching games: {e}")
            return []

    def predict_todays_games(self) -> ConfigBox:
        """Predict all today's games and return results"""
        result = ConfigBox({
            'status': False,
            'predicted_games': [],
            'error': None,
            'output_file': None
        })

        try:
            if not self.fetch_team_data():
                raise ValueError("Could not fetch team data")

            games = self.get_todays_games()
            if not games:
                logger.info("No games scheduled for today")
                return result

            predictions = []
            for game in games:
                try:
                    game_prediction = self._process_game(game)
                    if game_prediction:
                        predictions.append(game_prediction)
                        time.sleep(0.2)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Skipping game due to error: {str(e)}")

            if predictions:
                output_file = self._save_predictions(predictions)
                result.update({
                    'status': True,
                    'predicted_games': predictions,
                    'output_file': output_file
                })

            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            result['error'] = str(e)
            return result

    def _process_game(self, game: Dict) -> Optional[Dict]:
        """Process individual game and return prediction"""
        try:
            home_team = game['teams']['home']['team']
            away_team = game['teams']['away']['team']
            
            # Get team abbreviations
            home_abbr = self.team_id_map.get(home_team['id'], home_team.get('abbreviation', home_team['name'][:3]))
            away_abbr = self.team_id_map.get(away_team['id'], away_team.get('abbreviation', away_team['name'][:3]))

            # Validate teams exist in model
            if home_abbr not in self.predictor.original_home_teams:
                raise ValueError(f"Home team {home_abbr} not in training data")
            if away_abbr not in self.predictor.original_away_teams:
                raise ValueError(f"Away team {away_abbr} not in training data")

            # Make prediction with current ET date
            game_date = datetime.now(self.et).strftime("%d-%m-%Y")
            prediction = self.predictor.predict_runs(home_abbr, away_abbr, game_date)
            
            if not prediction.status:
                raise ValueError(prediction.error)

            # Convert game time to Eastern Time
            game_time = datetime.strptime(game['gameDate'], "%Y-%m-%dT%H:%M:%SZ")
            game_time = game_time.astimezone(self.et)

            return {
                'game_time': game_time.strftime("%I:%M %p ET"),
                'home_team': home_team['name'],
                'home_abbr': home_abbr,
                'away_team': away_team['name'],
                'away_abbr': away_abbr,
                'prediction': prediction.to_dict()
            }
            
        except ValueError as e:
            logger.warning(str(e))
            return None
        except Exception as e:
            logger.error(f"Game processing error: {e}")
            return None

    def _save_predictions(self, predictions: List[Dict]) -> str:
        """Save predictions to JSON file with US date format"""
        today_str = datetime.now(self.et).strftime("%Y-%m-%d")
        output_dir = "Artifacts/MLB_Artifacts/Future_Predictions"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"predictions_{today_str}.json")
        
        with open(output_path, 'w') as f:
            json.dump(predictions, f, indent=4, default=str)
            
        logger.info(f"Saved {len(predictions)} predictions to {output_path}")
        return output_path