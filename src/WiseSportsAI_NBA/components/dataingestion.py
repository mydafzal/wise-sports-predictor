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
        self.driver.set_page_load_timeout(60)  
    
    def scrape_team_data(self, team_abbr, filename):
        max_retries = 3
        retry_delay = 10 
        url = f"https://www.basketball-reference.com/teams/{team_abbr}/2025/gamelog/"
        
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt+1}/{max_retries} for {team_abbr}")
                self.driver.get(url)
                
                # Wait for table to load with extended timeout
                table = WebDriverWait(self.driver, 45).until(
                    EC.presence_of_element_located((By.ID, "team_game_log_reg"))
                )
                break  
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    print(f"Max retries exhausted for {team_abbr}. Skipping...")
                    return
                time.sleep(retry_delay)
                self.driver.refresh()  

        try:
            headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
            rows = []
            for row in table.find_elements(By.TAG_NAME, "tr"):
                cells = [cell.text for cell in row.find_elements(By.XPATH, ".//th | .//td")]
                if cells:
                    rows.append(cells)
            
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(rows[1:])
            
            print(f"Successfully saved data for {team_abbr} to {file_path}")
        except Exception as e:
            print(f"Error processing data for {team_abbr}: {str(e)}")

    def run(self):
        for team_abbr, filename in self.team_mapping.items():
            self.scrape_team_data(team_abbr, filename)
            time.sleep(10)  
        self.driver.quit()
        print("Data ingestion process completed.")

