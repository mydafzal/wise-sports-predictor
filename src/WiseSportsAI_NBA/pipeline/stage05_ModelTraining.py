from WiseSportsAI_NBA.components.modeltraining import ModelTraining
from WiseSportsAI_NBA.logging import logger

def main():
    input_file = "Artifacts/DataScraping/PreprocessedData.csv"
    output_dir = "Artifacts/TrainedModels"
    
    print("<------------------ 🚀 Stage05: Started Model Training ------------------>")
    logger.info("<------------------ 🚀 Stage05: Started Model Training ------------------>")

    
    trainer = ModelTraining(input_file, output_dir)
    trainer.run()

    print("<------------------ ✅ Model Training Completed ------------------>\n\n")
    logger.info("<------------------ ✅ Model Training Completed ------------------>\n\n")

if __name__ == "__main__":
    main()
