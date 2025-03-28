import json
import os
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional

BASE_DIR = "Artifacts/TeamStats"
os.makedirs(BASE_DIR, exist_ok=True)

def fetch_with_retry(url: str, max_retries: int = 3, delay: int = 1) -> Optional[Dict]:
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                return None
            time.sleep(delay * (attempt + 1))

def get_stat(stats: List[Dict], name: str, default: float = 0.0) -> float:
    if not stats:
        return default
    stat = next((s for s in stats if s.get('name') == name), None)
    if not stat:
        return default
    try:
        return float(stat.get('displayValue', default))
    except (ValueError, TypeError):
        return default

def calculate_game_stats(game: Dict, team_id: str) -> Optional[Dict]:
    try:
        competition = game['competitions'][0]
        team_comp = next(c for c in competition['competitors'] if c['team']['id'] == team_id)
        opponent_comp = next(c for c in competition['competitors'] if c['team']['id'] != team_id)
        
        boxscore = fetch_with_retry(
            f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event={game['id']}"
        )
        if not boxscore or 'boxscore' not in boxscore:
            return None
            
        team_stats = next(t for t in boxscore['boxscore']['teams'] if t['team']['id'] == team_id)
        opponent_stats = next(t for t in boxscore['boxscore']['teams'] if t['team']['id'] != team_id)
        
        return {
            'game_id': game['id'],
            'date': game['date'],
            'opponent': opponent_stats['team']['abbreviation'],
            'home': team_comp['homeAway'] == 'home',
            'win': team_comp.get('winner', False),
            'stats': {
                'points': int(team_comp['score']['value']),
                'points_allowed': int(opponent_comp['score']['value']),
                'rebounds': get_stat(team_stats['statistics'], 'totalRebounds'),
                'assists': get_stat(team_stats['statistics'], 'assists'),
                'steals': get_stat(team_stats['statistics'], 'steals'),
                'blocks': get_stat(team_stats['statistics'], 'blocks'),
                'turnovers': get_stat(team_stats['statistics'], 'turnovers'),
                'field_goal_pct': get_stat(team_stats['statistics'], 'fieldGoalPct'),
                'three_point_pct': get_stat(team_stats['statistics'], 'threePointFieldGoalPct'),
                'free_throw_pct': get_stat(team_stats['statistics'], 'freeThrowPct'),
                'points_in_paint': get_stat(team_stats['statistics'], 'pointsInPaint'),
                'fast_break_points': get_stat(team_stats['statistics'], 'fastBreakPoints'),
                'second_chance_points': get_stat(team_stats['statistics'], 'secondChancePoints'),
                'biggest_lead': get_stat(team_stats['statistics'], 'largestLead')
            }
        }
    except Exception as e:
        print(f"Error processing game {game.get('id')}: {e}")
        return None

def calculate_recent_averages(games: List[Dict]) -> Dict:
    if not games:
        return {}
    
    stats = [g['stats'] for g in games]
    return {
        'points': sum(s['points'] for s in stats) / len(stats),
        'points_allowed': sum(s['points_allowed'] for s in stats) / len(stats),
        'rebounds': sum(s['rebounds'] for s in stats) / len(stats),
        'assists': sum(s['assists'] for s in stats) / len(stats),
        'steals': sum(s['steals'] for s in stats) / len(stats),
        'blocks': sum(s['blocks'] for s in stats) / len(stats),
        'turnovers': sum(s['turnovers'] for s in stats) / len(stats),
        'field_goal_pct': sum(s['field_goal_pct'] for s in stats) / len(stats),
        'three_point_pct': sum(s['three_point_pct'] for s in stats) / len(stats),
        'free_throw_pct': sum(s['free_throw_pct'] for s in stats) / len(stats),
        'points_in_paint': sum(s['points_in_paint'] for s in stats) / len(stats),
        'fast_break_points': sum(s['fast_break_points'] for s in stats) / len(stats),
        'second_chance_points': sum(s['second_chance_points'] for s in stats) / len(stats)
    }

def calculate_trends(games: List[Dict]) -> Dict:
    if not games:
        return {}
    
    # Simple trend calculations
    wins = sum(1 for g in games if g['win'])
    return {
        'momentum': wins / len(games) if games else 0,
        'fatigue': min(len(games), 5) / 5,
        'rest_days': (datetime.now() - datetime.strptime(games[0]['date'], '%Y-%m-%dT%H:%MZ')).days,
        'consistency': sum(1 for g in games if abs(g['stats']['points'] - g['stats']['points_allowed']) > 10) / len(games)
    }

def update_team_stats(team_id: str):
    try:
        print(f"Updating stats for team {team_id}")
        
        # Fetch base data
        schedule = fetch_with_retry(
            f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/schedule"
        )
        roster = fetch_with_retry(
            f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"
        )
        base_stats = fetch_with_retry(
            f"https://sports.core.api.espn.com/v2/sports/basketball/leagues/nba/seasons/2025/types/2/teams/{team_id}/statistics"
        )

        if not all([schedule, roster, base_stats]):
            print(f"Missing data for team {team_id}")
            return None

        # Process last 15 completed games
        completed_games = [
            g for g in schedule.get('events', [])
            if g.get('competitions', [{}])[0].get('status', {}).get('type', {}).get('completed', False)
        ][-15:]

        recent_games = []
        for game in completed_games:
            game_stats = calculate_game_stats(game, team_id)
            if game_stats:
                recent_games.append(game_stats)
            time.sleep(0.5)  # Be gentle with the API

        # Calculate aggregates
        recent_avgs = calculate_recent_averages(recent_games[:10])
        trends = calculate_trends(recent_games)

        # Prepare final data
        team_data = {
            'base_stats': base_stats,
            'recent_games': recent_games,
            'recent_averages': recent_avgs,
            'last_game_date': recent_games[0]['date'] if recent_games else None,
            'roster': roster.get('athletes', []),
            'trends': trends,
            'last_updated': datetime.now().isoformat()
        }

        # Save to file
        with open(f"{BASE_DIR}/{team_id}.json", 'w') as f:
            json.dump(team_data, f, indent=2)
            
        return team_data
    except Exception as e:
        print(f"Error updating stats for team {team_id}: {e}")
        return None

def get_nba_team_ids() -> List[str]:
    """Fetch all NBA team IDs from ESPN API"""
    teams_data = fetch_with_retry("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams?limit=50")
    if not teams_data:
        return []
    
    # The team data is in items array
    teams = teams_data.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])
    
    # Extract team IDs - handle both the new and old API formats
    team_ids = []
    for team in teams:
        if isinstance(team, dict):
            # New format: team is a dict with 'team' key
            if 'team' in team and 'id' in team['team']:
                team_ids.append(team['team']['id'])
            # Old format: team is a dict with 'id' directly
            elif 'id' in team:
                team_ids.append(team['id'])
    
    if not team_ids:
        print("Warning: No team IDs found in API response")
        print("API response structure:", json.dumps(teams_data, indent=2))
    
    return team_ids

def update_all_teams():
    team_ids = get_nba_team_ids()
    if not team_ids:
        print("Failed to fetch team IDs")
        return False
    
    print(f"Found {len(team_ids)} teams to update")
    
    for team_id in team_ids:
        update_team_stats(team_id)
        time.sleep(1)  # Rate limiting
    
    return True

if __name__ == "__main__":
    print("Starting team stats update...")
    success = update_all_teams()
    if success:
        print("Team stats update completed successfully")
    else:
        print("Team stats update encountered errors")