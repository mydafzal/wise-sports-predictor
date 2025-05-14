from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
import pandas as pd
import json
from typing import Any
import math
import os
import requests
import re
from pathlib import Path
from datetime import datetime, timedelta

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if pd.isna(obj) or (isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj))):
            return 0.0
        return super().default(obj)

class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomJSONEncoder,
        ).encode("utf-8")

router = APIRouter(tags=["MLB Predictions"])

TEAM_ABBR_MAP = {
    "Arizona Diamondbacks": "ARI",
    "Atlanta Braves": "ATL",
    "Baltimore Orioles": "BAL",
    "Boston Red Sox": "BOS",
    "Chicago Cubs": "CHC",
    "Chicago White Sox": "CWS",
    "Cincinnati Reds": "CIN",
    "Cleveland Guardians": "CLE",
    "Colorado Rockies": "COL",
    "Detroit Tigers": "DET",
    "Houston Astros": "HOU",
    "Kansas City Royals": "KC",
    "Los Angeles Angels": "LAA",
    "Los Angeles Dodgers": "LAD",
    "Miami Marlins": "MIA",
    "Milwaukee Brewers": "MIL",
    "Minnesota Twins": "MIN",
    "New York Mets": "NYM",
    "New York Yankees": "NYY",
    "Oakland Athletics": "OAK",
    "Philadelphia Phillies": "PHI",
    "Pittsburgh Pirates": "PIT",
    "San Diego Padres": "SD",
    "San Francisco Giants": "SF",
    "Seattle Mariners": "SEA",
    "St. Louis Cardinals": "STL",
    "Tampa Bay Rays": "TB",
    "Texas Rangers": "TEX",
    "Toronto Blue Jays": "TOR",
    "Washington Nationals": "WSH"
}

