from WiseSportsAI_MLB.components.startingpitchingadjustments import StartingPitchingAdjuster
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox
from datetime import datetime
from pytz import timezone
import os
import json
from typing import List, Dict

STAGE_NAME = "Starting Pitching Adjustment Stage"

class StartingPitchingAdjustmentPipeline:
    def __init__(self, artifacts_path: str = "Artifacts/MLB_Artifacts"):
        self.artifacts_path = artifacts_path
        self.et = timezone('America/New_York')

    def main(self, previous_stage_output: ConfigBox) -> ConfigBox:
        result = ConfigBox({
            'stage_name': STAGE_NAME,
            'status': False,
            'adjusted_games': [],
            'output_file': None,
            'error': None
        })

        try:
            logger.info(f">>>>>> {STAGE_NAME} started <<<<<<")
            
            if not previous_stage_output.status:
                raise ValueError("Previous stage failed")
                
            if not previous_stage_output.predictions:
                raise ValueError("No predictions received")

            adjuster = StartingPitchingAdjuster(
                os.path.join(self.artifacts_path, "startingpitching.csv")
            )
            
            adjusted_games = adjuster.adjust_predictions(
                previous_stage_output.predictions
            )
            
            output_file = self._save_adjusted_predictions(adjusted_games)
            
            result.update({
                'status': True,
                'adjusted_games': adjusted_games,
                'output_file': output_file
            })
            
            self._log_adjustments(adjusted_games)
            logger.info(f">>>>>> {STAGE_NAME} completed <<<<<<")
            return result

        except Exception as e:
            error_msg = f"{STAGE_NAME} failed: {str(e)}"
            logger.error(error_msg)
            result.update({'error': error_msg})
            return result

    def _save_adjusted_predictions(self, predictions: List[Dict]) -> str:
        output_dir = os.path.join(self.artifacts_path, "Adjusted_Predictions")
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now(self.et).strftime("%Y%m%d_%H%M")
        output_path = os.path.join(output_dir, f"adjusted_predictions_{timestamp}.json")
        
        with open(output_path, 'w') as f:
            json.dump(predictions, f, indent=4, default=str)
            
        logger.info(f"Saved {len(predictions)} adjusted predictions to {output_path}")
        return output_path

    def _log_adjustments(self, games: List[Dict]) -> None:
        logger.info("\n===== Pitching Adjustments =====")
        for game in games:
            pred = game['prediction']
            adj = pred['pitching_adjustment']
            
            logger.info(
                f"\nGame: {game['away_abbr']} @ {game['home_abbr']}\n"
                f"Original: {game['home_abbr']} {float(pred['predicted_home_runs']) - adj['home_adjustment']:.2f} - "
                f"{game['away_abbr']} {float(pred['predicted_away_runs']) - adj['away_adjustment']:.2f}\n"
                f"Adjustments: Home {adj['home_adjustment']:+.2f}, Away {adj['away_adjustment']:+.2f}\n"
                f"New Score: {pred['predicted_home_runs']} - {pred['predicted_away_runs']}\n"
                # f"Spread: {adj['spread']:+.2f} | Total: {adj['adjusted_total']:.2f}"
            )

