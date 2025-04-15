import pandas as pd
import os
from pathlib import Path

class DataPreparation:
    def __init__(self, data_directory):
        self.data_directory = Path(data_directory)
        self.team_mapping = {
            "Dallas_Mavericks.csv": "DAL",
            "Atlanta_Hawks.csv": "ATL",
            "Boston_Celtics.csv": "BOS",
            "Chicago_Bulls.csv": "CHI",
            "Cleveland_Cavaliers.csv": "CLE",
            "Denver_Nuggets.csv": "DEN",
            "Detroit_Pistons.csv": "DET",
            "Golden_State_Warriors.csv": "GSW",
            "Houston_Rockets.csv": "HOU",
            "Indiana_Pacers.csv": "IND",
            "Los_Angeles_Clippers.csv": "LAC",
            "Los_Angeles_Lakers.csv": "LAL",
            "Memphis_Grizzlies.csv": "MEM",
            "Miami_Heat.csv": "MIA",
            "Milwaukee_Bucks.csv": "MIL",
            "Minnesota_Timberwolves.csv": "MIN",
            "New_Orleans_Pelicans.csv": "NOP",
            "New_York_Knicks.csv": "NYK",
            "Oklahoma_City_Thunder.csv": "OKC",
            "Orlando_Magic.csv": "ORL",
            "Philadelphia_76ers.csv": "PHI",
            "Phoenix_Suns.csv": "PHO",
            "Portland_Trail_Blazers.csv": "POR",
            "Sacramento_Kings.csv": "SAC",
            "San_Antonio_Spurs.csv": "SAS",
            "Toronto_Raptors.csv": "TOR",
            "Utah_Jazz.csv": "UTA",
            "Washington_Wizards.csv": "WAS",
            "Brooklyn_Nets.csv": "BRK",
            "Charlotte_Hornets.csv": "CHO"
        }

        self.columns = [
            'Date', 'Opp', 'Rslt', 'Tm', 'Opp.1', 'FG', 'FGA', 'FG%', '3P', '3PA',
            '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB',
            'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'FG.1', 'FGA.1', 'FG%.1',
            '3P.1', '3PA.1', '3P%.1', '2P.1', '2PA.1', '2P%.1', 'eFG%.1', 'FT.1',
            'FTA.1', 'FT%.1', 'ORB.1', 'DRB.1', 'TRB.1', 'AST.1', 'STL.1', 'BLK.1',
            'TOV.1', 'PF.1'
        ]
        
        self.rename_dict = {
            "Tm": "home_team_score",
            "Opp.1": "away_team_score",
            "Rslt": "result",
            "Opp": "away_team_name"
        }
        
        for col in self.columns:
            if col.endswith('.1'):
                self.rename_dict[col] = f"away_team_{col[:-2]}"
            elif col not in self.rename_dict and col not in ["Date", "Opp", "result"]:
                self.rename_dict[col] = f"home_team_{col}"
    
    def preprocess_data(self, file_path, home_team_name):
        try:
            df = pd.read_csv(file_path, skiprows=1)
            df.drop(columns=["Rk", "Gtm", "Unnamed: 3", "OT"], errors='ignore', inplace=True)
            
            for col in self.columns:
                if col not in df.columns:
                    df[col] = pd.NA
            
            df = df[self.columns]
            df.rename(columns=self.rename_dict, inplace=True)
            df.insert(1, "home_team_name", home_team_name)
            df.drop(df.index[-1], inplace=True)
            
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
            
            return df
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return None
    
    def run(self):
        all_teams_data = []
        
        for file, team_name in self.team_mapping.items():
            file_path = self.data_directory / file
            
            if not file_path.exists():
                print(f"⚠️ Warning: {file} not found. Skipping.")
                continue
            
            print(f"✅ Processing: {file} for team {team_name}")
            processed_df = self.preprocess_data(file_path, team_name)
            
            if processed_df is not None:
                all_teams_data.append(processed_df)
        
        if all_teams_data:
            final_df = pd.concat(all_teams_data, ignore_index=True)
            final_columns = ['Date', 'home_team_name'] + [col for col in self.rename_dict.values()]
            final_df = final_df[final_columns]
            final_df = final_df.rename(columns={"away_team_Opp": "away_team_score"})
            final_df = final_df.sort_values(by='Date', ascending=False)
            
            output_path = "Artifacts/DataScraping/AllTeamsMatches2025.csv"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            final_df.to_csv(output_path, index=False)
            
            print("✅ All Team Data Processed Successfully.")
            print(f"Final dataset shape: {final_df.shape}")
        else:
            print("❌ No valid data to merge. Check files.")