class BettingCalculator:
    def __init__(self):
        self.base_odds = {
            'moneyline': {'home': -110, 'away': -110},
            'run_line': {'home': {'line': -1.5, 'odds': -110}, 'away': {'line': 1.5, 'odds': -110}},
            'total_runs': {'line': 8.5, 'over': -110, 'under': -110}
        }

    def get_espn_event_id(self, home_team: str, away_team: str, date: str) -> Optional[str]:
        formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={date}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            home_abbr = TEAM_ABBR_MAP.get(home_team)
            away_abbr = TEAM_ABBR_MAP.get(away_team)
            
            if not home_abbr or not away_abbr:
                return None

            for event in data.get('events', []):
                competitors = event.get('competitions', [{}])[0].get('competitors', [])
                if len(competitors) != 2:
                    continue

                event_home = next((t for t in competitors if t.get('homeAway') == 'home'), None)
                event_away = next((t for t in competitors if t.get('homeAway') == 'away'), None)

                if not event_home or not event_away:
                    continue

                event_home_abbr = event_home.get('team', {}).get('abbreviation', '')
                event_away_abbr = event_away.get('team', {}).get('abbreviation', '')

                if event_home_abbr == home_abbr and event_away_abbr == away_abbr:
                    return event.get('id')
            return None
        except Exception:
            return None

    def fetch_espn_odds(self, event_id: str) -> Dict:
        if not event_id:
            return self.base_odds
            
        try:
            url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/events/{event_id}/competitions/{event_id}/odds"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            odds = self.base_odds.copy()
            provider = data.get('items', [{}])[0]

            # Moneyline
            home_ml = provider.get('homeTeamOdds', {}).get('current', {}).get('moneyLine', {}).get('american')
            away_ml = provider.get('awayTeamOdds', {}).get('current', {}).get('moneyLine', {}).get('american')
            if home_ml and away_ml:
                odds['moneyline']['home'] = int(home_ml)
                odds['moneyline']['away'] = int(away_ml)

            # Run Line
            home_spread = self._parse_spread(provider.get('homeTeamOdds', {}).get('current', {}))
            away_spread = self._parse_spread(provider.get('awayTeamOdds', {}).get('current', {}))
            odds['run_line']['home'] = home_spread
            odds['run_line']['away'] = away_spread

            # Total Runs
            over_under = provider.get('overUnder', '')
            line_match = re.search(r"(\d+\.?\d*)", over_under)
            if line_match:
                odds['total_runs']['line'] = float(line_match.group(1))
                odds['total_runs']['over'] = int(provider.get('overOdds', {}).get('american', -110))
                odds['total_runs']['under'] = int(provider.get('underOdds', {}).get('american', -110))

            return odds
        except Exception:
            return self.base_odds

    def _parse_spread(self, odds_data: Dict) -> Dict:
        try:
            spread = odds_data.get('pointSpread', {}).get('american', '+1.5')
            odds = odds_data.get('spread', {}).get('american', -110)
            return {
                'line': float(spread.replace('EVEN', '0')),
                'odds': int(odds)
            }
        except:
            return {'line': 1.5, 'odds': -110}

    def calculate_total_confidence(self, projected: float, book_line: float) -> Dict:
        diff = abs(projected - book_line)
        if diff >= 0.15:
            confidence = 52.5 + (3.5 * diff)
            recommendation = 'Over' if projected > book_line else 'Under'
        else:
            confidence = None
            recommendation = 'No Edge'
        
        # Add precise rounding
        if confidence is not None:
            confidence = round(confidence, 1)
            
        return {
            'line': book_line,
            'projection': round(projected, 2),
            'difference': round(diff, 2),
            'confidence': min(100, max(0, confidence)) if confidence else None,
            'recommendation': recommendation,
            'has_edge': confidence is not None
        }

    def calculate_spread_confidence(self, margin: float) -> Dict:
        abs_margin = abs(margin)
        if abs_margin >= 0.6:
            confidence = 52.5 + (3.5 * abs_margin)
        else:
            confidence = None
        
        # Add precise rounding
        if confidence is not None:
            confidence = round(confidence, 1)
            
        return {
            'margin': round(margin, 2),  # Increased precision
            'confidence': min(100, max(0, confidence)) if confidence else None,
            'has_edge': confidence is not None
        }
    
    def calculate_moneyline_confidence(self, home_runs: float, away_runs: float) -> Dict:
        margin = abs(home_runs - away_runs)
        if margin >= 0.6:
            confidence = 52.5 + (3.5 * margin)
        else:
            confidence = None
            
        return {
            'margin': round(margin, 2),
            'confidence': round(confidence, 1) if confidence else None,
            'recommendation': 'Home' if home_runs > away_runs else 'Away',
            'has_edge': confidence is not None
        }

    def calculate_spread_confidence(self, margin: float) -> Dict:
        abs_margin = abs(margin)
        if abs_margin >= 0.6:
            confidence = 52.5 + (3.5 * abs_margin)
        else:
            confidence = None
            
        return {
            'margin': round(margin, 1),
            'confidence': min(100, max(0, round(confidence, 1))) if confidence else None,
            'has_edge': confidence is not None
        }

    def get_spread_recommendation(self, margin: float, home_line: float, away_line: float) -> Dict:
        favorite = 'home' if home_line <= -1.5 else 'away'
        spread_line = home_line if favorite == 'home' else away_line
        
        if (favorite == 'home' and margin > 1.5) or (favorite == 'away' and margin < -1.5):
            pick = f"{favorite.capitalize()} {spread_line}"
            reason = "Projected margin > 1.5 runs"
        else:
            underdog = 'away' if favorite == 'home' else 'home'
            pick = f"{underdog.capitalize()} {abs(spread_line)}"
            reason = "Projected margin ≤ 1.5 runs"
            
        return {
            'pick': pick,
            'reason': reason,
            'favorite': favorite,
            'spread_line': spread_line
        }

    def get_stars(self, confidence: Optional[float]) -> str:
        if not confidence:
            return "★☆☆☆☆ (No Edge)"
        if confidence >= 90: return "★★★★★"
        if confidence >= 75: return "★★★★☆"
        if confidence >= 60: return "★★★☆☆"
        if confidence >= 52.5: return "★★☆☆☆"
        return "★☆☆☆☆"

