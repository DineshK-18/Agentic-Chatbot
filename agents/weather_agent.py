# agents/weather_agent.py - Weather Intelligence Agent
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class WeatherAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
        
    def get_weather(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get weather data for location and date"""
        try:
            # Get coordinates for location
            coords = self._get_coordinates(location)
            if not coords:
                return {"error": f"Could not find location: {location}"}
            
            lat, lon = coords['lat'], coords['lon']
            
            # Make API call to One Call API 3.0
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'exclude': 'minutely,alerts'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            
            # Process based on date
            if date == 'today':
                return self._process_current_weather(weather_data, location)
            elif date == 'tomorrow':
                return self._process_tomorrow_weather(weather_data, location)
            elif date == 'yesterday':
                return self._process_historical_weather(lat, lon, location)
            else:
                return self._process_current_weather(weather_data, location)
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get latitude and longitude for location"""
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'limit': 1
            }
            response = requests.get(self.geocode_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return {
                    'lat': data[0]['lat'],
                    'lon': data[0]['lon']
                }
        except:
            # Fallback to predefined coordinates
            predefined = {
                'chennai': {'lat': 13.0827, 'lon': 80.2707},
                'bengaluru': {'lat': 12.9716, 'lon': 77.5946},
                'london': {'lat': 51.5074, 'lon': -0.1278},
                'mumbai': {'lat': 19.0760, 'lon': 72.8777},
                'delhi': {'lat': 28.7041, 'lon': 77.1025}
            }
            return predefined.get(location.lower())
        
        return None
    
    def _process_current_weather(self, data: Dict, location: str) -> Dict[str, Any]:
        """Process current weather data"""
        current = data.get('current', {})
        
        return {
            "location": location,
            "date": "today",
            "temperature": current.get('temp'),
            "feels_like": current.get('feels_like'),
            "humidity": current.get('humidity'),
            "pressure": current.get('pressure'),
            "wind_speed": current.get('wind_speed'),
            "description": current.get('weather', [{}])[0].get('description', ''),
            "main": current.get('weather', [{}])[0].get('main', ''),
            "icon": current.get('weather', [{}])[0].get('icon', ''),
            "timestamp": datetime.fromtimestamp(current.get('dt')).isoformat()
        }
    
    def _process_tomorrow_weather(self, data: Dict, location: str) -> Dict[str, Any]:
        """Process tomorrow's weather forecast"""
        daily = data.get('daily', [])
        
        if len(daily) > 1:
            tomorrow = daily[1]
            return {
                "location": location,
                "date": "tomorrow",
                "temperature": {
                    "min": tomorrow.get('temp', {}).get('min'),
                    "max": tomorrow.get('temp', {}).get('max'),
                    "day": tomorrow.get('temp', {}).get('day'),
                    "night": tomorrow.get('temp', {}).get('night')
                },
                "humidity": tomorrow.get('humidity'),
                "pressure": tomorrow.get('pressure'),
                "wind_speed": tomorrow.get('wind_speed'),
                "description": tomorrow.get('weather', [{}])[0].get('description', ''),
                "main": tomorrow.get('weather', [{}])[0].get('main', ''),
                "pop": tomorrow.get('pop', 0),  # Probability of precipitation
                "rain": tomorrow.get('rain', 0),
                "snow": tomorrow.get('snow', 0),
                "timestamp": datetime.fromtimestamp(tomorrow.get('dt')).isoformat()
            }
        
        return {"error": "Could not get tomorrow's forecast"}
    
    def _process_historical_weather(self, lat: float, lon: float, location: str) -> Dict[str, Any]:
        """Process historical weather data (simulated for demo)"""
        # Note: Historical data requires paid subscription in OpenWeather
        # This is a simulation for demonstration
        yesterday = datetime.now() - timedelta(days=1)
        
        return {
            "location": location,
            "date": "yesterday",
            "temperature": 28.5,
            "humidity": 65,
            "pressure": 1013,
            "wind_speed": 12.5,
            "description": "Partly cloudy",
            "main": "Clouds",
            "note": "Historical weather simulation - requires paid subscription for real data",
            "timestamp": yesterday.isoformat()
        }
    
    def is_good_weather(self, weather_data: Dict[str, Any]) -> bool:
        """Determine if weather is good based on conditions"""
        try:
            main = weather_data.get('main', '').lower()
            description = weather_data.get('description', '').lower()
            
            # Bad weather conditions
            bad_conditions = ['rain', 'storm', 'thunderstorm', 'snow', 'extreme']
            
            for condition in bad_conditions:
                if condition in main or condition in description:
                    return False
            
            # Check precipitation probability
            pop = weather_data.get('pop', 0)
            if pop > 0.3:  # More than 30% chance of precipitation
                return False
            
            # Check wind speed
            wind_speed = weather_data.get('wind_speed', 0)
            if wind_speed > 20:  # Too windy
                return False
            
            return True
            
        except:
            return True  # Default to good weather if can't determine