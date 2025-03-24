import requests
import pandas as pd
from typing import Dict, List, Optional
from WiseSportsAI.logging import logger

class InjuriesImpact:
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
        self.replacement_factor = 0.95  # Teams recover 95% of lost production
        
        self.ABBREVIATION_MAPPING = {
            "CHO": "CHA",  # Charlotte Hornets
            "PHO": "PHX",  # Phoenix Suns
            "BRK": "BKN"   # Brooklyn Nets
        }

    def _convert_to_espn_abbrev(self, team_abbrev: str) -> str:
        """Convert internal team abbreviation to ESPN's format"""
        return self.ABBREVIATION_MAPPING.get(team_abbrev, team_abbrev)

    def get_team_roster(self, team_abbrev: str) -> Optional[Dict]:
        espn_abbrev = self._convert_to_espn_abbrev(team_abbrev)
        url = f"{self.base_url}/teams/{espn_abbrev}/roster"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch roster for {team_abbrev} (ESPN: {espn_abbrev}): {str(e)}")
            return None

    def get_player_stats(self, player_id: str) -> Optional[Dict]:
        url = f"https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{player_id}/overview"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch stats for player {player_id}: {str(e)}")
            return None

    def get_injured_players(self, roster_data: Dict) -> List[Dict]:
        injured_players = []
        for athlete in roster_data.get("athletes", []):
            if athlete.get("injuries"):
                status = athlete["injuries"][0]["status"]
                injured_players.append({
                    "id": athlete["id"],
                    "name": athlete["fullName"],
                    "position": athlete["position"]["abbreviation"],
                    "status": status
                })
        return injured_players

    def calculate_impact(self, team_abbrev: str, predicted_score: float) -> Dict:
        espn_abbrev = self._convert_to_espn_abbrev(team_abbrev)
        roster_data = self.get_team_roster(team_abbrev)
        if not roster_data:
            return {
                "team": team_abbrev,
                "original_score": predicted_score,
                "net_impact": 0,
                "adjusted_score": predicted_score,
                "impact_percentage": 0,
                "injured_players": [],
                "total_ppg_lost": 0
            }

        injured_players = self.get_injured_players(roster_data)
        total_ppg_lost = 0
        significant_injuries = []

        for player in injured_players:
            player_stats = self.get_player_stats(player["id"])
            if player_stats:
                stats = player_stats.get("statistics", {}).get("splits", [{}])[0].get("stats", [])
                ppg = float(stats[11]) if stats and len(stats) > 11 else 0
                
                if player["status"] == "Out" or (ppg > 5 and player["status"] == "Day-To-Day"):
                    total_ppg_lost += ppg
                    significant_injuries.append({
                        "name": player["name"],
                        "position": player["position"],
                        "status": player["status"],
                        "ppg": ppg
                    })

        net_impact = total_ppg_lost * (1 - self.replacement_factor)
        impact_percentage = (net_impact / predicted_score) * 100 if predicted_score > 0 else 0

        return {
            "team": team_abbrev,
            "original_score": predicted_score,
            "net_impact": net_impact,
            "adjusted_score": predicted_score - net_impact,
            "impact_percentage": impact_percentage,
            "injured_players": significant_injuries,
            "total_ppg_lost": total_ppg_lost
        }