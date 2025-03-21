import requests
from datetime import datetime, timedelta
from typing import List, Dict

# Constants
BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team}/schedule"

TEAM_ABBREVIATIONS = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN", "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE", "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET", "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "LA Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM", "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP", "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA", "Washington Wizards": "WAS"
}

# Mapping from ESPN's team abbreviations to FastAPI's expected abbreviations
ESPN_TO_FASTAPI_MAPPING = {"PHX": "PHO", "CHA": "CHO", "BKN": "BRK"}

class FuturePredictions:
    def __init__(self):
        """Initialize the FuturePredictions class."""
        self.tomorrow = (datetime.utcnow() + timedelta(days=1)).date().isoformat()

    def fetch_tomorrows_games(self) -> List[Dict]:
        """Fetch tomorrow's NBA games from ESPN API."""
        tomorrow_games = []
        seen_games = set()

        for team in TEAM_ABBREVIATIONS.values():
            url = BASE_URL.format(team=team)
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])

                for event in events:
                    game_id = event["id"]
                    game_date = event["date"][:10]

                    if game_date == self.tomorrow and game_id not in seen_games:
                        teams_info = event["competitions"][0]["competitors"]

                        home_team = None
                        away_team = None
                        for team_info in teams_info:
                            team_name = team_info["team"]["displayName"]
                            team_abbr = TEAM_ABBREVIATIONS.get(team_name, team_name)
                            if team_info["homeAway"] == "home":
                                home_team = team_abbr
                            else:
                                away_team = team_abbr

                        # Convert ESPN abbreviations to FastAPI expected ones
                        home_team = ESPN_TO_FASTAPI_MAPPING.get(home_team, home_team)
                        away_team = ESPN_TO_FASTAPI_MAPPING.get(away_team, away_team)

                        game_info = {
                            "game_id": game_id,
                            "date": game_date,
                            "home_team": home_team,
                            "away_team": away_team,
                        }
                        tomorrow_games.append(game_info)
                        seen_games.add(game_id)

        return tomorrow_games