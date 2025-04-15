from WiseSportsAI_MLB.components.modelprediction import BaseballRunPredictor
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox
import pandas as pd

STAGE_NAME = "Model Prediction Stage"

class ModelPredictionPipeline:
    def __init__(self, artifacts_path: str = "Artifacts/MLB_Artifacts"):
        self.artifacts_path = artifacts_path
        self.predictor = BaseballRunPredictor(artifacts_path)

    def predict_single_game(self, home_team: str, away_team: str, game_date: str) -> ConfigBox:

        logger.info(f"Predicting game: {home_team} vs {away_team} on {game_date}")
        return self.predictor.predict_runs(home_team, away_team, game_date)

    def predict_from_csv(self, input_path: str, output_path: str) -> ConfigBox:

        result = ConfigBox({
            'status': False,
            'input_path': input_path,
            'output_path': output_path,
            'games_processed': 0,
            'errors': []
        })
        
        try:
            logger.info(f"Loading games from {input_path}")
            games_df = pd.read_csv(input_path)
            
            predictions = []
            for _, row in games_df.iterrows():
                prediction = self.predict_runs(
                    row['HomeTeam'],
                    row['AwayTeam'],
                    row['Date']
                )
                
                if prediction.status:
                    predictions.append({
                        'HomeTeam': prediction.home_team,
                        'AwayTeam': prediction.away_team,
                        'Date': prediction.game_date,
                        'PredictedHomeRuns': prediction.predicted_home_runs,
                        'PredictedAwayRuns': prediction.predicted_away_runs,
                        'PredictedWinner': prediction.predicted_winner
                    })
                    result.games_processed += 1
                else:
                    result.errors.append(f"Game {row['HomeTeam']} vs {row['AwayTeam']}: {prediction.error}")
            
            if predictions:
                pd.DataFrame(predictions).to_csv(output_path, index=False)
                logger.info(f"Saved predictions to {output_path}")
            
            result.status = True
            result.message = f"Processed {result.games_processed} games, {len(result.errors)} errors"
            return result
            
        except Exception as e:
            error_msg = f"Batch prediction error: {str(e)}"
            logger.error(error_msg)
            result.error = error_msg
            return result

    def main(self, prediction_type: str = "single", **kwargs) -> ConfigBox:

        result = ConfigBox({
            'stage_name': STAGE_NAME,
            'status': False,
            'prediction_type': prediction_type,
            'message': ''
        })
        
        try:
            logger.info(f">>>>>>>>>>>>>> Stage {STAGE_NAME} started <<<<<<<<<<<<")
            
            if prediction_type == "single":
                prediction = self.predict_single_game(
                    kwargs['home_team'],
                    kwargs['away_team'],
                    kwargs['game_date']
                )
                result.update(prediction)
            elif prediction_type == "batch":
                batch_result = self.predict_from_csv(
                    kwargs['input_path'],
                    kwargs['output_path']
                )
                result.update(batch_result)
            else:
                raise ValueError(f"Invalid prediction type: {prediction_type}")
            
            if result.status:
                logger.info(f">>>>>>>>>>>> Stage {STAGE_NAME} completed <<<<<<<<<<<<\n\n")
            else:
                logger.error(f"Stage {STAGE_NAME} failed with errors")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in {STAGE_NAME}: {str(e)}"
            logger.exception(error_msg)
            result.update({
                'error': error_msg,
                'message': f"Stage failed: {error_msg}"
            })
            return result


if __name__ == '__main__':
    try:
        pipeline = ModelPredictionPipeline()
        
        result = pipeline.main(
            prediction_type="single",
            home_team="NYY",
            away_team="BOS",
            game_date="15-05-2025"
        )
        
        if result.status:
            print("\n===== Prediction Results =====")
            print(f"Game: {result.home_team} vs {result.away_team} on {result.game_date}")
            print(f"Predicted Home Runs: {result.predicted_home_runs}")
            print(f"Predicted Away Runs: {result.predicted_away_runs}")
            print(f"Predicted Winner: {result.predicted_winner}")
        
        else:
            print(f"Prediction failed: {result.error}")
            
    except Exception as e:
        logger.exception(e)
        exit(1)