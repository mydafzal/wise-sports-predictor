from WiseSportsAI_MLB.components.modeltraining import ModelTrainer
from WiseSportsAI_MLB.logging import logger
from box import ConfigBox
import os

STAGE_NAME = "Model Training Stage"

class ModelTrainingPipeline:
    def __init__(self):
        self.processed_data_path = "Artifacts/MLB_Artifacts/MLB_Processed_Data.csv"
        self.artifacts_dir = "Artifacts/MLB_Artifacts/Model_Artifacts"

    def main(self) -> ConfigBox:

        result = ConfigBox({
            'stage_name': STAGE_NAME,
            'status': False,
            'message': '',
            'artifacts_dir': self.artifacts_dir,
            'metrics': None
        })
        
        try:
            logger.info(f">>>>>>>>>>>> Stage {STAGE_NAME} started <<<<<<<<<<<<<")
            
            model_trainer = ModelTrainer(processed_data_path=self.processed_data_path)

            df = model_trainer.load_data()
            
            X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = model_trainer.split_data(df)
            
            X_train_scaled, X_test_scaled, scaler = model_trainer.scale_features(X_train, X_test)
            
            home_model, away_model = model_trainer.train_models(X_train_scaled, y_home_train, y_away_train)
            
            metrics = model_trainer.evaluate_models(
                home_model, away_model, X_test_scaled, y_home_test, y_away_test
            )
            
            model_trainer.save_models(
                home_model, away_model, scaler, X_train.columns.tolist(), self.artifacts_dir
            )
            
            result.update({
                'status': True,
                'message': f"{STAGE_NAME} completed successfully",
                'metrics': metrics
            })
            
            logger.info(f"Home Model Metrics - MSE: {metrics['home_model']['mse']:.2f}, R2: {metrics['home_model']['r2']:.2f}")
            logger.info(f"Away Model Metrics - MSE: {metrics['away_model']['mse']:.2f}, R2: {metrics['away_model']['r2']:.2f}")
            logger.info(f">>>>>>>>>>> Stage {STAGE_NAME} completed <<<<<<<<<<<\n\n")
            
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
        pipeline = ModelTrainingPipeline()
        result = pipeline.main()
        if not result.status:
            logger.error(f"Stage failed: {result.message}")
            exit(1)
    except Exception as e:
        logger.exception(e)
        exit(1)