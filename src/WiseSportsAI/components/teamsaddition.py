import pandas as pd
import os

class TeamsDataAddition:
    def __init__(self, team_stats_path, matches_data_path, output_path):
        self.team_stats_path = team_stats_path
        self.matches_data_path = matches_data_path
        self.output_path = output_path
    
    def load_data(self):
        self.df1 = pd.read_csv(self.team_stats_path)
        self.df2 = pd.read_csv(self.matches_data_path)
    
    def preprocess_team_stats(self):
        team_mapping = {
            "ATL": "Atlanta Hawks", "BOS": "Boston Celtics", "CHI": "Chicago Bulls", "CLE": "Cleveland Cavaliers",
            "DAL": "Dallas Mavericks", "DEN": "Denver Nuggets", "DET": "Detroit Pistons", "GSW": "Golden State Warriors",
            "HOU": "Houston Rockets", "IND": "Indiana Pacers", "LAC": "Los Angeles Clippers", "LAL": "Los Angeles Lakers",
            "MEM": "Memphis Grizzlies", "MIA": "Miami Heat", "MIL": "Milwaukee Bucks", "MIN": "Minnesota Timberwolves",
            "NOP": "New Orleans Pelicans", "NYK": "New York Knicks", "OKC": "Oklahoma City Thunder", "ORL": "Orlando Magic",
            "PHI": "Philadelphia 76ers", "PHO": "Phoenix Suns", "POR": "Portland Trail Blazers", "SAC": "Sacramento Kings",
            "SAS": "San Antonio Spurs", "TOR": "Toronto Raptors", "UTA": "Utah Jazz", "WAS": "Washington Wizards",
            "BRK": "Brooklyn Nets", "CHO": "Charlotte Hornets"
        }

        # Drop 'Wins' column
        if 'Wins' in self.df1.columns:
            self.df1.drop(columns=['Wins'], inplace=True)

        # Rename columns safely
        rename_map_1 = {
            'Losses': 'Wins',
            'Win/Loss %': 'Losses',
            'Rank': 'Win/Loss %',
            'SRS': 'Rank',
            'DUMMY1': 'SRS'
        }
        self.df1.rename(columns=rename_map_1, inplace=True)

        # Drop additional columns if they exist
        drop_columns = ['Rank', 'Pace']
        self.df1.drop(columns=[col for col in drop_columns if col in self.df1.columns], inplace=True)

        # Rename next set of columns safely
        rename_map_2 = {
            'Pace Rel': 'Pace',
            'Off Rtg': 'Pace_Rel',
            'Off Rtg Rel': 'ORtg',
            'Def Rtg': 'Rel_ORtg',
            'Def Rtg Rel': 'DRtg',
            'DUMMY2': 'Rel_DRtg'
        }
        self.df1.rename(columns=rename_map_2, inplace=True)

        # Drop last 4 columns only if we know their names
        num_cols_to_drop = 4
        if self.df1.shape[1] > num_cols_to_drop:
            self.df1 = self.df1.iloc[:, :-num_cols_to_drop]

        # Replace team names with abbreviations
        team_mapping_reverse = {v: k for k, v in team_mapping.items()}
        if "Team Name" in self.df1.columns:
            self.df1["Team Name"] = self.df1["Team Name"].replace(team_mapping_reverse)
            self.df1.rename(columns={'Team Name': 'team_name'}, inplace=True)

    
    def merge_dataframes(self):
        teams_stats = self.df1.copy()
        result_df = self.df2.copy()
        
        home_stats = teams_stats.copy()
        home_stats.columns = ['home_team_' + col if col != 'team_name' else 'home_team_name' for col in home_stats.columns]
        result_df = pd.merge(result_df, home_stats, on='home_team_name', how='left')
        
        away_stats = teams_stats.copy()
        away_stats.columns = ['away_team_' + col if col != 'team_name' else 'away_team_name' for col in away_stats.columns]
        result_df = pd.merge(result_df, away_stats, on='away_team_name', how='left')
        
        return result_df
    
    def save_final_data(self, final_df):
        final_df.to_csv(self.output_path, index=False)
    
    def run(self):
        self.load_data()
        self.preprocess_team_stats()
        final_df = self.merge_dataframes()
        self.save_final_data(final_df)
        print(f"Final dataset saved at {self.output_path}")