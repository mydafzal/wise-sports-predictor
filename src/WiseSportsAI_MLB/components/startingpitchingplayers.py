import pandas as pd
from sklearn.preprocessing import StandardScaler
import requests
import numpy as np
import unidecode
from datetime import datetime
from pathlib import Path

class PitcherBasedScorer:
    def __init__(self, pitcher_stats_df):
        self.feature_config = {
            'IP': 0.50, 'K%': 0.35, 'BB%': -0.30, 'HR%': -0.25,
            'BA': -0.20, 'OBP': -0.20, 'SLG': -0.25, 'EV': -0.15,
            'HardH%': -0.18, 'LD%': -0.10, 'GB%': 0.10, 'FB%': -0.08,
            'WPA': 0.30, 'RE24': 0.25
        }
        
        if 'Player' not in pitcher_stats_df.columns:
            raise KeyError("DataFrame must contain 'Player' column")
            
        self.df = self._preprocess_data(pitcher_stats_df.copy())
        self.scaler = StandardScaler()
        
        self._prepare_scaler()
        self.ADJUSTMENT_FACTOR = 0.30
        self.abbreviation_conversion = { 
            'TB': 'TBR',
            'KC': 'KCR',
            'ATH': 'OAK',
            'WAS': 'WSN',
            'SD': 'SDP',
            'SF': 'SFG',
            'CWS': 'CHW' 
        }
        self.team_mapping = self._create_team_mapping()

    def _preprocess_data(self, df):
        df['Player'] = df['Player'].apply(self._normalize_name)
        
        for col in self.feature_config.keys():
            if col in df.columns:
                if col in ['K%', 'BB%', 'HR%', 'HardH%', 'LD%', 'GB%', 'FB%']:
                    df[col] = df[col].replace('%', '', regex=True).astype(float) / 100
                else:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        agg_rules = {k: 'mean' for k in self.feature_config.keys()}
        return df.groupby('Player', as_index=False).agg(agg_rules)

    def _normalize_name(self, name):
        return unidecode.unidecode(str(name)).lower().strip().replace('.', '').replace(' jr', '')

    def _create_team_mapping(self):
        return {
            'Arizona Diamondbacks': 'ARI',
            'Atlanta Braves': 'ATL',
            'Baltimore Orioles': 'BAL',
            'Boston Red Sox': 'BOS',
            'Chicago Cubs': 'CHC',
            'Chicago White Sox': 'CHW',  
            'Cincinnati Reds': 'CIN',
            'Cleveland Guardians': 'CLE',
            'Colorado Rockies': 'COL',
            'Detroit Tigers': 'DET',
            'Houston Astros': 'HOU',
            'Kansas City Royals': 'KCR',  
            'Los Angeles Angels': 'LAA',
            'Los Angeles Dodgers': 'LAD',
            'Miami Marlins': 'MIA',
            'Milwaukee Brewers': 'MIL',
            'Minnesota Twins': 'MIN',
            'New York Mets': 'NYM',
            'New York Yankees': 'NYY',
            'Oakland Athletics': 'OAK',
            'Philadelphia Phillies': 'PHI',
            'Pittsburgh Pirates': 'PIT',
            'San Diego Padres': 'SDP',  
            'San Francisco Giants': 'SFG',  
            'Seattle Mariners': 'SEA',
            'St. Louis Cardinals': 'STL',
            'Tampa Bay Rays': 'TBR',
            'Texas Rangers': 'TEX',
            'Toronto Blue Jays': 'TOR',
            'Washington Nationals': 'WSN'  
        }

    def _prepare_scaler(self):
        required_cols = list(self.feature_config.keys())
        clean_df = self.df[required_cols].fillna(self.df.median(numeric_only=True))
        self.scaler.fit(clean_df)

    def calculate_pitcher_impact(self, pitcher_name):
        if pitcher_name == "TBD":
            return 0.0
            
        norm_name = self._normalize_name(pitcher_name)
        pitcher_data = self.df[self.df['Player'] == norm_name]
        
        if pitcher_data.empty:
            print(f"⚠️ Pitcher {pitcher_name} not found. Using league average.")
            return 0.0
            
        try:
            features = list(self.feature_config.keys())
            scaled = self.scaler.transform(pitcher_data[features])
            impact = sum(scaled[0][i] * weight 
                       for i, (_, weight) in enumerate(self.feature_config.items()))
            return impact * 1.4 if impact > 0 else impact * 0.6
        except Exception as e:
            print(f"Error calculating impact for {pitcher_name}: {str(e)}")
            return 0.0

    def adjust_game_scores(self, home_team_abbr, away_team_abbr, home_pred, away_pred, game_date):
        try:
            home_abbr = self.abbreviation_conversion.get(home_team_abbr, home_team_abbr)
            away_abbr = self.abbreviation_conversion.get(away_team_abbr, away_team_abbr)
            
            reverse_mapping = {v: k for k, v in self.team_mapping.items()}
            home_team = reverse_mapping.get(home_abbr)
            away_team = reverse_mapping.get(away_abbr)
            
            if not home_team or not away_team:
                raise ValueError(f"Invalid team abbreviation: {home_abbr} vs {away_abbr}")
            
            home_pitcher, away_pitcher = self._get_pitchers(home_team, away_team, game_date)
            home_impact = self.calculate_pitcher_impact(home_pitcher)
            away_impact = self.calculate_pitcher_impact(away_pitcher)
            
            home_adj = away_impact * self.ADJUSTMENT_FACTOR
            away_adj = home_impact * self.ADJUSTMENT_FACTOR
            
            print(f"\n{'='*40}")
            print(f"Game Date: {game_date}")
            print(f"Matchup: {home_team} vs {away_team}")
            print(f"\nProbable Pitchers:")
            print(f"  {home_team}: {home_pitcher} (Impact Score: {home_impact:.2f})")
            print(f"  {away_team}: {away_pitcher} (Impact Score: {away_impact:.2f})")
            print(f"\nOriginal Predictions:")
            print(f"  {home_team}: {home_pred:.2f}")
            print(f"  {away_team}: {away_pred:.2f}")
            print(f"\nAdjustment Factors:")
            print(f"  Home Adjustment: -{home_adj:.2f} (Based on {away_pitcher}'s impact)")
            print(f"  Away Adjustment: -{away_adj:.2f} (Based on {home_pitcher}'s impact)")
            print(f"\nFinal Adjusted Scores:")
            print(f"  {home_team}: {max(0, home_pred - home_adj):.2f}")
            print(f"  {away_team}: {max(0, away_pred - away_adj):.2f}")
            print(f"{'='*40}")

            return (
                round(max(0, home_pred - home_adj), 2),
                round(max(0, away_pred - away_adj), 2)
            )
        except Exception as e:
            print(f"⚠️ Adjustment failed: {str(e)}")
            return home_pred, away_pred

    def _get_pitchers(self, home_team, away_team, date):
        try:
            url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&hydrate=probablePitcher&startDate={date}&endDate={date}"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            for date_info in data.get("dates", []):
                for game in date_info.get("games", []):
                    game_home = game["teams"]["home"]["team"]["name"]
                    game_away = game["teams"]["away"]["team"]["name"]
                    
                    if game_home == home_team and game_away == away_team:
                        return (
                            game["teams"]["home"].get("probablePitcher", {}).get("fullName", "TBD"),
                            game["teams"]["away"].get("probablePitcher", {}).get("fullName", "TBD")
                        )
            raise ValueError(f"Game {home_team} vs {away_team} not found on {date}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"API Error: {str(e)}")


class StartingPitcherDataLoader:
    def __init__(self):
        self.data_dir = Path("Artifacts/MLB_Artifacts")
        self.combined_data = self._load_and_combine_data()
    
    def _load_and_combine_data(self):
        numeric_cols = [
            "Rk", "Age", "IP", "BA", "OBP", "SLG", "OPS", "BAbip",
            "HR%", "K%", "BB%", "EV", "HardH%", "LD%", "GB%", "FB%", 
            "GB/FB", "WPA", "cWPA", "RE24"
        ]
        
        dfs = []
        for year in [2023, 2024, 2025]:
            df = pd.read_csv(self.data_dir / f"PSP_{year}.csv")
            df = df.reset_index()
            df.columns = [
                "Rk", "Player", "Age", "Team", "Lg", "IP", "BA", "OBP", 
                "SLG", "OPS", "BAbip", "HR%", "K%", "BB%", "EV", "HardH%", 
                "LD%", "GB%", "FB%", "GB/FB", "WPA", "cWPA", "RE24", "Awards"
            ]
            
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            dfs.append(df)
        
        return pd.concat(dfs, ignore_index=True).fillna(0)