import json
import requests
from pathlib import Path
from datetime import datetime
import csv

baseball_stadiums = [
    { 
      'name': "Angel Stadium of Anaheim", 
      'team': "LAA", 
      'teamFullName': "Los Angeles Angels",
      'lat': 33.8003, 
      'lon': -117.8827, 
      'indoor': False, 
      'hitterFriendlyScore': 4.8,
      'elevation': 154,
      'dimensions': { 'left': 330, 'center': 400, 'right': 330 },
      'homeDirection': "NE" 
    },
    { 
      'name': "Chase Field", 
      'team': "ARI", 
      'teamFullName': "Arizona Diamondbacks",
      'lat': 33.4455, 
      'lon': -112.0667, 
      'indoor': True, 
      'hitterFriendlyScore': 7.2,
      'elevation': 1086,
      'dimensions': { 'left': 330, 'center': 407, 'right': 334 },
      'homeDirection': "SE"
    },
    { 
      'name': "Citi Field", 
      'team': "NYM", 
      'teamFullName': "New York Mets",
      'lat': 40.7571, 
      'lon': -73.8458, 
      'indoor': False, 
      'hitterFriendlyScore': 4.5,
      'elevation': 10,
      'dimensions': { 'left': 335, 'center': 408, 'right': 330 },
      'homeDirection': "NE"
    },
    { 
      'name': "Comerica Park", 
      'team': "DET", 
      'teamFullName': "Detroit Tigers",
      'lat': 42.339, 
      'lon': -83.0485, 
      'indoor': False, 
      'hitterFriendlyScore': 4.7,
      'elevation': 600,
      'dimensions': { 'left': 345, 'center': 420, 'right': 330 },
      'homeDirection': "S"
    },
    { 
      'name': "Coors Field", 
      'team': "COL", 
      'teamFullName': "Colorado Rockies",
      'lat': 39.7559, 
      'lon': -104.9942, 
      'indoor': False, 
      'hitterFriendlyScore': 9.5,
      'elevation': 5280,
      'dimensions': { 'left': 347, 'center': 415, 'right': 350 },
      'homeDirection': "NE"
    },
    { 
      'name': "Dodger Stadium", 
      'team': "LAD", 
      'teamFullName': "Los Angeles Dodgers",
      'lat': 34.0739, 
      'lon': -118.24, 
      'indoor': False, 
      'hitterFriendlyScore': 5.2,
      'elevation': 500,
      'dimensions': { 'left': 330, 'center': 395, 'right': 330 },
      'homeDirection': "N"
    },
    { 
      'name': "Fenway Park", 
      'team': "BOS", 
      'teamFullName': "Boston Red Sox",
      'lat': 42.3467, 
      'lon': -71.0972, 
      'indoor': False, 
      'hitterFriendlyScore': 7.8,
      'elevation': 20,
      'dimensions': { 'left': 310, 'center': 390, 'right': 302 },
      'homeDirection': "NE"
    },
    { 
      'name': "Globe Life Field", 
      'team': "TEX", 
      'teamFullName': "Texas Rangers",
      'lat': 32.7461, 
      'lon': -97.0842, 
      'indoor': True, 
      'hitterFriendlyScore': 5.0,
      'elevation': 545,
      'dimensions': { 'left': 329, 'center': 407, 'right': 326 },
      'homeDirection': "S"
    },
    { 
      'name': "Great American Ball Park", 
      'team': "CIN", 
      'teamFullName': "Cincinnati Reds",
      'lat': 39.0974, 
      'lon': -84.5079, 
      'indoor': False, 
      'hitterFriendlyScore': 8.0,
      'elevation': 490,
      'dimensions': { 'left': 328, 'center': 404, 'right': 325 },
      'homeDirection': "NE"
    },
    { 
      'name': "Guaranteed Rate Field", 
      'team': "CWS", 
      'teamFullName': "Chicago White Sox",
      'lat': 41.8301, 
      'lon': -87.6339, 
      'indoor': False, 
      'hitterFriendlyScore': 7.5,
      'elevation': 594,
      'dimensions': { 'left': 330, 'center': 400, 'right': 335 },
      'homeDirection': "S"
    },
    { 
      'name': "Kauffman Stadium", 
      'team': "KC", 
      'teamFullName': "Kansas City Royals",
      'lat': 39.0517, 
      'lon': -94.4804, 
      'indoor': False, 
      'hitterFriendlyScore': 4.9,
      'elevation': 750,
      'dimensions': { 'left': 330, 'center': 410, 'right': 330 },
      'homeDirection': "NE"
    },
    { 
      'name': "loanDepot park", 
      'team': "MIA", 
      'teamFullName': "Miami Marlins",
      'lat': 25.7782, 
      'lon': -80.2195, 
      'indoor': True, 
      'hitterFriendlyScore': 3.8,
      'elevation': 7,
      'dimensions': { 'left': 344, 'center': 400, 'right': 341 },
      'homeDirection': "E"
    },
    { 
      'name': "Minute Maid Park", 
      'team': "HOU", 
      'teamFullName': "Houston Astros",
      'lat': 29.7573, 
      'lon': -95.3555, 
      'indoor': True, 
      'hitterFriendlyScore': 6.8,
      'elevation': 45,
      'dimensions': { 'left': 315, 'center': 409, 'right': 326 },
      'homeDirection': "N"
    },
    { 
      'name': "Nationals Park", 
      'team': "WSH", 
      'teamFullName': "Washington Nationals",
      'lat': 38.873, 
      'lon': -77.0074, 
      'indoor': False, 
      'hitterFriendlyScore': 5.5,
      'elevation': 25,
      'dimensions': { 'left': 336, 'center': 402, 'right': 335 },
      'homeDirection': "NE"
    },
    { 
      'name': "Oakland Coliseum", 
      'team': "OAK", 
      'teamFullName': "Oakland Athletics",
      'lat': 37.7516, 
      'lon': -122.2005, 
      'indoor': False, 
      'hitterFriendlyScore': 3.5,
      'elevation': 42,
      'dimensions': { 'left': 330, 'center': 400, 'right': 330 },
      'homeDirection': "E"
    },
    { 
      'name': "Oracle Park", 
      'team': "SF", 
      'teamFullName': "San Francisco Giants",
      'lat': 37.7786, 
      'lon': -122.3893, 
      'indoor': False, 
      'hitterFriendlyScore': 3.2,
      'elevation': 39,
      'dimensions': { 'left': 339, 'center': 399, 'right': 309 },
      'homeDirection': "ENE"
    },
    { 
      'name': "Oriole Park at Camden Yards", 
      'team': "BAL", 
      'teamFullName': "Baltimore Orioles",
      'lat': 39.2839, 
      'lon': -76.6219, 
      'indoor': False, 
      'hitterFriendlyScore': 7.0,
      'elevation': 36,
      'dimensions': { 'left': 333, 'center': 410, 'right': 318 },
      'homeDirection': "E"
    },
    { 
      'name': "Petco Park", 
      'team': "SD", 
      'teamFullName': "San Diego Padres",
      'lat': 32.7073, 
      'lon': -117.1566, 
      'indoor': False, 
      'hitterFriendlyScore': 4.2,
      'elevation': 13,
      'dimensions': { 'left': 334, 'center': 396, 'right': 322 },
      'homeDirection': "NE"
    },
    { 
      'name': "PNC Park", 
      'team': "PIT", 
      'teamFullName': "Pittsburgh Pirates",
      'lat': 40.4469, 
      'lon': -80.0057, 
      'indoor': False, 
      'hitterFriendlyScore': 4.8,
      'elevation': 727,
      'dimensions': { 'left': 325, 'center': 399, 'right': 320 },
      'homeDirection': "ESE"
    },
    { 
      'name': "Progressive Field", 
      'team': "CLE", 
      'teamFullName': "Cleveland Guardians",
      'lat': 41.4958, 
      'lon': -81.6853, 
      'indoor': False, 
      'hitterFriendlyScore': 5.2,
      'elevation': 653,
      'dimensions': { 'left': 325, 'center': 405, 'right': 325 },
      'homeDirection': "NE"
    },
    { 
      'name': "Rogers Centre", 
      'team': "TOR", 
      'teamFullName': "Toronto Blue Jays",
      'lat': 43.6414, 
      'lon': -79.3894, 
      'indoor': True, 
      'hitterFriendlyScore': 6.5,
      'elevation': 266,
      'dimensions': { 'left': 328, 'center': 400, 'right': 328 },
      'homeDirection': "N"
    },
    { 
      'name': "T-Mobile Park", 
      'team': "SEA", 
      'teamFullName': "Seattle Mariners",
      'lat': 47.5914, 
      'lon': -122.3325, 
      'indoor': True, 
      'hitterFriendlyScore': 4.3,
      'elevation': 15,
      'dimensions': { 'left': 331, 'center': 401, 'right': 326 },
      'homeDirection': "NE"
    },
    { 
      'name': "Target Field", 
      'team': "MIN", 
      'teamFullName': "Minnesota Twins",
      'lat': 44.9817, 
      'lon': -93.2775, 
      'indoor': False, 
      'hitterFriendlyScore': 5.0,
      'elevation': 840,
      'dimensions': { 'left': 339, 'center': 404, 'right': 328 },
      'homeDirection': "SE"
    },
    { 
      'name': "Tropicana Field", 
      'team': "TB", 
      'teamFullName': "Tampa Bay Rays",
      'lat': 27.7683, 
      'lon': -82.6534, 
      'indoor': True, 
      'hitterFriendlyScore': 3.7,
      'elevation': 45,
      'dimensions': { 'left': 315, 'center': 404, 'right': 322 },
      'homeDirection': "E"
    },
    { 
      'name': "Truist Park", 
      'team': "ATL", 
      'teamFullName': "Atlanta Braves",
      'lat': 33.8908, 
      'lon': -84.4678, 
      'indoor': False, 
      'hitterFriendlyScore': 5.3,
      'elevation': 1050,
      'dimensions': { 'left': 335, 'center': 400, 'right': 325 },
      'homeDirection': "NNE"
    },
    { 
      'name': "Wrigley Field", 
      'team': "CHC", 
      'teamFullName': "Chicago Cubs",
      'lat': 41.9484, 
      'lon': -87.6553, 
      'indoor': False, 
      'hitterFriendlyScore': 6.7,
      'elevation': 600,
      'dimensions': { 'left': 355, 'center': 400, 'right': 353 },
      'homeDirection': "ENE"
    },
    { 
      'name': "Yankee Stadium", 
      'team': "NYY", 
      'teamFullName': "New York Yankees",
      'lat': 40.8296, 
      'lon': -73.9262, 
      'indoor': False, 
      'hitterFriendlyScore': 7.5,
      'elevation': 53,
      'dimensions': { 'left': 318, 'center': 408, 'right': 314 },
      'homeDirection': "SE"
    },
    { 
      'name': "American Family Field", 
      'team': "MIL", 
      'teamFullName': "Milwaukee Brewers",
      'lat': 43.0286, 
      'lon': -87.9711, 
      'indoor': True, 
      'hitterFriendlyScore': 7.0,
      'elevation': 602,
      'dimensions': { 'left': 344, 'center': 400, 'right': 345 },
      'homeDirection': "SW"
    },
    { 
      'name': "Busch Stadium", 
      'team': "STL", 
      'teamFullName': "St. Louis Cardinals",
      'lat': 38.6226, 
      'lon': -90.1928, 
      'indoor': False, 
      'hitterFriendlyScore': 4.7,
      'elevation': 466,
      'dimensions': { 'left': 336, 'center': 400, 'right': 335 },
      'homeDirection': "NE"
    },
    { 
      'name': "Citizens Bank Park", 
      'team': "PHI", 
      'teamFullName': "Philadelphia Phillies",
      'lat': 39.9058, 
      'lon': -75.1666, 
      'indoor': False, 
      'hitterFriendlyScore': 6.4,
      'elevation': 40,
      'dimensions': { 'left': 329, 'center': 401, 'right': 330 },
      'homeDirection': "NE"
    }
]

