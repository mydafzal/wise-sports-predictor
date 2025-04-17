import argparse
from WiseSportsAI_MLB.pipeline.stage06_StartingPitching import StartingPitchingAdjustmentPipeline
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox
import json
import os

def run_adjustments(prediction_file: str):
    """Run pitching adjustments on a saved predictions file"""
    try:
        # Validate file exists
        if not os.path.exists(prediction_file):
            raise FileNotFoundError(f"Prediction file {prediction_file} not found")

        # Load predictions from file
        with open(prediction_file, 'r') as f:
            predictions = json.load(f)

        # Create mock previous stage output
        mock_input = ConfigBox({
            'status': True,
            'predictions': predictions,
            'output_file': prediction_file
        })

        # Run adjustment pipeline
        pipeline = StartingPitchingAdjustmentPipeline()
        result = pipeline.main(mock_input)

        if result.status:
            logger.info("\n===== Adjustment Results =====")
            logger.info(f"Input File: {prediction_file}")
            logger.info(f"Output File: {result.output_file}")
            logger.info(f"Adjusted Games: {len(result.adjusted_games)}")
        else:
            logger.error(f"Adjustment failed: {result.error}")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run pitching adjustments on existing predictions')
    parser.add_argument('--input', type=str, required=True,
                       help='Path to predictions JSON file')
    args = parser.parse_args()

    run_adjustments(args.input)