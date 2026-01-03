# tools/weather_tool.py
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
import httpx

load_dotenv(Path(__file__).parent.parent / '.env')

class WeatherTool:
    """Weather Intelligence Agent - Uses OpenWeather API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geocode_url = "http://api.openweathermap.org/geo/1.0/direct"
        
        # Mock data for when API key is not available
        self.mock_data = {
            "chennai": {"temp": 32, "humidity": 70, "condition": "Partly cloudy"},
            "bengaluru": {"temp": 28, "humidity": 65, "condition": "Sunny"},
            "london": {"temp": 15, "humidity": 80, "condition": "Cloudy"},
            "mumbai": {"temp": 30, "humidity": 75, "condition": "Humid"},
            "delhi": {"temp": 35, "humidity": 60, "condition": "Clear"}
        }
    
    def get_weather(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get weather data for location and date"""
        try:
            # For demo purposes, use mock data if no API key
            if not self.api_key or self.api_key == "your_api_key_here_register_at_openweathermap.org":
                return self._get_mock_weather(location, date)
            
            # Get coordinates
            coords = self._get_coordinates(location)
            if not coords:
                return {"error": f"Location '{location}' not found"}
            
            lat, lon = coords['lat'], coords['lon']
            
            # Determine which API endpoint to use based on date
            if date in ['today', None]:
                return self._get_current_weather(lat, lon, location)
            elif date == 'tomorrow':
                return self._get_forecast(lat, lon, location, days=1)
            elif date == 'yesterday':
                return self._get_historical_weather(lat, lon, location)
            else:
                return self._get_current_weather(lat, lon, location)
                
        except Exception as e:
            return {"error": f"Weather API error: {str(e)}", "location": location}
    
    def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get latitude and longitude for location"""
        try:
            if not self.api_key:
                return self._get_mock_coordinates(location)
            
            params = {
                'q': location,
                'appid': self.api_key,
                'limit': 1
            }
            
            response = requests.get(self.geocode_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return {
                    'lat': data[0]['lat'],
                    'lon': data[0]['lon'],
                    'name': data[0].get('name', location)
                }
        except:
            pass
        
        return self._get_mock_coordinates(location)
    
    def _get_current_weather(self, lat: float, lon: float, location: str) -> Dict[str, Any]:
        """Get current weather data"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(f"{self.base_url}/weather", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                "location": location,
                "date": "today",
                "temperature": data['main']['temp'],
                "feels_like": data['main']['feels_like'],
                "humidity": data['main']['humidity'],
                "pressure": data['main']['pressure'],
                "wind_speed": data['wind']['speed'],
                "conditions": data['weather'][0]['description'],
                "main": data['weather'][0]['main'],
                "icon": data['weather'][0]['icon'],
                "timestamp": datetime.now().isoformat(),
                "source": "openweathermap"
            }
        except Exception as e:
            return self._get_mock_weather(location, "today")
    
    def _get_forecast(self, lat: float, lon: float, location: str, days: int = 1) -> Dict[str, Any]:
        """Get weather forecast"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': 40  # 5 days * 8 intervals per day
            }
            
            response = requests.get(f"{self.base_url}/forecast", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Get tomorrow's forecast (index 8 for 24 hours ahead, 3-hour intervals)
            tomorrow_index = min(8, len(data['list']) - 1)
            forecast = data['list'][tomorrow_index]
            
            return {
                "location": location,
                "date": "tomorrow",
                "temperature": forecast['main']['temp'],
                "feels_like": forecast['main']['feels_like'],
                "humidity": forecast['main']['humidity'],
                "pressure": forecast['main']['pressure'],
                "wind_speed": forecast['wind']['speed'],
                "conditions": forecast['weather'][0]['description'],
                "main": forecast['weather'][0]['main'],
                "pop": forecast.get('pop', 0),  # Probability of precipitation
                "timestamp": datetime.fromtimestamp(forecast['dt']).isoformat(),
                "source": "openweathermap"
            }
        except Exception as e:
            return self._get_mock_weather(location, "tomorrow")
    
    def _get_historical_weather(self, lat: float, lon: float, location: str) -> Dict[str, Any]:
        """Get historical weather data (simulated)"""
        yesterday = datetime.now() - timedelta(days=1)
        
        return {
            "location": location,
            "date": "yesterday",
            "temperature": 28.5,
            "humidity": 65,
            "pressure": 1013,
            "wind_speed": 12.5,
            "conditions": "Partly cloudy",
            "main": "Clouds",
            "note": "Historical weather simulation",
            "timestamp": yesterday.isoformat(),
            "source": "simulation"
        }
    
    def _get_mock_coordinates(self, location: str) -> Dict[str, float]:
        """Get mock coordinates for common locations"""
        locations = {
            "chennai": {"lat": 13.0827, "lon": 80.2707, "name": "Chennai"},
            "bengaluru": {"lat": 12.9716, "lon": 77.5946, "name": "Bengaluru"},
            "london": {"lat": 51.5074, "lon": -0.1278, "name": "London"},
            "mumbai": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai"},
            "delhi": {"lat": 28.7041, "lon": 77.1025, "name": "Delhi"}
        }
        
        location_lower = location.lower()
        for key, value in locations.items():
            if key in location_lower:
                return value
        
        # Default to Chennai
        return locations["chennai"]
    
    def _get_mock_weather(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get mock weather data for demo"""
        location_lower = location.lower()
        
        # Find matching location
        for key, data in self.mock_data.items():
            if key in location_lower:
                temp = data["temp"]
                humidity = data["humidity"]
                condition = data["condition"]
                break
        else:
            # Default values
            temp = 25
            humidity = 65
            condition = "Clear"
        
        # Adjust for date
        if date == "tomorrow":
            temp += 2  # Slightly warmer tomorrow
            condition = "Mostly sunny"
        elif date == "yesterday":
            temp -= 1  # Slightly cooler yesterday
            condition = "Partly cloudy"
        
        return {
            "location": location,
            "date": date or "today",
            "temperature": temp,
            "humidity": humidity,
            "pressure": 1013,
            "wind_speed": 12.5,
            "conditions": condition,
            "main": condition.split()[0],
            "icon": "01d" if "sunny" in condition.lower() or "clear" in condition.lower() else "04d",
            "timestamp": datetime.now().isoformat(),
            "source": "mock_data",
            "note": "Using mock data. Add OpenWeather API key for real weather data."
        }
    
    def is_good_weather(self, weather_data: Dict[str, Any]) -> bool:
        """Determine if weather is good for meetings"""
        try:
            if "error" in weather_data:
                return True  # Default to good if we can't get weather
            
            conditions = weather_data.get("conditions", "").lower()
            main = weather_data.get("main", "").lower()
            
            # Bad weather conditions
            bad_conditions = ["rain", "storm", "thunderstorm", "snow", "extreme", "heavy"]
            
            for condition in bad_conditions:
                if condition in conditions or condition in main:
                    return False
            
            # Check temperature range (comfortable range: 15-30°C)
            temp = weather_data.get("temperature", 25)
            if isinstance(temp, (int, float)):
                if temp < 10 or temp > 35:
                    return False
            
            # Check wind speed
            wind_speed = weather_data.get("wind_speed", 0)
            if isinstance(wind_speed, (int, float)) and wind_speed > 20:
                return False
            
            return True
            
        except:
            return True  # Default to good weather if error
    
    def check_status(self) -> str:
        """Check weather service status"""
        if self.api_key and self.api_key != "your_api_key_here_register_at_openweathermap.org":
            return "connected"
        return "mock_mode"