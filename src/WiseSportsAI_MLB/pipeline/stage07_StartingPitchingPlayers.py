import json
from datetime import datetime
from pathlib import Path
from WiseSportsAI_MLB.components.startingpitchingplayers import StartingPitcherDataLoader, PitcherBasedScorer

class StartingPitchingAdjustor:
    def __init__(self):
        self.data_loader = StartingPitcherDataLoader()
        self.scorer = PitcherBasedScorer(self.data_loader.combined_data)
        self.input_dir = Path("Artifacts/MLB_Artifacts/Adjusted_Predictions")
        self.output_dir = Path("Artifacts/MLB_Artifacts/StartingPitcherAdjustments")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_latest_predictions(self):
        pred_files = sorted(self.input_dir.glob("adjusted_predictions_*.json"), reverse=True)
        if not pred_files:
            raise FileNotFoundError("No prediction files found")
        with open(pred_files[0]) as f:
            return json.load(f), pred_files[0].name

    def _convert_date_format(self, dd_mm_yyyy):
        try:
            day, month, year = dd_mm_yyyy.split('-')
            return f"{year}-{month}-{day}"
        except ValueError:
            raise ValueError(f"Invalid date format: {dd_mm_yyyy}")

    def process_predictions(self):
        predictions, filename = self._load_latest_predictions()
        processed = []
        
        for game in predictions:
            pred = game['prediction']
            if not pred['status']: 
                processed.append(game)
                continue
            
            try:
                home_abbr = self.scorer.abbreviation_conversion.get(
                    pred['home_team'], 
                    pred['home_team']
                )
                away_abbr = self.scorer.abbreviation_conversion.get(
                    pred['away_team'], 
                    pred['away_team']
                )
                
                existing_adj = pred['pitching_adjustment']['adjusted_scores']
                adj_home, adj_away = self.scorer.adjust_game_scores(
                    home_abbr,
                    away_abbr,
                    float(existing_adj['adjusted_home_runs']),
                    float(existing_adj['adjusted_away_runs']),
                    self._convert_date_format(pred['game_date'])
                )
                
                pred['pitching_adjustment']['pitcher_adjustments'] = {
                    "home_pitcher_impact": round(float(existing_adj['adjusted_home_runs']) - adj_home, 2),
                    "away_pitcher_impact": round(float(existing_adj['adjusted_away_runs']) - adj_away, 2),
                    "final_scores": {
                        "home_runs": round(adj_home, 2),
                        "away_runs": round(adj_away, 2),
                        "total": round(adj_home + adj_away, 2),
                        "spread": round(adj_home - adj_away, 2),
                        "winner": pred['home_team'] if adj_home > adj_away else pred['away_team']
                    }
                }
                pred['final_prediction'] = pred['pitching_adjustment']['pitcher_adjustments']['final_scores']
                
            except Exception as e:
                print(f"Error processing {pred['home_team']} vs {pred['away_team']}: {str(e)}")
                pred['pitching_adjustment']['error'] = str(e)
            
            processed.append(game)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = self.output_dir / f"starterpitcheradjusted_{timestamp}.json"
        with open(output_path, 'w') as f:
            json.dump(processed, f, indent=2)
        
        print(f"Successfully processed {len(processed)} games. Output saved to {output_path}")

if __name__ == "__main__":
    pipeline = StartingPitchingAdjustor()
    pipeline.process_predictions()