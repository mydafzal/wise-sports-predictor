import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from box import ConfigBox
from datetime import datetime
from typing import List, Dict
from WiseSportsAI_MLB.logging import logger

class StartingPitchingAdjuster:
    def __init__(self, pitching_data_path: str):
        self.pitching_data = self._prepare_data(pitching_data_path)
        self.feature_weights = np.array([1.00, 0.80, 0.50, 0.30, 0.30, 0.30, 0.15])
        self._initialize_mappings()
        self._normalize_features()

    def _prepare_data(self, path: str) -> pd.DataFrame:
        """Load and preprocess pitching data"""
        try:
            df = pd.read_csv(path)
            for col in df.columns:
                if df[col].astype(str).str.contains('%').any():
                    df[col] = df[col].str.replace('%', '', regex=False).astype(float) / 100
            df['IP_per_GS'] = df['IP/GS']
            df['Pitch_Efficiency'] = df['IP/GS'] / df['Pit/GS']
            return df.set_index('Tm').dropna(subset=['RS/GS'])
        except Exception as e:
            logger.error(f"Failed to load pitching data: {e}")
            raise

    def _initialize_mappings(self):
        """Map team abbreviations to full names"""
        self.team_map = {
            'ARI': 'Arizona Diamondbacks',
            'ATL': 'Atlanta Braves',
            'BAL': 'Baltimore Orioles',
            'BOS': 'Boston Red Sox',
            'CHC': 'Chicago Cubs',
            'CHW': 'Chicago White Sox',
            'CIN': 'Cincinnati Reds',
            'CLE': 'Cleveland Guardians',
            'COL': 'Colorado Rockies',
            'DET': 'Detroit Tigers',
            'HOU': 'Houston Astros',
            'KCR': 'Kansas City Royals',
            'LAA': 'Los Angeles Angels',
            'LAD': 'Los Angeles Dodgers',
            'MIA': 'Miami Marlins',
            'MIL': 'Milwaukee Brewers',
            'MIN': 'Minnesota Twins',
            'NYM': 'New York Mets',
            'NYY': 'New York Yankees',
            'OAK': 'Oakland Athletics',
            'PHI': 'Philadelphia Phillies',
            'PIT': 'Pittsburgh Pirates',
            'SD': 'San Diego Padres',
            'SF': 'San Francisco Giants',
            'SEA': 'Seattle Mariners',
            'STL': 'St. Louis Cardinals',
            'TB': 'Tampa Bay Rays',
            'TEX': 'Texas Rangers',
            'TOR': 'Toronto Blue Jays',
            'WSH': 'Washington Nationals',
            'WSN': 'Washington Nationals',
            'SFG': 'San Francisco Giants',
            'TBR': 'Tampa Bay Rays',
            'SDP': 'San Diego Padres',
            'OAK': 'Oakland Athletics',
        }

    def _normalize_features(self):
        """Normalize and prepare features for calculations"""
        features = ['GmScA', 'QS%', 'IP_per_GS', 'Pitch_Efficiency', 'SHO', 'BQS', 'RS/GS']
        scaler = MinMaxScaler()
        self.normalized = pd.DataFrame(
            scaler.fit_transform(self.pitching_data[features]),
            columns=features,
            index=self.pitching_data.index
        )
        self.normalized[['RS/GS', 'BQS']] = 1 - self.normalized[['RS/GS', 'BQS']]

    def _get_team_impact(self, team_abbr: str) -> pd.Series:
        """Get normalized pitching stats for a team"""
        full_name = self.team_map.get(team_abbr)
        if not full_name:
            logger.warning(f"No mapping found for {team_abbr}")
            return pd.Series()
        try:
            return self.normalized.loc[full_name]
        except KeyError:
            logger.warning(f"No pitching data for {full_name}")
            return pd.Series()

    def calculate_adjustments(self, home_abbr: str, away_abbr: str) -> ConfigBox:

        try:
            home_stats = self._get_team_impact(home_abbr)
            away_stats = self._get_team_impact(away_abbr)

            if home_stats.empty or away_stats.empty:
                return ConfigBox({'home_adj': 0.0, 'away_adj': 0.0})

            # Convert to numpy arrays and ensure float types
            home_values = home_stats.values.astype(float)
            away_values = away_stats.values.astype(float)
            
            home_advantage = np.dot(home_values - away_values, self.feature_weights)
            away_advantage = np.dot(away_values - home_values, self.feature_weights)

            def scale_impact(x):
                # Cap values to prevent overflow
                x = np.clip(x, -5, 5)
                return float(1.5 * (1 / (1 + np.exp(-x)) - 0.5))

            return ConfigBox({
                'home_adj': scale_impact(home_advantage),
                'away_adj': scale_impact(away_advantage)
            })
        except Exception as e:
            logger.error(f"Adjustment calculation failed: {str(e)}")
            return ConfigBox({'home_adj': 0.0, 'away_adj': 0.0})


    def adjust_predictions(self, predictions: List[Dict]) -> List[Dict]:
        """Adjust a list of game predictions"""
        adjusted_games = []
        for game in predictions:
            try:
                original_pred = game['prediction']
                adj = self.calculate_adjustments(game['home_abbr'], game['away_abbr'])
                
                # Calculate adjusted scores
                original_home = float(original_pred['predicted_home_runs'])
                original_away = float(original_pred['predicted_away_runs'])
                
                adjusted_home = max(original_home + adj.home_adj, 0.0)
                adjusted_away = max(original_away + adj.away_adj, 0.0)
                adjusted_winner = game['home_abbr'] if adjusted_home > adjusted_away else game['away_abbr']

                # Create updated prediction
                updated_pred = {
                    **original_pred,
                    'pitching_adjustment': {
                        'home_adjustment': round(float(adj.home_adj), 2),
                        'away_adjustment': round(float(adj.away_adj), 2),
                        'adjusted_total': round(adjusted_home + adjusted_away, 2),
                        'spread': round(adjusted_home - adjusted_away, 2),
                        'adjusted_scores': {
                            'adjusted_home_runs': round(adjusted_home, 2),
                            'adjusted_away_runs': round(adjusted_away, 2),
                            'adjusted_winner': adjusted_winner
                        }
                    }
                }

                # Preserve original predictions while adding adjustments
                adjusted_game = {
                    **game,
                    'prediction': updated_pred,
                    'adjustment_timestamp': datetime.now().isoformat()
                }
                adjusted_games.append(adjusted_game)
                
            except Exception as e:
                logger.error(f"Failed to adjust {game['home_abbr']} vs {game['away_abbr']}: {str(e)}")
                adjusted_games.append({
                    **game,
                    'prediction': {
                        **game['prediction'],
                        'error': f"Adjustment failed: {str(e)}"
                    }
                })
        
        return adjusted_games