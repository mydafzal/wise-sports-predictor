import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox
from typing import Tuple
import pickle

class DataProcessing:
    def __init__(self, artifacts_dir: str = "Artifacts/MLB_Artifacts"):

        self.artifacts_dir = artifacts_dir
        self.data_2023_path = os.path.join(artifacts_dir, "MLB_2023_Data.csv")
        self.data_2024_path = os.path.join(artifacts_dir, "MLB_2024_Data.csv")
        self.data_2025_path = os.path.join(artifacts_dir, "MLB_2025_Data.csv")

        self._validate_paths()

    def _validate_paths(self):
        if not os.path.exists(self.data_2023_path):
            raise FileNotFoundError(f"2023 data file not found at {self.data_2023_path}")
        if not os.path.exists(self.data_2024_path):
            raise FileNotFoundError(f"2024 data file not found at {self.data_2024_path}")
        if not os.path.exists(self.data_2024_path):
            raise FileNotFoundError(f"2024 data file not found at {self.data_2025_path}")

    def load_raw_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        logger.info("Loading raw data files")
        df23 = pd.read_csv(self.data_2023_path)
        df24 = pd.read_csv(self.data_2024_path)
        df25 = pd.read_csv(self.data_2025_path)
        return df23, df24, df25

    def prepare_data(self, df23: pd.DataFrame, df24: pd.DataFrame, df25: pd.DataFrame) -> ConfigBox:

        try:
            logger.info("Starting data preparation")
            df = pd.concat([df23, df24, df25], ignore_index=True)
            
            df.drop(columns=[
                "HomeTeamBatting_Batting", "AwayTeamPitching_Pitching",
                "HomeTeamPitching_Pitching", "AwayTeamBatting_Batting",
                "HomeTeamBatting_Details", "AwayTeamBatting_Details"
            ], inplace=True)
            
            df.rename(columns={
                "R": "HomeTeamRuns", 
                "RA": "AwayTeamRuns",
                "W": "HomeTeamWins", 
                "L": "AwayTeamWins"
            }, inplace=True)
            
            df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
            df['Day'] = df['Date'].dt.day
            df['Month'] = df['Date'].dt.month
            df['Year'] = df['Date'].dt.year
            df['DayOfWeek'] = df['Date'].dt.dayofweek
            df['IsWeekend'] = df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
            
            original_home_teams = df['HomeTeam'].unique()
            original_away_teams = df['AwayTeam'].unique()
            
            df_original = df.copy()
            
            categorical_columns = [
                'HomeTeam', 'AwayTeam', 'Result', 'GB', 'D/N', 'Attendance',
                'HomeTeamBatting_cWPA', 'HomeTeamPitching_cWPA', 
                'AwayTeamBatting_cWPA', 'AwayTeamPitching_cWPA'
            ]
            
            label_encoders = {}
            
            for col in categorical_columns:
                if col in df.columns:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    label_encoders[col] = le
            
            df = df.drop(columns=['Date'])
            
            result = {
                'processed_data': df,
                'original_data': df_original,
                'label_encoders': label_encoders,
                'original_home_teams': original_home_teams,
                'original_away_teams': original_away_teams,
                'status': True,
                'message': "Data processing completed successfully"
            }
            
            logger.info(result['message'])
            return ConfigBox(result)
            
        except Exception as e:
            error_msg = f"Error in data preparation: {str(e)}"
            logger.error(error_msg)
            return ConfigBox({
                'status': False,
                'error': error_msg,
                'message': "Data processing failed"
            })

    def save_processed_data(self, processed_data: pd.DataFrame, output_path: str) -> None:

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            processed_data.to_csv(output_path, index=False)
            logger.info(f"Processed data saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving processed data: {str(e)}")
            raise

    def save_artifacts(self, artifacts: dict, output_dir: str) -> None:

        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for col, encoder in artifacts['label_encoders'].items():
                safe_col = col.replace('/', '_')
                encoder_path = os.path.join(output_dir, f"{safe_col}_encoder.pkl")
                
                with open(encoder_path, 'wb') as f:
                    pickle.dump(encoder, f)
                logger.info(f"Saved {col} encoder to {encoder_path}")
            
            artifacts_path = os.path.join(output_dir, "processing_artifacts.pkl")
            artifact_data = {
                'original_home_teams': artifacts['original_home_teams'],
                'original_away_teams': artifacts['original_away_teams']
            }
            
            with open(artifacts_path, 'wb') as f:
                pickle.dump(artifact_data, f)
            logger.info(f"Saved processing artifacts to {artifacts_path}")
            
        except Exception as e:
            logger.error(f"Error saving artifacts: {str(e)}")
            raise