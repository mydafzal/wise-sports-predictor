from pydantic import BaseModel
from typing import List, Dict, Optional

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    match_date: str

class DateSpecificPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    date: str  

class InjuryImpactResponse(BaseModel):
    home_team: str
    away_team: str
    original_home_score: float
    original_away_score: float
    initial_adjusted_home_score: float
    initial_adjusted_away_score: float
    final_adjusted_home_score: float
    final_adjusted_away_score: float
    home_net_impact: float
    away_net_impact: float
    home_injured_players: List[Dict]
    away_injured_players: List[Dict]
    cross_impact_home_boost: float
    cross_impact_away_boost: float

class DateSpecificPredictionResponse(BaseModel):
    date: str
    home_team: str
    away_team: str
    original_home_score: int
    original_away_score: int
    adjusted_home_score: int
    adjusted_away_score: int
    home_net_impact: int
    away_net_impact: int
    home_injured_players: int
    away_injured_players: int
    home_injury_details: List[Dict]
    away_injury_details: List[Dict]
    cross_impact_home_boost: float
    cross_impact_away_boost: float
    note: Optional[str] = None

class PredictionResult(BaseModel):
    game_time: str
    teams: str
    original_prediction: Dict
    adjusted_prediction: Dict
    adjustment_details: Dict

class PitcherAdjustedResult(BaseModel):
    game_time: str
    home_team: str
    away_team: str
    home_abbr: str
    away_abbr: str
    pitcher_impacts: Dict
    final_scores: Dict

class WeatherAdjustedResult(BaseModel):
    game_time: str
    home_team: str
    away_team: str
    original_prediction: Dict
    adjusted_prediction: Dict
    weather_impact: str
    error: Optional[str]
