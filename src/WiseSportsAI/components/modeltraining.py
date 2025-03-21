import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor

class ModelTraining:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        df = pd.read_csv(self.input_file)
        return df

    def train_model(self, X_train, y_train):
        model = XGBRegressor(
            n_estimators=2000, learning_rate=0.01, max_depth=8, subsample=1.0,
            colsample_bytree=1.0, reg_alpha=0.5, reg_lambda=1, random_state=42
        )
        model.fit(X_train, y_train)
        return model

    def evaluate_model(self, model, X_train, y_train, X_test, y_test, label):
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)

        print(f"{label} Model Performance:")
        print(f"Train RMSE: {np.sqrt(mean_squared_error(y_train, train_pred))}")
        print(f"Test RMSE: {np.sqrt(mean_squared_error(y_test, test_pred))}")
        print(f"Train R2: {r2_score(y_train, train_pred)}")
        print(f"Test R2: {r2_score(y_test, test_pred)}")

    def run(self):
        df = self.load_data()

        # Train Home Team Score Model
        X_home = df.drop(columns=['home_team_score'])
        y_home = df['home_team_score']
        X_train_home, X_test_home, y_train_home, y_test_home = train_test_split(X_home, y_home, test_size=0.2, random_state=42)

        xgb_home = self.train_model(X_train_home, y_train_home)
        self.evaluate_model(xgb_home, X_train_home, y_train_home, X_test_home, y_test_home, "Home Team Score")
        joblib.dump(xgb_home, os.path.join(self.output_dir, "xgb_home_score_model.pkl"))

        # Train Away Team Score Model
        X_away = df.drop(columns=['away_team_score'])
        y_away = df['away_team_score']
        X_train_away, X_test_away, y_train_away, y_test_away = train_test_split(X_away, y_away, test_size=0.2, random_state=42)

        xgb_away = self.train_model(X_train_away, y_train_away)
        self.evaluate_model(xgb_away, X_train_away, y_train_away, X_test_away, y_test_away, "Away Team Score")
        joblib.dump(xgb_away, os.path.join(self.output_dir, "xgb_away_score_model.pkl"))

        print("Model training completed and saved in", self.output_dir)
