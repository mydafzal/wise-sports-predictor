from datetime import datetime, timedelta, timezone
from typing import List, Dict
from zoneinfo import ZoneInfo
import requests
import warnings

warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/schedule"

ESPN_TO_FASTAPI_MAPPING = {"PHX": "PHO", "CHA": "CHO", "BKN": "BRK", "GS": "GSW", "NY": "NYK", "SA": "SAS", "UTAH": "UTA", "WSH": "WAS"}

def get_nba_teams():

    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        teams = []
        for team in data['sports'][0]['leagues'][0]['teams']:
            team_info = team['team']
            teams.append({
                'id': team_info['id'],
                'name': team_info['displayName'],
                'abbreviation': team_info['abbreviation']
            })
        return teams
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return None

class FuturePredictions:
    def __init__(self):

        self.utc_tz = ZoneInfo("UTC")
        self.eastern_tz = ZoneInfo("America/New_York")
        
        now_utc = datetime.now(self.utc_tz)
        now_et = now_utc.astimezone(self.eastern_tz)

        self.target_date = (now_et + timedelta(days=0)).date()
        print(f"\nTarget date (ET): {self.target_date}")
        
        self.teams = get_nba_teams()
        if not self.teams:
            raise ValueError("Failed to fetch NBA teams data")
        
        self.team_name_to_abbr = {t['name']: t['abbreviation'] for t in self.teams}
        self.team_abbr_to_id = {t['abbreviation']: t['id'] for t in self.teams}
        self.cached_games = []

    def fetch_all_games(self) -> List[Dict]:
        """Fetch games from all team schedules with proper timezone handling"""
        seen_game_ids = set()
        games = []
        current_year = datetime.now().year

        for team in self.teams:
            team_id = team['id']
            try:
                url = BASE_URL.format(team_id=team_id)
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()

                # Check if we're getting current season data
                season_year = data.get('season', {}).get('year', current_year)
                if season_year != current_year:
                    continue

                for event in data.get("events", []):
                    try:
                        game_id = event["id"]
                        if game_id in seen_game_ids:
                            continue

                        # Date processing with proper timezone conversion
                        raw_date = event["date"].replace('Z', '+00:00')
                        game_time = datetime.fromisoformat(raw_date).astimezone(self.utc_tz)
                        game_date_et = game_time.astimezone(self.eastern_tz).date()

                        # Skip if not target date
                        if game_date_et != self.target_date:
                            continue

                        # Get competition details
                        competition = event["competitions"][0]
                        competitors = competition["competitors"]
                        
                        home_team = next((c for c in competitors if c["homeAway"] == "home"), None)
                        away_team = next((c for c in competitors if c["homeAway"] == "away"), None)

                        if not home_team or not away_team:
                            continue

                        # Get team abbreviations
                        home_name = home_team["team"]["displayName"]
                        away_name = away_team["team"]["displayName"]
                        home_abbr = self.team_name_to_abbr.get(home_name, "UNK")
                        away_abbr = self.team_name_to_abbr.get(away_name, "UNK")

                        # Apply FastAPI mapping
                        home_abbr = ESPN_TO_FASTAPI_MAPPING.get(home_abbr, home_abbr)
                        away_abbr = ESPN_TO_FASTAPI_MAPPING.get(away_abbr, away_abbr)

                        game_data = {
                            "game_id": game_id,
                            "date": game_date_et.isoformat(),
                            "home_team": home_abbr,
                            "away_team": away_abbr,
                            "season_type": event["seasonType"]["type"],
                            "utc_time": game_time.isoformat()
                        }

                        games.append(game_data)
                        seen_game_ids.add(game_id)

                    except (KeyError, IndexError) as e:
                        print(f"Skipping malformed event: {str(e)}")
                        continue

            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    continue  # Team not in playoffs
                print(f"Error fetching {team['abbreviation']}: {str(e)}")
            except Exception as e:
                print(f"Error processing {team['abbreviation']}: {str(e)}")

        return games

    def fetch_tomorrows_games(self) -> List[Dict]:
        """Get filtered games for target date"""
        if not self.cached_games:
            self.cached_games = self.fetch_all_games()
        
        return [game for game in self.cached_games 
                if game["season_type"] in {2, 3, 5}]  # 2=Regular, 3=Playoffs, 5=Postseason