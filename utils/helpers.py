import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
from WiseSportsAI_NBA.components.modelpredictions import ModelPredictor
from WiseSportsAI_NBA.components.injuriesimpact import InjuriesImpact

def safe_float_convert(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def load_historical_predictions() -> pd.DataFrame:
    path = "Artifacts/FuturePredictions/historical_injuries_predictions.csv"
    return pd.read_csv(path)

model_home_path = "Artifacts/TrainedModels/xgb_home_score_model.pkl"
model_away_path = "Artifacts/TrainedModels/xgb_away_score_model.pkl"
label_encoder_home_path = "Artifacts/LabelEncoderhome_team_name.pkl"
label_encoder_away_path = "Artifacts/LabelEncoderaway_team_name.pkl"
historical_data = pd.read_csv("Artifacts/DataScraping/MergedDataSet.csv")

predictor = ModelPredictor(model_home_path, model_away_path, label_encoder_home_path, label_encoder_away_path)
injuries_analyzer = InjuriesImpact()


def get_latest_file_by_pattern(directory: Path, pattern: str) -> Path:
    files = list(directory.glob(pattern))
    file_data: List[Tuple[datetime, Path]] = []

    for file in files:
        match = re.search(r"_(\d{8})_(\d{4})", file.name)
        if match:
            dt = datetime.strptime(f"{match.group(1)}_{match.group(2)}", "%Y%m%d_%H%M")
            file_data.append((dt, file))

    if not file_data:
        return None

    return sorted(file_data, key=lambda x: x[0], reverse=True)[0][1]
    

