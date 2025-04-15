from WiseSportsAI_MLB.components.dataingestion import DataIngestion
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox

STAGE_NAME = "Data Ingestion Stage"

class DataIngestionTrainingPipeline:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        
    def main(self) -> ConfigBox:
        result = ConfigBox({
            'stage_name': STAGE_NAME,
            'status': False,
            'message': '',
            'error': None
        })
        
        try:
            logger.info(f">>>>>>>>> Stage {STAGE_NAME} started <<<<<<<<<<")

            data_ingestion = DataIngestion(config_path=self.config_path)
            download_result = data_ingestion.download_files_from_s3()
            
            result.update({
                'status': download_result.status,
                'message': download_result.message,
                'downloaded_files': download_result.get('downloaded_files', []),
                'downloaded_count': download_result.get('downloaded_count', 0)
            })
            
            logger.info(f">>>>>> Stage {STAGE_NAME} completed <<<<<<\n\n")
            return result

        except Exception as e:
            error_msg = f"Error in {STAGE_NAME}: {e}"
            logger.exception(error_msg)
            result.update({
                'error': error_msg,
                'message': f"Stage failed: {error_msg}"
            })
            return result

if __name__ == '__main__':
    try:
        pipeline = DataIngestionTrainingPipeline()
        result = pipeline.main()
        if not result.status:
            logger.error(f"Stage failed: {result.message}")
            exit(1)
    except Exception as e:
        logger.exception(e)
        exit(1)