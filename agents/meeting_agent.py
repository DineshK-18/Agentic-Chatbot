# app/agents/meeting_agent.py
from sqlalchemy.orm import Session
from app.models.meeting import Meeting
from app.tools.weather_tool import WeatherTool
from datetime import datetime, timedelta

class MeetingAgent:
    def __init__(self, db_session: Session, weather_tool: WeatherTool):
        self.db = db_session
        self.weather_tool = weather_tool
    
    def schedule_meeting_based_on_weather(self, city: str, date: str, 
                                          team: str, description: str) -> Dict:
        # 1. Check weather
        weather = self.weather_tool.get_weather(city, date)
        
        # 2. Decide if weather is good
        is_good_weather = self._evaluate_weather(weather)
        
        if not is_good_weather:
            return {"decision": "cancel", "reason": "Bad weather forecast"}
        
        # 3. Check existing meetings
        existing = self.db.query(Meeting).filter(
            Meeting.date == date,
            Meeting.team == team
        ).first()
        
        if existing:
            return {"decision": "exists", "meeting": existing}
        
        # 4. Create new meeting
        new_meeting = Meeting(
            date=date,
            team=team,
            description=description,
            location=city,
            weather_conditions=weather["conditions"]
        )
        self.db.add(new_meeting)
        self.db.commit()
        
        return {"decision": "scheduled", "meeting": new_meeting}
    
    def _evaluate_weather(self, weather: Dict) -> bool:
        # Simple logic: good if no rain and temperature between 15-30°C
        conditions = weather["conditions"].lower()
        temp = weather["temperature"]
        
        bad_keywords = ["rain", "storm", "snow", "thunder"]
        if any(keyword in conditions for keyword in bad_keywords):
            return False
        if temp < 15 or temp > 30:
            return False
        return True