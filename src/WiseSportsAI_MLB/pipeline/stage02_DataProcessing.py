from WiseSportsAI_MLB.components.dataprocessing import DataProcessing
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox
import os

STAGE_NAME = "Data Processing Stage"

class DataProcessingTrainingPipeline:
    def __init__(self, artifacts_dir: str = "Artifacts/MLB_Artifacts"):
        self.artifacts_dir = artifacts_dir
        self.processed_data_path = os.path.join(artifacts_dir, "MLB_Processed_Data.csv")
        self.artifacts_output_dir = os.path.join(artifacts_dir, "MLBProcessed_Artifacts")

    def main(self) -> ConfigBox:

        result = ConfigBox({
            'stage_name': STAGE_NAME,
            'status': False,
            'message': '',
            'processed_data_path': self.processed_data_path,
            'artifacts_dir': self.artifacts_output_dir
        })
        
        try:
            logger.info(f">>>>>>>>>> Stage {STAGE_NAME} started <<<<<<<<<<")
            
            data_processor = DataProcessing(artifacts_dir=self.artifacts_dir)
            
            df23, df24 = data_processor.load_raw_data()
            
            processing_result = data_processor.prepare_data(df23, df24)
            if not processing_result.status:
                raise Exception(processing_result.message)
            
            data_processor.save_processed_data(
                processing_result.processed_data,
                self.processed_data_path
            )
            
            data_processor.save_artifacts({
                'label_encoders': processing_result.label_encoders,
                'original_home_teams': processing_result.original_home_teams,
                'original_away_teams': processing_result.original_away_teams
            }, self.artifacts_output_dir)
            
            result.update({
                'status': True,
                'message': f"{STAGE_NAME} completed successfully",
                'processed_data': processing_result.processed_data,
                'original_data': processing_result.original_data
            })
            
            logger.info(f">>>>>> Stage {STAGE_NAME} completed <<<<<<\n\n")
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
        pipeline = DataProcessingTrainingPipeline()
        result = pipeline.main()
        if not result.status:
            logger.error(f"Stage failed: {result.message}")
            exit(1)
    except Exception as e:
        logger.exception(e)
        exit(1)