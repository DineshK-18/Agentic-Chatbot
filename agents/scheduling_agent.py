# agents/scheduling_agent.py - Meeting Scheduling + Weather Reasoning Agent
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from database.models import Meeting, SessionLocal
from sqlalchemy.orm import Session

class SchedulingAgent:
    def __init__(self, weather_agent):
        self.weather_agent = weather_agent
    
    def schedule_meeting(self, location: str, date: str, 
                         meeting_title: str = "Team Meeting",
                         participants: List[str] = None) -> Dict[str, Any]:
        """Schedule meeting based on weather conditions"""
        try:
            # Get weather for the specified date and location
            weather_data = self.weather_agent.get_weather(location, date)
            
            if 'error' in weather_data:
                return {
                    "status": "error",
                    "message": f"Could not get weather data: {weather_data['error']}"
                }
            
            # Determine if weather is good
            is_good_weather = self.weather_agent.is_good_weather(weather_data)
            
            # Check if meeting already exists
            db = SessionLocal()
            existing_meeting = self._check_existing_meeting(db, date, location, meeting_title)
            
            if existing_meeting:
                db.close()
                return {
                    "status": "exists",
                    "message": f"A meeting '{meeting_title}' is already scheduled for {date} in {location}.",
                    "meeting_id": existing_meeting.id,
                    "weather_decision": "good" if is_good_weather else "bad",
                    "weather_data": weather_data
                }
            
            # Create meeting if weather is good
            if is_good_weather:
                meeting = Meeting(
                    title=meeting_title,
                    location=location,
                    scheduled_date=self._parse_date(date),
                    participants=participants or [],
                    weather_conditions=weather_data,
                    status="scheduled"
                )
                
                db.add(meeting)
                db.commit()
                db.refresh(meeting)
                db.close()
                
                return {
                    "status": "scheduled",
                    "message": f"Meeting '{meeting_title}' scheduled for {date} in {location}.",
                    "meeting_id": meeting.id,
                    "weather_decision": "good",
                    "weather_data": weather_data
                }
            else:
                db.close()
                return {
                    "status": "cancelled",
                    "message": f"Meeting not scheduled due to bad weather in {location} on {date}.",
                    "weather_decision": "bad",
                    "weather_data": weather_data,
                    "reason": self._get_weather_reason(weather_data)
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error scheduling meeting: {str(e)}"
            }
    
    def _check_existing_meeting(self, db: Session, date: str, location: str, title: str) -> Optional[Meeting]:
        """Check if meeting already exists"""
        target_date = self._parse_date(date)
        
        return db.query(Meeting).filter(
            Meeting.title == title,
            Meeting.location == location,
            Meeting.scheduled_date == target_date
        ).first()
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        today = datetime.now().date()
        
        if date_str == 'today':
            return datetime.combine(today, datetime.min.time())
        elif date_str == 'tomorrow':
            tomorrow = today + timedelta(days=1)
            return datetime.combine(tomorrow, datetime.min.time())
        elif date_str == 'yesterday':
            yesterday = today - timedelta(days=1)
            return datetime.combine(yesterday, datetime.min.time())
        else:
            # Try to parse date string
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except:
                # Default to tomorrow
                tomorrow = today + timedelta(days=1)
                return datetime.combine(tomorrow, datetime.min.time())
    
    def _get_weather_reason(self, weather_data: Dict[str, Any]) -> str:
        """Get reason for bad weather"""
        main = weather_data.get('main', '').lower()
        description = weather_data.get('description', '').lower()
        
        if 'rain' in main or 'rain' in description:
            return "High probability of rain"
        elif 'storm' in main or 'storm' in description:
            return "Stormy conditions expected"
        elif 'snow' in main or 'snow' in description:
            return "Snowfall expected"
        elif weather_data.get('wind_speed', 0) > 20:
            return "High wind speeds"
        elif weather_data.get('pop', 0) > 0.3:
            return "High precipitation probability"
        else:
            return "Unfavorable weather conditions"