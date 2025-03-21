from WiseSportsAI.components.datapreparation import DataPreparation

def main():
    print("< ------------------- 🚀 Stage 02: Started Data Preparation -------------------> ")
    
    data_directory = "Artifacts/DataScraping/Teams"
    data_prep = DataPreparation(data_directory)
    data_prep.run()
    
    print("<------------------- ✅ Stage 02: Data Preparation Completed ------------------->\n\n")

if __name__ == "__main__":
    main()
