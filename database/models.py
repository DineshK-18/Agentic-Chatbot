# database/models.py - FIXED version
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from datetime import datetime
from database.db import Base

class Meeting(Base):
    """Meeting model for scheduling agent"""
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, default="Team Meeting")
    location = Column(String(100), nullable=False, default="Office")
    scheduled_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    participants = Column(JSON, default=list)
    weather_conditions = Column(JSON, nullable=True)
    weather_decision = Column(String(50), nullable=True)  # "good" or "bad"
    status = Column(String(50), default="scheduled")  # scheduled, cancelled, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "location": self.location,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "participants": self.participants or [],
            "weather_conditions": self.weather_conditions,
            "weather_decision": self.weather_decision,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Conversation(Base):
    """Conversation history model"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), index=True, nullable=True)
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    agent_type = Column(String(50), nullable=False)  # weather, document, scheduling, database
    confidence = Column(Integer, default=0)  # 0-100
    extra_data = Column(JSON, nullable=True)  # Changed from 'metadata' to 'extra_data'
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user_message": self.user_message,
            "agent_response": self.agent_response,
            "agent_type": self.agent_type,
            "confidence": self.confidence,
            "extra_data": self.extra_data,  # Updated field name
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }