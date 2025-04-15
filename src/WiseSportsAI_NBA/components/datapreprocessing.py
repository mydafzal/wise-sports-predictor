import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder

class DataPreprocessing:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.label_encoders = {}
    
    def load_data(self):
        self.df = pd.read_csv(self.file_path)
    
    def clean_data(self):
        self.df.drop(columns=["home_team_Season", "home_team_League", "away_team_Season", "away_team_League"], inplace=True)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df['year'] = self.df['Date'].dt.year
        self.df['month'] = self.df['Date'].dt.month
        self.df['day'] = self.df['Date'].dt.day
        self.df['day_of_week'] = self.df['Date'].dt.dayofweek
        self.df.drop(columns=['result', 'Date'], inplace=True)
    
    def encode_categorical(self):
        categorical_columns = ['home_team_name', 'away_team_name']
        
        for col in categorical_columns:
            le = LabelEncoder()
            self.df[col] = le.fit_transform(self.df[col].astype(str))
            self.label_encoders[col] = le
            joblib.dump(le, f"Artifacts/LabelEncoder{col}.pkl")
    
    def convert_numeric(self):
        numeric_columns = self.df.select_dtypes(include=['float64', 'int64']).columns
        self.df[numeric_columns] = self.df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    def calculate_h2h_stats(self, home_team, away_team):
        h2h_games = self.df[((self.df['home_team_name'] == home_team) & (self.df['away_team_name'] == away_team)) |
                             ((self.df['home_team_name'] == away_team) & (self.df['away_team_name'] == home_team))]
        
        if h2h_games.empty:
            return {
                'h2h_games_played': 0, 'h2h_home_wins': 0, 'h2h_away_wins': 0,
                'h2h_avg_home_score': 0, 'h2h_avg_away_score': 0, 'h2h_avg_point_diff': 0
            }
        
        return {
            'h2h_games_played': len(h2h_games),
            'h2h_home_wins': len(h2h_games[(h2h_games['home_team_name'] == home_team) & (h2h_games['home_team_score'] > h2h_games['away_team_score'])]),
            'h2h_away_wins': len(h2h_games[(h2h_games['away_team_name'] == home_team) & (h2h_games['away_team_score'] > h2h_games['home_team_score'])]),
            'h2h_avg_home_score': h2h_games[h2h_games['home_team_name'] == home_team]['home_team_score'].mean(),
            'h2h_avg_away_score': h2h_games[h2h_games['away_team_name'] == away_team]['away_team_score'].mean(),
            'h2h_avg_point_diff': h2h_games[h2h_games['home_team_name'] == home_team]['home_team_score'].mean() - h2h_games[h2h_games['away_team_name'] == away_team]['away_team_score'].mean()
        }
    
    def add_h2h_features(self):
        h2h_features = [self.calculate_h2h_stats(row['home_team_name'], row['away_team_name']) for _, row in self.df.iterrows()]
        self.df = pd.concat([self.df, pd.DataFrame(h2h_features)], axis=1)
    
    def save_processed_data(self, output_path):
        self.df.to_csv(output_path, index=False)
    
    def run_pipeline(self, output_path):
        self.load_data()
        self.clean_data()
        self.encode_categorical()
        self.convert_numeric()
        self.add_h2h_features()
        self.save_processed_data(output_path)
        print("Data Preprocessing Complete!")
