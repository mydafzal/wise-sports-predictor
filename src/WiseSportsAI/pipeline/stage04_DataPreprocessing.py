import os
from WiseSportsAI.components.datapreprocessing import DataPreprocessing

def main():
    """Main function to run data preprocessing."""
    input_file = "Artifacts/DataScraping/MergedDataSet.csv"
    output_file = "Artifacts/DataScraping/PreprocessedData.csv"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print("<------------------ 🚀 Stage04: Started Data Preprocessing ------------------>")

    preprocessing = DataPreprocessing(input_file)
    preprocessing.run_pipeline(output_file)

    print("<------------------ ✅ Data Preprocessing Completed ------------------>\n\n")
    
if __name__ == "__main__":
    main()
