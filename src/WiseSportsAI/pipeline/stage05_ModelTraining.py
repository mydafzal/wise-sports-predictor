from WiseSportsAI.components.modeltraining import ModelTraining

def main():
    input_file = "Artifacts/DataScraping/PreprocessedData.csv"
    output_dir = "Artifacts/TrainedModels"
    
    print("<------------------ 🚀 Stage05: Started Model Training ------------------>")
    
    trainer = ModelTraining(input_file, output_dir)
    trainer.run()

    print("<------------------ ✅ Model Training Completed ------------------>\n\n")

if __name__ == "__main__":
    main()
