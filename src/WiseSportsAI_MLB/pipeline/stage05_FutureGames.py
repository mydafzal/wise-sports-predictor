from WiseSportsAI_MLB.components.futuregames import MLBFutureGamesPredictor
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox
from datetime import datetime
from pytz import timezone
from typing import List, Dict

STAGE_NAME = "Future Games Prediction Stage"

class FutureGamesPredictionPipeline:
    def __init__(self, artifacts_path: str = "Artifacts/MLB_Artifacts"):
        self.artifacts_path = artifacts_path
        self.et = timezone('America/New_York')

    def main(self) -> ConfigBox:
        """Execute future games prediction pipeline"""
        result = ConfigBox({
            'stage_name': STAGE_NAME,
            'status': False,
            'predictions': [],
            'output_file': None,
            'error': None
        })

        try:
            logger.info(f">>>>>> {STAGE_NAME} started <<<<<<")
            
            predictor = MLBFutureGamesPredictor(self.artifacts_path)
            prediction_result = predictor.predict_todays_games()

            if prediction_result.status:
                result.update({
                    'status': True,
                    'predictions': prediction_result.predicted_games,
                    'output_file': prediction_result.output_file
                })
                self._log_predictions(prediction_result.predicted_games)
                
            current_time = datetime.now(self.et).strftime("%Y-%m-%d %I:%M %p ET")
            logger.info(f">>>>>> {STAGE_NAME} completed at {current_time} <<<<<<")
            return result

        except Exception as e:
            error_msg = f"{STAGE_NAME} failed: {str(e)}"
            logger.error(error_msg)
            result.update({
                'error': error_msg,
                'message': error_msg
            })
            return result

    def _log_predictions(self, predictions: List[Dict]) -> None:
        """Log prediction results with proper formatting"""
        logger.info("\n===== Today's Predictions =====")
        for idx, game in enumerate(predictions, 1):
            pred = game['prediction']
            logger.info(
                f"\nGame {idx}: {game['away_abbr']} @ {game['home_abbr']}\n"
                f"Time: {game['game_time']}\n"
                f"Predicted Score: {game['home_abbr']} {pred['predicted_home_runs']:.1f} - "
                f"{game['away_abbr']} {pred['predicted_away_runs']:.1f}\n"
                f"Predicted Winner: {pred['predicted_winner']}\n"
                f"Historical Matchup: {pred['historical_matchup']['games_played']} games, "
                f"{pred['historical_matchup']['home_win_pct']:.1f}% home win rate"
            )

if __name__ == '__main__':
    try:
        pipeline = FutureGamesPredictionPipeline()
        result = pipeline.main()
        
        if result.status:
            print(f"\nSuccessfully predicted {len(result.predictions)} games")
            print(f"Predictions saved to: {result.output_file}")
            print(f"Prediction time: {datetime.now(pipeline.et).strftime('%Y-%m-%d %I:%M %p ET')}")
        else:
            print(f"\nPrediction failed: {result.error}")
            
    except Exception as e:
        logger.exception(e)
        exit(1)