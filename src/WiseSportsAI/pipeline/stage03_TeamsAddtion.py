import os
from WiseSportsAI.components.teamsaddition import TeamsDataAddition

def main():
    team_stats_path = "Artifacts/DataScraping/TeamsData/TeamsStats.csv"
    matches_data_path = "Artifacts/DataScraping/AllTeamsMatches2025.csv"
    output_path = "Artifacts/DataScraping/MergedDataSet.csv"
    
    print("<------------------- 🚀 Stage03: tarted the Teams Data Addition Pipeline ------------------->")
    teams_data_addition = TeamsDataAddition(team_stats_path, matches_data_path, output_path)
    teams_data_addition.run()
    print("<------------------- ✅ Teams Data Addition Pipeline completed successfully ------------------->\n\n")

if __name__ == "__main__":
    main()