TEAM_ABBREVIATION_MAP = {
    "KCR": "KC",    # Kansas City Royals
    "TBR": "TB",    # Tampa Bay Rays
    "WSN": "WSH",   # Washington Nationals
    "SFG": "SF",    # San Francisco Giants
    "SDP": "SD",    # San Diego Padres
    "CHW": "CWS",   # Chicago White Sox
    # Add all other teams for completeness
    "ARI": "ARI", "ATL": "ATL", "BAL": "BAL", "BOS": "BOS", 
    "CHC": "CHC", "CIN": "CIN", "CLE": "CLE", "COL": "COL",
    "DET": "DET", "HOU": "HOU", "LAA": "LAA", "LAD": "LAD",
    "MIA": "MIA", "MIL": "MIL", "MIN": "MIN", "NYM": "NYM",
    "NYY": "NYY", "OAK": "OAK", "PHI": "PHI", "PIT": "PIT",
    "SEA": "SEA", "STL": "STL", "TEX": "TEX", "TOR": "TOR"
}

class WeatherImpactCalculator:
    def __init__(self):
        self.stadiums = baseball_stadiums  # Make sure this is defined
        self.team_map = TEAM_ABBREVIATION_MAP  # Make sure this is defined
        self.api_key = "9ab58e4ce21f2bea7f8aa407e40d60a6"  # Replace with your actual API key

    def find_stadium_by_team(self, abbreviation):
        mapped_abbr = self.team_map.get(abbreviation, abbreviation)
        return next((s for s in self.stadiums if s['team'] == mapped_abbr), None)

    @staticmethod
    def degrees_to_compass(degrees):
        """Convert wind direction in degrees to compass direction."""
        if degrees is None:
            return None
        compass_points = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                         'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = int((degrees + 11.25) / 22.5) % 16
        return compass_points[index]

    def get_weather_data(self, lat, lon):
        """Fetch weather data from OpenWeatherMap API"""
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=imperial"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Weather API Error: {str(e)}")
            return None

    @staticmethod
    def get_wind_impact(wind_direction, home_direction):
        """Determine the wind impact based on directions."""
        compass_to_degrees = {
            'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5, 
            'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
            'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
            'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
        }
        
        wind_deg = compass_to_degrees.get(wind_direction, 0)
        home_deg = compass_to_degrees.get(home_direction, 0)
        
        angle_diff = abs(wind_deg - home_deg)
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
        
        if angle_diff < 45:
            return {'impact': 'negative', 'effect': -1}
        elif angle_diff > 135:
            return {'impact': 'positive', 'effect': 1}
        else:
            return {'impact': 'neutral', 'effect': 0}

    def calculate_score_adjustment(self, stadium, weather_data):
        """Calculate the total score adjustment multiplier"""
        if not stadium or not weather_data:
            return 1.0

        adjustments = {
            'base': 0.7 + (stadium['hitterFriendlyScore'] / 10 * 0.6),
            'temperature': 0.0,
            'humidity': 0.0,
            'wind': 0.0,
            'altitude': 0.0,
            'air_pressure': 0.0,
            'rain': 0.0
        }

        # Elevation adjustment
        if stadium['elevation'] > 2000:
            adjustments['altitude'] = 0.12
        elif stadium['elevation'] > 1000:
            adjustments['altitude'] = 0.07

        if not stadium['indoor'] and weather_data:
            main_data = weather_data.get('main', {})
            wind_data = weather_data.get('wind', {})
            rain_data = weather_data.get('rain', {})

            temp = main_data.get('temp', 70)
            humidity = main_data.get('humidity', 50)
            wind_speed = wind_data.get('speed', 0)
            wind_deg = wind_data.get('deg')
            pressure = main_data.get('pressure', 1013)
            rain_threat = rain_data.get('1h', 0) > 5

            # Temperature adjustments
            if temp > 80:
                adjustments['temperature'] = 0.05
            elif temp < 60:
                adjustments['temperature'] = -0.05

            # Humidity adjustments
            if humidity > 70:
                adjustments['humidity'] = 0.02
            elif humidity < 30:
                adjustments['humidity'] = -0.02

            # Wind adjustments
            if wind_speed >= 7:
                wind_dir = self.degrees_to_compass(wind_deg)
                wind_impact = self.get_wind_impact(wind_dir, stadium['homeDirection'])
                adjustments['wind'] = 0.10 if wind_impact['impact'] == 'positive' else -0.10

            # Air pressure adjustment
            pressure_inhg = pressure * 0.02953
            if pressure_inhg < 29.80:
                adjustments['air_pressure'] = 0.03

            # Rain adjustment
            if rain_threat:
                adjustments['rain'] = 0.05

        return sum(adjustments.values())

    def adjust_game(self, game_data):
        """Process a single game's data"""
        try:
            home_abbr = game_data['home_abbr']
            prediction = game_data['prediction']
            
            # Extract scores from nested structure
            final_scores = prediction['pitching_adjustment']['pitcher_adjustments']['final_scores']
            home_runs = float(final_scores['home_runs'])
            away_runs = float(final_scores['away_runs'])

            # Get stadium data
            stadium = self.find_stadium_by_team(home_abbr)
            if not stadium:
                raise ValueError(f"Stadium not found for {home_abbr}")

            # Get weather data
            weather_data = self.get_weather_data(stadium['lat'], stadium['lon'])
            if not weather_data:
                raise ValueError("Failed to fetch weather data")

            # Calculate adjustment
            adjustment = self.calculate_score_adjustment(stadium, weather_data)

            # Build weather description
            weather_desc = (
                f"{weather_data['weather'][0]['main']} "
                f"({weather_data['main']['temp']}°F, "
                f"{weather_data['wind']['speed']}mph "
                f"{self.degrees_to_compass(weather_data['wind'].get('deg'))})"
            )

            return {
                "game_time": game_data['game_time'],
                "home_team": game_data['home_team'],
                "away_team": game_data['away_team'],
                "original_home": home_runs,
                "original_away": away_runs,
                "adjusted_home": home_runs * adjustment,
                "adjusted_away": away_runs * adjustment,
                "weather_impact": weather_desc,
                "error": None
            }
        except Exception as e:
            return {
                "game_time": game_data.get('game_time', 'Unknown'),
                "home_team": game_data.get('home_team', 'Unknown'),
                "error": str(e)
            }
        
        