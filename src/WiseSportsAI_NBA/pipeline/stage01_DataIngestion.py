from WiseSportsAI_NBA.components.dataingestion import DataIngestion
from WiseSportsAI_NBA.logging import logger

def main():
    print("<------------------- 🚀 Stage01: Started Data Ingestion Pipeline ------------------->")
    logger.info("<------------------- 🚀 Stage01: Started Data Ingestion Pipeline ------------------->")

    ingestion = DataIngestion()
    ingestion.run()

    print("<-------------------- ✅ Data Ingestion Pipeline Completed ------------------->\n\n")
    logger.info("<-------------------- ✅ Data Ingestion Pipeline Completed ------------------->\n\n")

if __name__ == "__main__":
    main()
