import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox
from typing import Tuple, Dict

class ModelTrainer:
    def __init__(self, processed_data_path: str = "Artifacts/MLB_Artifacts/Processed_data.csv"):

        self.processed_data_path = processed_data_path
        self._validate_path()

    def _validate_path(self):

        if not os.path.exists(self.processed_data_path):
            raise FileNotFoundError(f"Processed data file not found at {self.processed_data_path}")

    def load_data(self) -> pd.DataFrame:

        logger.info("Loading processed data")
        return pd.read_csv(self.processed_data_path)

    def split_data(self, df: pd.DataFrame) -> Tuple:
 
        logger.info("Splitting data into features and targets")
        X = df.drop(['HomeTeamRuns', 'AwayTeamRuns'], axis=1)
        y_home = df['HomeTeamRuns']
        y_away = df['AwayTeamRuns']
        
        X_train, X_test, y_home_train, y_home_test = train_test_split(
            X, y_home, test_size=0.2, random_state=42
        )
        _, _, y_away_train, y_away_test = train_test_split(
            X, y_away, test_size=0.2, random_state=42
        )
        
        return X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test

    def scale_features(self, X_train: pd.DataFrame, X_test: pd.DataFrame) -> Tuple:

        logger.info("Scaling features")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        return X_train_scaled, X_test_scaled, scaler

    def train_models(self, X_train: np.ndarray, y_home_train: pd.Series, y_away_train: pd.Series) -> Tuple:

        logger.info("Training models")
        
        home_model = XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        home_model.fit(X_train, y_home_train)
        
        away_model = XGBRegressor(
            objective='reg:squarederror',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        away_model.fit(X_train, y_away_train)
        
        return home_model, away_model

    def evaluate_models(self, home_model, away_model, X_test: np.ndarray, 
                       y_home_test: pd.Series, y_away_test: pd.Series) -> Dict:
        
        logger.info("Evaluating models")

        y_home_pred = home_model.predict(X_test)
        home_metrics = {
            'mse': mean_squared_error(y_home_test, y_home_pred),
            'r2': r2_score(y_home_test, y_home_pred)
        }

        y_away_pred = away_model.predict(X_test)
        away_metrics = {
            'mse': mean_squared_error(y_away_test, y_away_pred),
            'r2': r2_score(y_away_test, y_away_pred)
        }
        
        return {
            'home_model': home_metrics,
            'away_model': away_metrics
        }

    def save_models(self, home_model, away_model, scaler, feature_names: list, 
                   output_dir: str = "Artifacts/MLB_Artifacts/Model_Artifacts") -> None:

        try:
            os.makedirs(output_dir, exist_ok=True)
            
            home_model_path = os.path.join(output_dir, "home_runs_model.pkl")
            with open(home_model_path, 'wb') as f:
                pickle.dump(home_model, f)
            logger.info(f"Saved home runs model to {home_model_path}")
            
            away_model_path = os.path.join(output_dir, "away_runs_model.pkl")
            with open(away_model_path, 'wb') as f:
                pickle.dump(away_model, f)
            logger.info(f"Saved away runs model to {away_model_path}")
            
            scaler_path = os.path.join(output_dir, "scaler.pkl")
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            logger.info(f"Saved scaler to {scaler_path}")
            
            features_path = os.path.join(output_dir, "feature_names.pkl")
            with open(features_path, 'wb') as f:
                pickle.dump(feature_names, f)
            logger.info(f"Saved feature names to {features_path}")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            raise