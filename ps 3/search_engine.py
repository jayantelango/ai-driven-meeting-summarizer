"""
Advanced search and filtering system
Provides full-text search, faceted search, and intelligent filtering
"""

import re
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func, text
from sqlalchemy.orm import joinedload
from models import db, MeetingSummary, TaskAssignment, Project, User, TeamMember
import logging

class SearchEngine:
    """Advanced search and filtering engine"""
    
    def __init__(self):
        self.search_weights = {
            'title': 3.0,
            'content': 2.0,
            'tags': 2.5,
            'client': 1.5,
            'project': 1.5
        }
    
    def search_meetings(self, query, filters=None, user_id=None, limit=20, offset=0):
        """Search meetings with advanced filtering"""
        try:
            # Base query
            search_query = MeetingSummary.query.options(
                joinedload(MeetingSummary.project)
            )
            
            # Apply user filter
            if user_id:
                search_query = search_query.filter(MeetingSummary.created_by == user_id)
            
            # Apply search query
            if query:
                search_conditions = self._build_search_conditions(query, [
                    'client_name', 'project_name', 'summary', 'transcript'
                ])
                search_query = search_query.filter(or_(*search_conditions))
            
            # Apply filters
            if filters:
                search_query = self._apply_filters(search_query, filters, 'meeting')
            
            # Order by relevance and date
            search_query = search_query.order_by(
                MeetingSummary.created_at.desc()
            )
            
            # Pagination
            total = search_query.count()
            results = search_query.offset(offset).limit(limit).all()
            
            return {
                'results': [self._format_meeting_result(meeting) for meeting in results],
                'total': total,
                'page': (offset // limit) + 1,
                'pages': (total + limit - 1) // limit
            }
            
        except Exception as e:
            logging.error(f"Meeting search failed: {e}")
            return {'results': [], 'total': 0, 'page': 1, 'pages': 0}
    
    def search_tasks(self, query, filters=None, user_id=None, limit=20, offset=0):
        """Search tasks with advanced filtering"""
        try:
            # Base query
            search_query = TaskAssignment.query.options(
                joinedload(TaskAssignment.project),
                joinedload(TaskAssignment.assignee)
            )
            
            # Apply user filter
            if user_id:
                search_query = search_query.filter(TaskAssignment.created_by == user_id)
            
            # Apply search query
            if query:
                search_conditions = self._build_search_conditions(query, [
                    'task_description', 'completion_notes'
                ])
                search_query = search_query.filter(or_(*search_conditions))
            
            # Apply filters
            if filters:
                search_query = self._apply_filters(search_query, filters, 'task')
            
            # Order by priority and due date
            search_query = search_query.order_by(
                TaskAssignment.priority.desc(),
                TaskAssignment.due_date.asc()
            )
            
            # Pagination
            total = search_query.count()
            results = search_query.offset(offset).limit(limit).all()
            
            return {
                'results': [self._format_task_result(task) for task in results],
                'total': total,
                'page': (offset // limit) + 1,
                'pages': (total + limit - 1) // limit
            }
            
        except Exception as e:
            logging.error(f"Task search failed: {e}")
            return {'results': [], 'total': 0, 'page': 1, 'pages': 0}
    
    def search_projects(self, query, filters=None, user_id=None, limit=20, offset=0):
        """Search projects with advanced filtering"""
        try:
            # Base query
            search_query = Project.query
            
            # Apply user filter
            if user_id:
                search_query = search_query.filter(Project.created_by == user_id)
            
            # Apply search query
            if query:
                search_conditions = self._build_search_conditions(query, [
                    'name', 'client', 'description'
                ])
                search_query = search_query.filter(or_(*search_conditions))
            
            # Apply filters
            if filters:
                search_query = self._apply_filters(search_query, filters, 'project')
            
            # Order by creation date
            search_query = search_query.order_by(Project.created_at.desc())
            
            # Pagination
            total = search_query.count()
            results = search_query.offset(offset).limit(limit).all()
            
            return {
                'results': [self._format_project_result(project) for project in results],
                'total': total,
                'page': (offset // limit) + 1,
                'pages': (total + limit - 1) // limit
            }
            
        except Exception as e:
            logging.error(f"Project search failed: {e}")
            return {'results': [], 'total': 0, 'page': 1, 'pages': 0}
    
    def global_search(self, query, user_id=None, limit=20):
        """Global search across all entities"""
        try:
            results = {
                'meetings': [],
                'tasks': [],
                'projects': [],
                'users': []
            }
            
            # Search meetings
            meeting_results = self.search_meetings(query, user_id=user_id, limit=5)
            results['meetings'] = meeting_results['results']
            
            # Search tasks
            task_results = self.search_tasks(query, user_id=user_id, limit=5)
            results['tasks'] = task_results['results']
            
            # Search projects
            project_results = self.search_projects(query, user_id=user_id, limit=5)
            results['projects'] = project_results['results']
            
            # Search users (if admin)
            if user_id:
                user = User.query.get(user_id)
                if user and user.role == 'admin':
                    user_results = self.search_users(query, limit=5)
                    results['users'] = user_results['results']
            
            return results
            
        except Exception as e:
            logging.error(f"Global search failed: {e}")
            return {'meetings': [], 'tasks': [], 'projects': [], 'users': []}
    
    def search_users(self, query, limit=20):
        """Search users"""
        try:
            search_query = User.query
            
            if query:
                search_conditions = self._build_search_conditions(query, [
                    'username', 'email'
                ])
                search_query = search_query.filter(or_(*search_conditions))
            
            results = search_query.limit(limit).all()
            
            return {
                'results': [self._format_user_result(user) for user in results],
                'total': search_query.count()
            }
            
        except Exception as e:
            logging.error(f"User search failed: {e}")
            return {'results': [], 'total': 0}
    
    def get_search_suggestions(self, query, entity_type=None):
        """Get search suggestions based on query"""
        try:
            suggestions = []
            
            if not query or len(query) < 2:
                return suggestions
            
            if entity_type == 'meetings' or entity_type is None:
                # Meeting suggestions
                meeting_suggestions = db.session.query(
                    MeetingSummary.client_name,
                    MeetingSummary.project_name
                ).filter(
                    or_(
                        MeetingSummary.client_name.ilike(f'%{query}%'),
                        MeetingSummary.project_name.ilike(f'%{query}%')
                    )
                ).distinct().limit(5).all()
                
                for suggestion in meeting_suggestions:
                    suggestions.append({
                        'text': f"{suggestion.client_name} - {suggestion.project_name}",
                        'type': 'meeting',
                        'category': 'Client/Project'
                    })
            
            if entity_type == 'tasks' or entity_type is None:
                # Task suggestions
                task_suggestions = db.session.query(
                    TaskAssignment.task_description
                ).filter(
                    TaskAssignment.task_description.ilike(f'%{query}%')
                ).distinct().limit(5).all()
                
                for suggestion in task_suggestions:
                    suggestions.append({
                        'text': suggestion.task_description[:50] + '...',
                        'type': 'task',
                        'category': 'Task Description'
                    })
            
            return suggestions[:10]  # Limit to 10 suggestions
            
        except Exception as e:
            logging.error(f"Search suggestions failed: {e}")
            return []
    
    def get_facets(self, entity_type, user_id=None):
        """Get search facets for filtering"""
        try:
            facets = {}
            
            if entity_type == 'meetings':
                # Meeting facets
                facets['clients'] = db.session.query(
                    MeetingSummary.client_name,
                    func.count(MeetingSummary.id).label('count')
                ).group_by(MeetingSummary.client_name).all()
                
                facets['projects'] = db.session.query(
                    MeetingSummary.project_name,
                    func.count(MeetingSummary.id).label('count')
                ).group_by(MeetingSummary.project_name).all()
                
                facets['meeting_types'] = db.session.query(
                    MeetingSummary.meeting_type,
                    func.count(MeetingSummary.id).label('count')
                ).group_by(MeetingSummary.meeting_type).all()
            
            elif entity_type == 'tasks':
                # Task facets
                facets['statuses'] = db.session.query(
                    TaskAssignment.status,
                    func.count(TaskAssignment.id).label('count')
                ).group_by(TaskAssignment.status).all()
                
                facets['priorities'] = db.session.query(
                    TaskAssignment.priority,
                    func.count(TaskAssignment.id).label('count')
                ).group_by(TaskAssignment.priority).all()
                
                facets['projects'] = db.session.query(
                    Project.name,
                    func.count(TaskAssignment.id).label('count')
                ).join(TaskAssignment).group_by(Project.name).all()
            
            elif entity_type == 'projects':
                # Project facets
                facets['clients'] = db.session.query(
                    Project.client,
                    func.count(Project.id).label('count')
                ).group_by(Project.client).all()
                
                facets['statuses'] = db.session.query(
                    Project.status,
                    func.count(Project.id).label('count')
                ).group_by(Project.status).all()
            
            return facets
            
        except Exception as e:
            logging.error(f"Facets retrieval failed: {e}")
            return {}
    
    def _build_search_conditions(self, query, fields):
        """Build search conditions for given fields"""
        conditions = []
        query_terms = self._parse_query(query)
        
        for field in fields:
            for term in query_terms:
                conditions.append(
                    getattr(MeetingSummary, field).ilike(f'%{term}%')
                )
        
        return conditions
    
    def _parse_query(self, query):
        """Parse search query into terms"""
        # Remove special characters and split
        cleaned_query = re.sub(r'[^\w\s]', ' ', query)
        terms = cleaned_query.split()
        
        # Remove duplicates and empty terms
        return list(set(term.lower() for term in terms if term.strip()))
    
    def _apply_filters(self, query, filters, entity_type):
        """Apply filters to query"""
        try:
            for filter_type, filter_value in filters.items():
                if not filter_value:
                    continue
                
                if entity_type == 'meeting':
                    if filter_type == 'client':
                        query = query.filter(MeetingSummary.client_name == filter_value)
                    elif filter_type == 'project':
                        query = query.filter(MeetingSummary.project_name == filter_value)
                    elif filter_type == 'meeting_type':
                        query = query.filter(MeetingSummary.meeting_type == filter_value)
                    elif filter_type == 'date_from':
                        query = query.filter(MeetingSummary.created_at >= filter_value)
                    elif filter_type == 'date_to':
                        query = query.filter(MeetingSummary.created_at <= filter_value)
                
                elif entity_type == 'task':
                    if filter_type == 'status':
                        query = query.filter(TaskAssignment.status == filter_value)
                    elif filter_type == 'priority':
                        query = query.filter(TaskAssignment.priority == filter_value)
                    elif filter_type == 'project_id':
                        query = query.filter(TaskAssignment.project_id == filter_value)
                    elif filter_type == 'assignee_id':
                        query = query.filter(TaskAssignment.assignee_id == filter_value)
                    elif filter_type == 'overdue':
                        if filter_value:
                            query = query.filter(
                                and_(
                                    TaskAssignment.due_date < datetime.utcnow(),
                                    TaskAssignment.status.in_(['pending', 'in_progress'])
                                )
                            )
                
                elif entity_type == 'project':
                    if filter_type == 'client':
                        query = query.filter(Project.client == filter_value)
                    elif filter_type == 'status':
                        query = query.filter(Project.status == filter_value)
                    elif filter_type == 'created_by':
                        query = query.filter(Project.created_by == filter_value)
            
            return query
            
        except Exception as e:
            logging.error(f"Filter application failed: {e}")
            return query
    
    def _format_meeting_result(self, meeting):
        """Format meeting search result"""
        return {
            'id': meeting.id,
            'type': 'meeting',
            'title': f"{meeting.client_name} - {meeting.project_name}",
            'summary': meeting.summary[:200] + '...' if meeting.summary else '',
            'client': meeting.client_name,
            'project': meeting.project_name,
            'created_at': meeting.created_at.isoformat(),
            'meeting_type': meeting.meeting_type
        }
    
    def _format_task_result(self, task):
        """Format task search result"""
        return {
            'id': task.id,
            'type': 'task',
            'title': task.task_description[:100] + '...' if len(task.task_description) > 100 else task.task_description,
            'status': task.status,
            'priority': task.priority,
            'project': task.project.name if task.project else 'Unknown',
            'assignee': task.assignee.name if task.assignee else 'Unassigned',
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'created_at': task.created_at.isoformat()
        }
    
    def _format_project_result(self, project):
        """Format project search result"""
        return {
            'id': project.id,
            'type': 'project',
            'title': project.name,
            'client': project.client,
            'status': project.status,
            'description': project.description[:200] + '...' if project.description and len(project.description) > 200 else project.description or '',
            'created_at': project.created_at.isoformat()
        }
    
    def _format_user_result(self, user):
        """Format user search result"""
        return {
            'id': user.id,
            'type': 'user',
            'title': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        }

# Global search engine
search_engine = SearchEngine()
