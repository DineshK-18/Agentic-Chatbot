# agents/database_agent.py - Natural Language → Database Query Agent
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database.models import Meeting
import re

class DatabaseAgent:
    def __init__(self):
        # Define patterns for natural language understanding
        self.patterns = {
            'tomorrow': r'(tomorrow|next day|day after)',
            'today': r'(today|current day|now)',
            'week': r'(week|next week|this week|weekly)',
            'all': r'(all|every|list|show)',
            'review': r'(review|retrospective|check-in)',
            'team': r'(team|group|department)',
            'scheduled': r'(scheduled|planned|arranged)'
        }
    
    def process_query(self, query: str, db_session: Session = None) -> Dict[str, Any]:
        """Process natural language query and convert to database query"""
        try:
            # Parse the query
            query_type, params = self._parse_query(query)
            
            # Execute appropriate query
            if query_type == 'get_meetings':
                result = self._get_meetings_query(params, db_session)
            elif query_type == 'check_meeting':
                result = self._check_meeting_query(params, db_session)
            elif query_type == 'count_meetings':
                result = self._count_meetings_query(params, db_session)
            else:
                result = {"error": "Could not understand query"}
            
            return {
                "query_type": query_type,
                "parameters": params,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Query processing error: {str(e)}",
                "query": query
            }
    
    def _parse_query(self, query: str) -> tuple:
        """Parse natural language query"""
        query_lower = query.lower()
        
        # Determine query type
        if re.search(r'(show|list|get|find)', query_lower):
            query_type = 'get_meetings'
        elif re.search(r'(do we have|is there|any meeting)', query_lower):
            query_type = 'check_meeting'
        elif re.search(r'(how many|count|number)', query_lower):
            query_type = 'count_meetings'
        else:
            query_type = 'unknown'
        
        # Extract parameters
        params = {
            'date_filter': self._extract_date_filter(query_lower),
            'meeting_type': self._extract_meeting_type(query_lower),
            'limit': 10
        }
        
        return query_type, params
    
    def _extract_date_filter(self, query: str) -> Dict[str, Any]:
        """Extract date filter from query"""
        today = datetime.now().date()
        
        if re.search(self.patterns['today'], query):
            return {
                'type': 'today',
                'date': today,
                'start_date': datetime.combine(today, datetime.min.time()),
                'end_date': datetime.combine(today, datetime.max.time())
            }
        elif re.search(self.patterns['tomorrow'], query):
            tomorrow = today + timedelta(days=1)
            return {
                'type': 'tomorrow',
                'date': tomorrow,
                'start_date': datetime.combine(tomorrow, datetime.min.time()),
                'end_date': datetime.combine(tomorrow, datetime.max.time())
            }
        elif re.search(self.patterns['week'], query):
            end_date = today + timedelta(days=7)
            return {
                'type': 'week',
                'start_date': datetime.combine(today, datetime.min.time()),
                'end_date': datetime.combine(end_date, datetime.max.time())
            }
        else:
            return {'type': 'all'}
    
    def _extract_meeting_type(self, query: str) -> str:
        """Extract meeting type from query"""
        if re.search(self.patterns['review'], query):
            return 'review'
        elif re.search(self.patterns['team'], query):
            return 'team'
        else:
            return 'any'
    
    def _get_meetings_query(self, params: Dict[str, Any], db_session: Session) -> List[Dict]:
        """Execute get meetings query"""
        query = db_session.query(Meeting)
        
        # Apply date filter
        date_filter = params.get('date_filter', {})
        if date_filter.get('type') == 'today':
            query = query.filter(Meeting.scheduled_date >= date_filter['start_date'],
                                Meeting.scheduled_date <= date_filter['end_date'])
        elif date_filter.get('type') == 'tomorrow':
            query = query.filter(Meeting.scheduled_date >= date_filter['start_date'],
                                Meeting.scheduled_date <= date_filter['end_date'])
        elif date_filter.get('type') == 'week':
            query = query.filter(Meeting.scheduled_date >= date_filter['start_date'],
                                Meeting.scheduled_date <= date_filter['end_date'])
        
        # Apply meeting type filter
        meeting_type = params.get('meeting_type')
        if meeting_type == 'review':
            query = query.filter(Meeting.title.ilike('%review%') | 
                                Meeting.title.ilike('%retro%'))
        elif meeting_type == 'team':
            query = query.filter(Meeting.title.ilike('%team%') | 
                                Meeting.participants.any())
        
        # Execute query
        meetings = query.limit(params.get('limit', 10)).all()
        
        # Convert to dictionaries
        return [
            {
                'id': m.id,
                'title': m.title,
                'location': m.location,
                'scheduled_date': m.scheduled_date.isoformat(),
                'participants': m.participants,
                'status': m.status
            }
            for m in meetings
        ]
    
    def _check_meeting_query(self, params: Dict[str, Any], db_session: Session) -> Dict[str, Any]:
        """Check if meetings exist"""
        meetings = self._get_meetings_query(params, db_session)
        
        return {
            'exists': len(meetings) > 0,
            'count': len(meetings),
            'meetings': meetings
        }
    
    def _count_meetings_query(self, params: Dict[str, Any], db_session: Session) -> Dict[str, Any]:
        """Count meetings"""
        meetings = self._get_meetings_query(params, db_session)
        
        return {
            'count': len(meetings),
            'period': params.get('date_filter', {}).get('type', 'all'),
            'meeting_type': params.get('meeting_type', 'any')
        }
    
    def get_meetings(self, db_session: Session, date: str = None) -> List[Dict]:
        """Get meetings with optional date filter"""
        query = db_session.query(Meeting)
        
        if date:
            try:
                if date == 'today':
                    target_date = datetime.now().date()
                elif date == 'tomorrow':
                    target_date = datetime.now().date() + timedelta(days=1)
                else:
                    target_date = datetime.strptime(date, '%Y-%m-%d').date()
                
                query = query.filter(
                    Meeting.scheduled_date >= datetime.combine(target_date, datetime.min.time()),
                    Meeting.scheduled_date <= datetime.combine(target_date, datetime.max.time())
                )
            except:
                pass
        
        meetings = query.all()
        return [
            {
                'id': m.id,
                'title': m.title,
                'location': m.location,
                'scheduled_date': m.scheduled_date.isoformat(),
                'participants': m.participants,
                'status': m.status
            }
            for m in meetings
        ]