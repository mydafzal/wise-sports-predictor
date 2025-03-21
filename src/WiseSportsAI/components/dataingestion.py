import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DataIngestion:
    def __init__(self, output_dir="Artifacts/DataScraping/Teams"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.team_mapping = {
            "ATL": "Atlanta_Hawks.csv", "BOS": "Boston_Celtics.csv",
            "CHI": "Chicago_Bulls.csv", "CLE": "Cleveland_Cavaliers.csv",
            "DAL": "Dallas_Mavericks.csv", "DEN": "Denver_Nuggets.csv",
            "DET": "Detroit_Pistons.csv", "GSW": "Golden_State_Warriors.csv",
            "HOU": "Houston_Rockets.csv", "IND": "Indiana_Pacers.csv",
            "LAC": "Los_Angeles_Clippers.csv", "LAL": "Los_Angeles_Lakers.csv",
            "MEM": "Memphis_Grizzlies.csv", "MIA": "Miami_Heat.csv",
            "MIL": "Milwaukee_Bucks.csv", "MIN": "Minnesota_Timberwolves.csv",
            "NOP": "New_Orleans_Pelicans.csv", "NYK": "New_York_Knicks.csv",
            "OKC": "Oklahoma_City_Thunder.csv", "ORL": "Orlando_Magic.csv",
            "PHI": "Philadelphia_76ers.csv", "PHO": "Phoenix_Suns.csv",
            "POR": "Portland_Trail_Blazers.csv", "SAC": "Sacramento_Kings.csv",
            "SAS": "San_Antonio_Spurs.csv", "TOR": "Toronto_Raptors.csv",
            "UTA": "Utah_Jazz.csv", "WAS": "Washington_Wizards.csv",
            "BRK": "Brooklyn_Nets.csv", "CHO": "Charlotte_Hornets.csv"
        }

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def scrape_team_data(self, team_abbr, filename):
        url = f"https://www.basketball-reference.com/teams/{team_abbr}/2025/gamelog/"
        print(f"Scraping data for {team_abbr} from {url}")
        self.driver.get(url)
        
        try:
            table = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "team_game_log_reg"))
            )
        except:
            print(f"Error: Table not found for {team_abbr}. Skipping...")
            return
        
        headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
        rows = []
        for row in table.find_elements(By.TAG_NAME, "tr"):
            cells = [cell.text for cell in row.find_elements(By.XPATH, ".//th | .//td")]
            if cells:
                rows.append(cells)
        
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows[1:])  # Skip the first row (header row)
        
        print(f"Data for {team_abbr} saved to {file_path}")
    
    def run(self):
        for team_abbr, filename in self.team_mapping.items():
            self.scrape_team_data(team_abbr, filename)
            time.sleep(2)  # Avoid overwhelming the server
        self.driver.quit()
        print("Data Scraping Complete.")
