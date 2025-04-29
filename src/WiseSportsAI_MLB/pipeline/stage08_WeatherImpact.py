from WiseSportsAI_MLB.components.weatherimpact import WeatherImpactCalculator
from pathlib import Path
import json
import csv
import datetime

class WeatherImpactPipeline:
    def __init__(self):
        self.input_path = Path("Artifacts/MLB_Artifacts/StartingPitcherAdjustments")
        self.output_dir = Path("Artifacts/MLB_Artifacts/WeatherAdjustments")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.calculator = WeatherImpactCalculator()
        
    def find_latest_file(self):
        files = list(self.input_path.glob("starterpitcheradjusted_*.json"))
        if not files:
            raise FileNotFoundError("No adjustment files found")
        return max(files, key=lambda x: x.stat().st_ctime)
    
    def process_games(self, input_file):
        with open(input_file) as f:
            games = json.load(f)
            
        results = []
        for game in games:
            result = self.calculator.adjust_game(game)
            results.append(result)
            
        return results
    
    def save_results(self, results):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        output_file = self.output_dir / f"weatheradjustments_{timestamp}.csv"
        
        fieldnames = [
            "game_time", "home_team", "away_team",
            "original_home", "original_away",
            "adjusted_home", "adjusted_away",
            "weather_impact", "error"
        ]
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                # Convert float values to strings with 2 decimal places
                cleaned_result = {
                    k: f"{v:.2f}" if isinstance(v, float) else v
                    for k, v in result.items()
                }
                writer.writerow(cleaned_result)
                
        return output_file
    
    def run_pipeline(self):
        try:
            print("⛈️ Starting Weather Impact Adjustment Pipeline")
            input_file = self.find_latest_file()
            print(f"📥 Loading input file: {input_file}")
            
            results = self.process_games(input_file)
            output_file = self.save_results(results)
            
            print(f"✅ Successfully processed {len(results)} games")
            print(f"📤 Output saved to: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Pipeline failed: {str(e)}")
            return False

if __name__ == "__main__":
    pipeline = WeatherImpactPipeline()
    pipeline.run_pipeline()