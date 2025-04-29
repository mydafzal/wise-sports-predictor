import argparse
from datetime import datetime

def run_mlb_pipeline():
    try:
        from WiseSportsAI_MLB.pipeline.stage01_DataIngestion import DataIngestionTrainingPipeline
        from WiseSportsAI_MLB.pipeline.stage02_DataProcessing import DataProcessingTrainingPipeline
        from WiseSportsAI_MLB.pipeline.stage03_ModelTraining import ModelTrainingPipeline
        from WiseSportsAI_MLB.pipeline.stage04_ModelPrediction import ModelPredictionPipeline
        from WiseSportsAI_MLB.pipeline.stage05_FutureGames import FutureGamesPredictionPipeline
        from WiseSportsAI_MLB.pipeline.stage06_StartingPitchingTeans import StartingPitchingAdjustmentPipeline
        from WiseSportsAI_MLB.pipeline.stage07_StartingPitchingPlayers import StartingPitchingAdjustor
        from WiseSportsAI_MLB.pipeline.stage08_WeatherImpact import WeatherImpactPipeline
        from WiseSportsAI_MLB.logging import logger

        logger.info("============== Starting MLB Pipeline ==============")

        # # Stage 1: Data Ingestion
        logger.info("============== Stage01 Data Ingestion ==============")
        ingestion_pipeline = DataIngestionTrainingPipeline()
        ingestion_result = ingestion_pipeline.main()
        if not ingestion_result.status:
            logger.error("❌ Data Ingestion Failed!")
            return

        # Stage 2: Data Processing
        logger.info("============== Stage02 Data Processing ==============")
        processing_pipeline = DataProcessingTrainingPipeline()
        processing_result = processing_pipeline.main()
        if not processing_result.status:
            logger.error("❌ Data Processing Failed!")
            return

        # Stage 3: Model Training
        logger.info("============== Stage03 Model Training ==============")
        training_pipeline = ModelTrainingPipeline()
        training_result = training_pipeline.main()
        if not training_result.status:
            logger.error("❌ Model Training Failed!")
            return

        # Stage 4: Model Prediction
        logger.info("============== Stage04 Model Prediction ==============")
        prediction_pipeline = ModelPredictionPipeline()
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
            print(f"Predicted Home Runs: {prediction_result.predicted_home_runs}")
            print(f"Predicted Away Runs: {prediction_result.predicted_away_runs}")
            print(f"Predicted Winner: {prediction_result.predicted_winner}")
        else:
            logger.error("❌ Model Prediction Failed!")

        # Stage 5: Future Games Predictions
        logger.info("============== Stage05 Future Games Predictions ==============")
        future_games = FutureGamesPredictionPipeline()
        future_games_result = future_games.main()

        if not future_games_result.status:
            logger.error("❌ Future games prediction failed!")
            return

        # Stage 6: Starting Pitching Adjustments
        logger.info("============== Stage06 Teams Starting Pitching Adjustments ==============")
        pitching_adjustments = StartingPitchingAdjustmentPipeline()
        adjustment_result = pitching_adjustments.main(future_games_result)

        if adjustment_result.status:
            logger.info(f"✅ Adjusted {len(adjustment_result.adjusted_games)} games")
            logger.info(f"📁 Adjusted predictions saved to: {adjustment_result.output_file}")
            logger.info("\n===== Final Adjusted Predictions =====")
            for game in adjustment_result.adjusted_games:
                pred = game['prediction']
                logger.info(
                    f"{game['away_abbr']} @ {game['home_abbr']}: "
                    f"{pred['predicted_home_runs']:.2f} - {pred['predicted_away_runs']:.2f} "
                    f"(Adj: {pred['pitching_adjustment']['home_adjustment']:+.2f}/"
                    f"{pred['pitching_adjustment']['away_adjustment']:+.2f})"
                )
        else:
            logger.error(f"❌ Pitching adjustments failed: {adjustment_result.error}")

        # Stage 7: Starting Pitching Players Adjustments
        logger.info("============== Stage07 Players Starting Pitching Adjustments ==============")
        playeradjustment = StartingPitchingAdjustor()
        playeradjustment.process_predictions()

        logger.info("============== Stage08 Weather Impact ==============")
        weather_impact = WeatherImpactPipeline()
        weather_impact.run_pipeline()


        logger.info("✅ MLB Pipeline Completed Successfully")

    except Exception as e:
        logger.exception(f"🔥 Pipeline execution failed: {str(e)}")
        raise
        
       

def run_nba_pipeline():
    try:
        from WiseSportsAI_NBA.logging import logger
        from WiseSportsAI_NBA.pipeline.stage01_DataIngestion import main as stage01_main
        from WiseSportsAI_NBA.pipeline.stage02_DataPreparation import main as stage02_main
        from WiseSportsAI_NBA.pipeline.stage03_TeamsAddtion import main as stage03_main
        from WiseSportsAI_NBA.pipeline.stage04_DataPreprocessing import main as stage04_main
        from WiseSportsAI_NBA.pipeline.stage05_ModelTraining import main as stage05_main
        from WiseSportsAI_NBA.pipeline.stage06_ModelPredictions import main as stage06_main
        from WiseSportsAI_NBA.pipeline.stage07_FuturePredictions import main as stage07_main
        from WiseSportsAI_NBA.pipeline.stage08_InjuriesImpact import main as stage08_main

        logger.info("============== Starting NBA Pipeline ==============")
        start_time = datetime.now()

        # Stage 1: Data Ingestion (commented out in original)
        stage01_main()

        # Stage 2: Data Preparation
        stage02_main()

        # Stage 3: Teams Data Addition
        stage03_main()

        # Stage 4: Data Preprocessing
        stage04_main()

        # Stage 5: Model Training
        stage05_main()

        # Stage 6: Model Predictions
        stage06_main()

        # Stage 7: Future Predictions
        stage07_main()

        # Stage 8: Injuries Impact Analysis
        stage08_main()

        logger.info("✅ NBA Pipeline Completed Successfully")

    except Exception as e:
        logger.error(f"❌ NBA Pipeline failed with error: {e}")
        raise

    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Pipeline execution time: {duration}")

def main():
    parser = argparse.ArgumentParser(description='Run WiseSportsAI pipeline for MLB or NBA.')
    parser.add_argument('--sport', type=str, required=True, 
                        choices=['MLB', 'NBA'], help='Sport to run pipeline for')
    args = parser.parse_args()

    if args.sport == 'MLB':
        run_mlb_pipeline()
    elif args.sport == 'NBA':
        run_nba_pipeline()

if __name__ == "__main__":
    main()