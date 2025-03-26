import requests
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from WiseSportsAI.logging import logger

class InjuriesImpact:
    def __init__(self):
        self.base_url = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
        self.replacement_factor = 0.9  # Teams recover 90% of lost production
        
        self.ABBREVIATION_MAPPING = {
            "CHO": "CHA",  # Charlotte Hornets
            "PHO": "PHX",  # Phoenix Suns
            "BRK": "BKN"   # Brooklyn Nets
        }
        
        self.POSITION_IMPACT = {
            'PG': {'offensive_impact': 0.3, 'defensive_impact': 0.4},
            'SG': {'offensive_impact': 0.25, 'defensive_impact': 0.35},
            'SF': {'offensive_impact': 0.2, 'defensive_impact': 0.3},
            'PF': {'offensive_impact': 0.15, 'defensive_impact': 0.25},
            'C': {'offensive_impact': 0.1, 'defensive_impact': 0.5}
        }
        
        self.INJURY_SEVERITY_MULTIPLIERS = {
            'Out': {'offensive_impact': 1.0, 'defensive_impact': 1.0},
            'Day-To-Day': {'offensive_impact': 0.5, 'defensive_impact': 0.6},
            'Questionable': {'offensive_impact': 0.3, 'defensive_impact': 0.4}
        }
        
        self.PLAYER_IMPACT_CATEGORIES = {
            'Star Player': 0.4,   # High-impact players
            'Key Starter': 0.25,  # Significant contributors
            'Rotation Player': 0.15,
            'Bench Player': 0.05
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

    def get_player_advanced_stats(self, player_stats: Dict) -> Dict:
        """Extract advanced player metrics"""
        try:
            stats = player_stats.get("statistics", {}).get("splits", [{}])[0].get("stats", [])
            advanced_stats = player_stats.get("statistics", {}).get("advanced", {})
            
            ppg = 0.0
            if stats and len(stats) > 11:
                try:
                    ppg = float(stats[11])
                except (ValueError, TypeError):
                    ppg = 0.0
            
            return {
                'ppg': ppg,
                'defensive_rating': float(advanced_stats.get('defensiveRating', 0)),
                'defensive_win_shares': float(advanced_stats.get('defensiveWinShares', 0)),
                'defensive_box_plus_minus': float(advanced_stats.get('defensiveBoxPlusMinus', 0)),
                'offensive_box_plus_minus': float(advanced_stats.get('offensiveBoxPlusMinus', 0)),
                'player_efficiency_rating': float(advanced_stats.get('playerEfficiencyRating', 0))
            }
        except Exception as e:
            logger.warning(f"Could not extract advanced metrics: {e}")
            return {
                'ppg': 0.0,
                'defensive_rating': 0.0,
                'defensive_win_shares': 0.0,
                'defensive_box_plus_minus': 0.0,
                'offensive_box_plus_minus': 0.0,
                'player_efficiency_rating': 0.0
            }

    def categorize_player_impact(self, advanced_stats: Dict) -> str:
        """Categorize player's overall impact"""
        dbpm = advanced_stats['defensive_box_plus_minus']
        obpm = advanced_stats['offensive_box_plus_minus']
        per = advanced_stats['player_efficiency_rating']
        
        if dbpm > 3 or obpm > 5 or per > 25:
            return 'Star Player'
        elif dbpm > 1.5 or obpm > 3 or per > 18:
            return 'Key Starter'
        elif dbpm > 0 or obpm > 1 or per > 12:
            return 'Rotation Player'
        else:
            return 'Bench Player'

    def calculate_impact(self, team_abbrev: str, predicted_score: float) -> Dict:
        """Calculate comprehensive injury impact with offensive and defensive components"""
        try:
            predicted_score = round(float(predicted_score))
        except (ValueError, TypeError):
            predicted_score = 0
        
        espn_abbrev = self._convert_to_espn_abbrev(team_abbrev)
        roster_data = self.get_team_roster(team_abbrev)
        if not roster_data:
            return self._default_impact_response(team_abbrev, predicted_score)

        injured_players = self.get_injured_players(roster_data)
        total_defensive_impact = 0.0
        total_offensive_impact = 0.0
        total_ppg_lost = 0.0
        significant_injuries = []

        for player in injured_players:
            player_stats = self.get_player_stats(player["id"])
            if not player_stats:
                continue

            advanced_stats = self.get_player_advanced_stats(player_stats)
            ppg = advanced_stats['ppg']
            
            if ppg < 2 and advanced_stats['defensive_box_plus_minus'] < 1:
                continue

            impact_category = self.categorize_player_impact(advanced_stats)
            
            position_impact = self.POSITION_IMPACT.get(
                player["position"], 
                {'offensive_impact': 0.1, 'defensive_impact': 0.1}
            )
            
            severity_multiplier = self.INJURY_SEVERITY_MULTIPLIERS.get(
                player["status"], 
                {'offensive_impact': 0.1, 'defensive_impact': 0.1}
            )
            
            category_weight = self.PLAYER_IMPACT_CATEGORIES.get(impact_category, 0.1)
            
            defensive_impact = (
                ppg * 
                position_impact['defensive_impact'] * 
                severity_multiplier['defensive_impact'] * 
                category_weight * 
                (1 - self.replacement_factor)
            )
            
            offensive_impact = (
                ppg * 
                position_impact['offensive_impact'] * 
                severity_multiplier['offensive_impact'] * 
                category_weight * 
                (1 - self.replacement_factor)
            )
            
            total_defensive_impact += defensive_impact
            total_offensive_impact += offensive_impact
            total_ppg_lost += ppg
            
            significant_injuries.append({
                "name": player["name"],
                "position": player["position"],
                "status": player["status"],
                "ppg": round(ppg, 1),
                "impact_category": impact_category,
                "defensive_impact": round(defensive_impact, 1),
                "offensive_impact": round(offensive_impact, 1),
                "defensive_box_plus_minus": advanced_stats['defensive_box_plus_minus'],
                "offensive_box_plus_minus": advanced_stats['offensive_box_plus_minus']
            })

        total_impact = total_defensive_impact + total_offensive_impact
        impact_factor = np.log1p(total_impact) / np.log1p(20)
        adjusted_score = predicted_score * (1 - min(impact_factor, 0.3))
        
        # Round scores and calculate net impact
        adjusted_score = round(adjusted_score)
        actual_net_impact = predicted_score - adjusted_score
        
        return {
            "team": team_abbrev,
            "original_score": predicted_score,
            "net_impact": actual_net_impact,
            "adjusted_score": adjusted_score,
            "impact_percentage": round((total_impact / predicted_score) * 100, 1) if predicted_score > 0 else 0,
            "injured_players": significant_injuries,
            "total_ppg_lost": round(total_ppg_lost, 1),
            "total_defensive_impact": round(total_defensive_impact, 1),
            "total_offensive_impact": round(total_offensive_impact, 1),
            "replacement_factor": self.replacement_factor
        }

    def adjust_scores_with_cross_impact(self, home_impact: Dict, away_impact: Dict) -> Dict:
        """Apply cross-impact adjustments to scores by exchanging net impacts"""
        # Exchange net impacts between teams
        home_final = home_impact['adjusted_score'] + away_impact['net_impact']
        away_final = away_impact['adjusted_score'] + home_impact['net_impact']

        # Round final scores to whole numbers
        home_final = round(home_final)
        away_final = round(away_final)

        # Calculate new net impacts
        new_home_net = home_impact['original_score'] - home_final
        new_away_net = away_impact['original_score'] - away_final

        return {
            'home_final_score': home_final,
            'away_final_score': away_final,
            'home_net_impact': new_home_net,
            'away_net_impact': new_away_net,
            'cross_impact': {
                'home_offensive_boost': away_impact['net_impact'],
                'away_offensive_boost': home_impact['net_impact']
            }
        }

    def _default_impact_response(self, team_abbrev: str, predicted_score: float) -> Dict:
        try:
            predicted_score = round(float(predicted_score))
        except (ValueError, TypeError):
            predicted_score = 0
            
        return {
            "team": team_abbrev,
            "original_score": predicted_score,
            "net_impact": 0,
            "adjusted_score": predicted_score,
            "impact_percentage": 0.0,
            "injured_players": [],
            "total_ppg_lost": 0.0,
            "total_defensive_impact": 0.0,
            "total_offensive_impact": 0.0
        }