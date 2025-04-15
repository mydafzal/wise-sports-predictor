from WiseSportsAI_MLB.pipeline.stage01_DataIngestion import DataIngestionTrainingPipeline
from WiseSportsAI_MLB.pipeline.stage02_DataProcessing import DataProcessingTrainingPipeline
from WiseSportsAI_MLB.pipeline.stage03_ModelTraining import ModelTrainingPipeline
from WiseSportsAI_MLB.pipeline.stage04_ModelPrediction import ModelPredictionPipeline
from WiseSportsAI_MLB.pipeline.stage05_FutureGames import FutureGamesPredictionPipeline

from WiseSportsAI_MLB.logging import logger


def run_all_stages():
    try:
        logger.info("============== Pipeline: Data Ingestion ==============")
        ingestion_pipeline = DataIngestionTrainingPipeline()
        ingestion_result = ingestion_pipeline.main()
        if not ingestion_result.status:
            logger.error("❌ Data Ingestion Failed!")
            return

        logger.info("============== Pipeline: Data Processing ==============")
        processing_pipeline = DataProcessingTrainingPipeline()
        processing_result = processing_pipeline.main()
        if not processing_result.status:
            logger.error("❌ Data Processing Failed!")
            return

        logger.info("============== Pipeline: Model Training ==============")
        training_pipeline = ModelTrainingPipeline()
        training_result = training_pipeline.main()
        if not training_result.status:
            logger.error("❌ Model Training Failed!")
            return

        logger.info("============== Pipeline: Model Prediction ==============")
        prediction_pipeline = ModelPredictionPipeline()

        # You can choose between single or batch mode
        prediction_result = prediction_pipeline.main(
            prediction_type="single",
            home_team="NYY",
            away_team="BOS",
            game_date="15-05-2025"
        )

        if prediction_result.status:
            logger.info("✅ Prediction successful!")
            print("\n===== Prediction Results =====")
            print(f"Game: {prediction_result.home_team} vs {prediction_result.away_team} on {prediction_result.game_date}")
            print(f"Predicted Home Runs ({prediction_result.home_team}): {prediction_result.predicted_home_runs}")
            print(f"Predicted Away Runs ({prediction_result.away_team}): {prediction_result.predicted_away_runs}")
            print(f"Predicted Winner: {prediction_result.predicted_winner}")
        else:
            logger.error("❌ Model Prediction Failed!")


        logger.info("============== Pipeline: Future Games Predictions==============")
        future_games = FutureGamesPredictionPipeline()
        future_games_result = future_games.main()

        if future_games_result.status:
            print(f"\nSuccessfully predicted {len(future_games_result.predictions)} games")
            print(f"Predictions saved to: {future_games_result.output_file}")
        else:
            print(f"\nPrediction failed: {future_games_result.error}")
            

    except Exception as e:
        logger.exception(f"🔥 Pipeline crashed: {str(e)}")


if __name__ == "__main__":
    run_all_stages()
