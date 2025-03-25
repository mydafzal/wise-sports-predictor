import os
import sys
from datetime import datetime
from WiseSportsAI.pipeline.stage01_DataIngestion import main as stage01_main
from WiseSportsAI.pipeline.stage02_DataPreparation import main as stage02_main
from WiseSportsAI.pipeline.stage03_TeamsAddtion import main as stage03_main
from WiseSportsAI.pipeline.stage04_DataPreprocessing import main as stage04_main
from WiseSportsAI.pipeline.stage05_ModelTraining import main as stage05_main
from WiseSportsAI.pipeline.stage06_ModelPredictions import main as stage06_main
from WiseSportsAI.pipeline.stage07_FuturePredictions import main as stage07_main
from WiseSportsAI.pipeline.stage08_InjuriesImpact import main as stage08_main
from WiseSportsAI.logging import logger

def run_pipeline():
    """Run the entire pipeline from stage 1 to stage 7."""
    print("Started WiseSportsAI Pipeline 🫠 ")
    logger.info("Started WiseSportsAI Pipeline 🫠 ")

    start_time = datetime.now()

    try:
        # Stage 1: Data Ingestion
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

        print("WiseSportsAI Pipeline Completed Successfully 😁")
        logger.info("WiseSportsAI Pipeline Completed Successfully 😁")

    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        raise

    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"\n✅ Pipeline completed in {duration}.")

if __name__ == "__main__":
    run_pipeline()