def load_predictions(date: str) -> pd.DataFrame:
    try:
        dir_path = Path("Artifacts/MLB_Artifacts/WeatherAdjustments")
        files = sorted(dir_path.glob(f"weatheradjustments_{date}_*.csv"), 
                       key=lambda x: x.stat().st_mtime, 
                       reverse=True)
        
        if not files:
            yesterday = (datetime.strptime(date, "%Y%m%d") - timedelta(1)).strftime("%Y%m%d")
            files = sorted(dir_path.glob(f"weatheradjustments_{yesterday}_*.csv"), 
                           key=lambda x: x.stat().st_mtime, 
                           reverse=True)
        
        if not files:
            raise FileNotFoundError("No prediction files found")
            
        return pd.read_csv(files[0])
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.get("/mlb/finalscores", response_class=JSONResponse)
async def get_finalscores(date: Optional[str] = None):
    date = date or datetime.today().strftime("%Y%m%d")
    calculator = BettingCalculator()
    
    try:
        df = load_predictions(date)
        results = []

        for _, row in df.iterrows():
            try:
                if pd.isna(row['adjusted_home']) or pd.isna(row['adjusted_away']):
                    continue

                # Core values
                home_runs = clean_float(row['adjusted_home'])
                away_runs = clean_float(row['adjusted_away'])
                total_runs = home_runs + away_runs
                margin = home_runs - away_runs

                # Get odds data
                event_id = calculator.get_espn_event_id(row['home_team'], row['away_team'], date)
                odds = calculator.fetch_espn_odds(event_id)

                # Calculate analyses
                total_analysis = calculator.calculate_total_confidence(total_runs, odds['total_runs']['line'])
                spread_analysis = calculator.calculate_spread_confidence(margin)
                moneyline_analysis = calculator.calculate_moneyline_confidence(home_runs, away_runs)
                spread_rec = calculator.get_spread_recommendation(
                    margin,
                    odds['run_line']['home']['line'],
                    odds['run_line']['away']['line']
                )

                game_data = {
                    'game_time': str(row['game_time']),
                    'matchup': f"{row['away_team']} @ {row['home_team']}",
                    'projections': {
                        'home': round(home_runs, 2),
                        'away': round(away_runs, 2),
                        'total': round(total_runs, 2),
                        'margin': round(margin, 2)
                    },
                    'analysis': {
                        'moneyline': {
                            'projection': moneyline_analysis['margin'],
                            'recommendation': moneyline_analysis['recommendation'],
                            'confidence': moneyline_analysis['confidence'],
                            'stars': calculator.get_stars(moneyline_analysis['confidence']),
                            'has_edge': moneyline_analysis['has_edge']
                        },
                        'total_runs': {
                            **total_analysis,
                            'stars': calculator.get_stars(total_analysis['confidence'])
                        },
                        'run_line': {
                            'projection': spread_analysis['margin'],
                            'confidence': spread_analysis['confidence'],
                            'recommendation': spread_rec['pick'],
                            'reason': spread_rec['reason'],
                            'stars': calculator.get_stars(spread_analysis['confidence']),
                            'favorite': spread_rec['favorite'],
                            'spread_line': spread_rec['spread_line']
                        }
                    },
                    'current_odds': odds,
                    'espn_event_id': event_id or 'Not found'
                }
                results.append(game_data)
            except Exception as e:
                print(f"Skipping game: {str(e)}")

        return {'date': date, 'games': results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def clean_float(value):
    try:
        return 0.0 if pd.isna(value) or math.isinf(value) else float(value)
    except:
        return 0.0