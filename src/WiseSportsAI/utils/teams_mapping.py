import pandas as pd
import os
from WiseSportsAI.components.teamstats import get_nba_team_ids
import requests

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

def create_team_mapping():
    team_ids = get_nba_team_ids()
    team_data = []
    
    for team_id in team_ids:
        response = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}")
        if response.status_code == 200:
            data = response.json()
            team_name = data['team']['displayName']
            abbrev = TEAM_ABBREVIATIONS.get(team_name, data['team']['abbreviation'])
            team_data.append({
                'team_id': team_id,
                'team_name': team_name.lower(),
                'abbreviation': abbrev
            })
    
    df = pd.DataFrame(team_data)
    os.makedirs("Artifacts/TeamInfo", exist_ok=True)
    df.to_csv("Artifacts/TeamInfo/team_mapping.csv", index=False)

if __name__ == "__main__":
    create_team_mapping()