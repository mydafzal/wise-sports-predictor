from WiseSportsAI.components.dataingestion import DataIngestion

def main():
    print("<------------------- 🚀 Stage01: Started Data Ingestion Pipeline ------------------->")
    ingestion = DataIngestion()
    ingestion.run()
    print("<-------------------- ✅ Data Ingestion Pipeline Completed ------------------->\n\n")

if __name__ == "__main__":
    main()
