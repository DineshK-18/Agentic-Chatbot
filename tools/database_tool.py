# tools/database_tool.py - Update imports
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session  # Add this import
from sqlalchemy import or_, and_
from database.models import Meeting

class DatabaseTool:
    """Natural Language → Database Query Agent"""
    
    def __init__(self):
        # Patterns for natural language understanding
        self.patterns = {
            'date_keywords': {
                'today': r'\b(today|now|current day)\b',
                'tomorrow': r'\b(tomorrow|next day|day after)\b',
                'yesterday': r'\b(yesterday|previous day|day before)\b',
                'week': r'\b(week|next week|this week|weekly)\b',
                'month': r'\b(month|next month|this month|monthly)\b'
            },
            'action_keywords': {
                'show': r'\b(show|list|display|get|find)\b',
                'count': r'\b(count|how many|number of)\b',
                'check': r'\b(check|verify|do we have|is there)\b',
                'schedule': r'\b(schedule|create|add|plan|book)\b'
            },
            'meeting_keywords': {
                'review': r'\b(review|retrospective|check-in|status)\b',
                'team': r'\b(team|group|department|all hands)\b',
                'client': r'\b(client|customer|partner|external)\b'
            }
        }
    
    def natural_language_query(self, query: str, db: Session) -> Dict[str, Any]:  # Correct type
        """Convert natural language to database query"""
        try:
            query_lower = query.lower()
            
            # Parse query type
            query_type = self._parse_query_type(query_lower)
            
            # Extract parameters
            params = self._extract_parameters(query_lower)
            
            # Execute appropriate query
            if query_type == 'get_meetings':
                result = self._execute_get_meetings(params, db)
            elif query_type == 'count_meetings':
                result = self._execute_count_meetings(params, db)
            elif query_type == 'check_meeting':
                result = self._execute_check_meeting(params, db)
            else:
                result = {"error": "Could not understand query type"}
            
            return {
                "query_type": query_type,
                "parameters": params,
                "result": result,
                "original_query": query,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Query processing error: {str(e)}",
                "original_query": query
            }
    
    def _execute_get_meetings(self, params: Dict[str, Any], db: Session) -> Dict[str, Any]:  # Correct type
        """Execute get meetings query"""
        query = db.query(Meeting)
        
        # Apply date filter
        date_filter = params.get('date_filter', {})
        if 'start' in date_filter and 'end' in date_filter:
            query = query.filter(
                Meeting.scheduled_date >= date_filter['start'],
                Meeting.scheduled_date <= date_filter['end']
            )
        
        # Apply meeting type filter
        meeting_type = params.get('meeting_type')
        if meeting_type == 'review':
            query = query.filter(Meeting.title.ilike('%review%'))
        elif meeting_type == 'team':
            query = query.filter(Meeting.title.ilike('%team%'))
        
        # Apply location filter
        location = params.get('location')
        if location:
            query = query.filter(Meeting.location.ilike(f'%{location}%'))
        
        # Execute query
        meetings = query.order_by(Meeting.scheduled_date.asc()).limit(params.get('limit', 10)).all()
        
        return {
            'count': len(meetings),
            'meetings': [meeting.to_dict() for meeting in meetings],
            'filters_applied': {
                'date_range': date_filter.get('type'),
                'meeting_type': meeting_type,
                'location': location
            }
        }
    
    def _execute_count_meetings(self, params: Dict[str, Any], db: Session) -> Dict[str, Any]:  # Correct type
        """Execute count meetings query"""
        result = self._execute_get_meetings(params, db)
        
        return {
            'count': result['count'],
            'period': params.get('date_filter', {}).get('type', 'all'),
            'meeting_type': params.get('meeting_type', 'all'),
            'location': params.get('location', 'all')
        }
    
    def _execute_check_meeting(self, params: Dict[str, Any], db: Session) -> Dict[str, Any]:  # Correct type
        """Execute check meeting existence query"""
        result = self._execute_get_meetings(params, db)
        
        return {
            'exists': result['count'] > 0,
            'count': result['count'],
            'message': f"{result['count']} meeting(s) found" if result['count'] > 0 else "No meetings found"
        }
    
    def get_meetings(self, db: Session, date: Optional[str] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:  # Correct type
        """Get meetings with optional filters"""
        query = db.query(Meeting)
        
        if date:
            try:
                if date == 'today':
                    target_date = datetime.now().date()
                elif date == 'tomorrow':
                    target_date = datetime.now().date() + timedelta(days=1)
                elif date == 'yesterday':
                    target_date = datetime.now().date() - timedelta(days=1)
                else:
                    target_date = datetime.strptime(date, '%Y-%m-%d').date()
                
                query = query.filter(
                    Meeting.scheduled_date >= datetime.combine(target_date, datetime.min.time()),
                    Meeting.scheduled_date <= datetime.combine(target_date, datetime.max.time())
                )
            except:
                pass
        
        if location:
            query = query.filter(Meeting.location.ilike(f'%{location}%'))
        
        meetings = query.order_by(Meeting.scheduled_date.asc()).all()
        return [meeting.to_dict() for meeting in meetings]
    
    def create_meeting(self, db: Session, meeting_data: Dict[str, Any]) -> Dict[str, Any]:  # Correct type
        """Create a new meeting"""
        try:
            meeting = Meeting(**meeting_data)
            db.add(meeting)
            db.commit()
            db.refresh(meeting)
            
            return {
                "status": "success",
                "message": "Meeting created successfully",
                "meeting": meeting.to_dict()
            }
        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "message": f"Failed to create meeting: {str(e)}"
            }