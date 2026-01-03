# agents/orchestrator.py - Update imports
import re
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session  # Add this import
from database.models import Conversation

class OrchestratorAgent:
    """Main orchestrator that routes queries to appropriate agents"""
    
    def __init__(self, weather_tool, document_tool, database_tool):
        self.weather_tool = weather_tool
        self.document_tool = document_tool
        self.database_tool = database_tool
        
        # Decision patterns
        self.decision_patterns = {
            'weather': [
                r'(weather|temperature|forecast|rain|sunny|cloudy|humidity)',
                r'(today|tomorrow|yesterday)',
                r'(chennai|bengaluru|mumbai|delhi|london|new york|paris)'
            ],
            'document': [
                r'(resume|document|upload|policy|leave|ceo|file|pdf|txt)',
                r'(what is|who is|how many|when is|where is)'
            ],
            'scheduling': [
                r'(schedule|meeting|team|verify|check|create|plan)',
                r'(if|when|check|create|tomorrow|today)'
            ],
            'database': [
                r'(show|list|get|find|search|meetings|appointment)',
                r'(today|tomorrow|week|next|scheduled|planned)'
            ]
        }
    
    def process(self, message: str, conversation_id: Optional[str] = None, 
                db: Optional[Session] = None) -> Dict[str, Any]:  # Correct type annotation
        """Process user message and route to appropriate agent"""
        try:
            # Determine which agent to use
            agent_type = self._determine_agent(message)
            
            # Route to appropriate agent
            if agent_type == 'weather':
                response = self._handle_weather(message)
            elif agent_type == 'document':
                response = self._handle_document(message)
            elif agent_type == 'scheduling':
                response = self._handle_scheduling(message, db)
            elif agent_type == 'database':
                response = self._handle_database(message, db)
            else:
                response = self._handle_general(message)
            
            # Save conversation history if database is available
            if db:
                self._save_conversation(
                    db=db,
                    conversation_id=conversation_id,
                    user_message=message,
                    agent_response=response.get("response", ""),
                    agent_type=agent_type,
                    confidence=response.get("confidence", 0)
                )
            
            # Add metadata
            response.update({
                "agent_used": agent_type,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat(),
                "original_message": message
            })
            
            return response
            
        except Exception as e:
            return {
                "agent": "error",
                "response": f"Sorry, I encountered an error: {str(e)}",
                "confidence": 0,
                "suggestion": "Please try rephrasing your question."
            }
    
    # ... rest of the methods remain the same ...
    
    def schedule_meeting(self, location: str, date: str, title: str = "Team Meeting", 
                        participants: list = None, db: Optional[Session] = None) -> Dict[str, Any]:  # Correct type
        """Schedule a meeting directly"""
        if not db:
            return {"error": "Database connection required"}
        
        return self._handle_scheduling(
            f"Schedule {title} in {location} on {date}", 
            db
        )
    
    def _save_conversation(self, db: Session, conversation_id: str, user_message: str, 
                          agent_response: str, agent_type: str, confidence: int):
        """Save conversation to database"""
        try:
            conversation = Conversation(
                conversation_id=conversation_id,
                user_message=user_message,
                agent_response=agent_response,
                agent_type=agent_type,
                confidence=confidence
            )
            db.add(conversation)
            db.commit()
        except Exception as e:
            db.rollback()
            # Don't raise error - conversation saving is optional
            pass