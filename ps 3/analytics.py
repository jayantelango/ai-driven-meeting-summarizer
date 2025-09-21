"""
Advanced analytics and reporting system
Provides comprehensive insights, trends, and business intelligence
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sqlalchemy import func, extract, and_, or_
from models import db, User, Project, MeetingSummary, TaskAssignment, TeamMember
import logging

class AnalyticsEngine:
    """Advanced analytics and reporting engine"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_dashboard_metrics(self, user_id=None, project_id=None, days=30):
        """Get comprehensive dashboard metrics"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query filters
            filters = []
            if user_id:
                filters.append(MeetingSummary.created_by == user_id)
            if project_id:
                filters.append(MeetingSummary.project_id == project_id)
            
            # Meeting metrics
            meetings_query = MeetingSummary.query.filter(
                and_(
                    MeetingSummary.created_at >= start_date,
                    MeetingSummary.created_at <= end_date,
                    *filters
                )
            )
            
            total_meetings = meetings_query.count()
            meetings_this_week = meetings_query.filter(
                MeetingSummary.created_at >= end_date - timedelta(days=7)
            ).count()
            
            # Task metrics
            tasks_query = TaskAssignment.query
            if user_id:
                tasks_query = tasks_query.filter(TaskAssignment.created_by == user_id)
            if project_id:
                tasks_query = tasks_query.filter(TaskAssignment.project_id == project_id)
            
            total_tasks = tasks_query.count()
            completed_tasks = tasks_query.filter(TaskAssignment.status == 'completed').count()
            pending_tasks = tasks_query.filter(TaskAssignment.status == 'pending').count()
            overdue_tasks = tasks_query.filter(
                and_(
                    TaskAssignment.due_date < end_date,
                    TaskAssignment.status.in_(['pending', 'in_progress'])
                )
            ).count()
            
            # Project metrics
            projects_query = Project.query
            if user_id:
                projects_query = projects_query.filter(Project.created_by == user_id)
            
            total_projects = projects_query.count()
            active_projects = projects_query.filter(Project.status == 'active').count()
            
            # User metrics
            total_users = User.query.count()
            active_users = User.query.filter(User.is_active == True).count()
            
            return {
                'meetings': {
                    'total': total_meetings,
                    'this_week': meetings_this_week,
                    'completion_rate': self._calculate_completion_rate(meetings_query)
                },
                'tasks': {
                    'total': total_tasks,
                    'completed': completed_tasks,
                    'pending': pending_tasks,
                    'overdue': overdue_tasks,
                    'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                },
                'projects': {
                    'total': total_projects,
                    'active': active_projects,
                    'completion_rate': self._calculate_project_completion_rate(projects_query)
                },
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'engagement_rate': self._calculate_user_engagement()
                },
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }
            
        except Exception as e:
            logging.error(f"Failed to get dashboard metrics: {e}")
            return {}
    
    def get_meeting_trends(self, days=30):
        """Get meeting trends and patterns"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Daily meeting counts
            daily_meetings = db.session.query(
                func.date(MeetingSummary.created_at).label('date'),
                func.count(MeetingSummary.id).label('count')
            ).filter(
                MeetingSummary.created_at >= start_date,
                MeetingSummary.created_at <= end_date
            ).group_by(
                func.date(MeetingSummary.created_at)
            ).all()
            
            # Meeting types distribution
            meeting_types = db.session.query(
                MeetingSummary.meeting_type,
                func.count(MeetingSummary.id).label('count')
            ).filter(
                MeetingSummary.created_at >= start_date,
                MeetingSummary.created_at <= end_date
            ).group_by(MeetingSummary.meeting_type).all()
            
            # Client distribution
            client_meetings = db.session.query(
                MeetingSummary.client_name,
                func.count(MeetingSummary.id).label('count')
            ).filter(
                MeetingSummary.created_at >= start_date,
                MeetingSummary.created_at <= end_date
            ).group_by(MeetingSummary.client_name).order_by(
                func.count(MeetingSummary.id).desc()
            ).limit(10).all()
            
            return {
                'daily_trends': [
                    {'date': str(record.date), 'count': record.count}
                    for record in daily_meetings
                ],
                'meeting_types': [
                    {'type': record.meeting_type or 'Unknown', 'count': record.count}
                    for record in meeting_types
                ],
                'top_clients': [
                    {'client': record.client_name, 'meetings': record.count}
                    for record in client_meetings
                ]
            }
            
        except Exception as e:
            logging.error(f"Failed to get meeting trends: {e}")
            return {}
    
    def get_task_analytics(self, user_id=None, project_id=None):
        """Get detailed task analytics"""
        try:
            # Task status distribution
            status_query = TaskAssignment.query
            if user_id:
                status_query = status_query.filter(TaskAssignment.created_by == user_id)
            if project_id:
                status_query = status_query.filter(TaskAssignment.project_id == project_id)
            
            status_distribution = db.session.query(
                TaskAssignment.status,
                func.count(TaskAssignment.id).label('count')
            ).filter(
                status_query.whereclause
            ).group_by(TaskAssignment.status).all()
            
            # Priority distribution
            priority_distribution = db.session.query(
                TaskAssignment.priority,
                func.count(TaskAssignment.id).label('count')
            ).filter(
                status_query.whereclause
            ).group_by(TaskAssignment.priority).all()
            
            # Completion time analysis
            completed_tasks = TaskAssignment.query.filter(
                and_(
                    TaskAssignment.status == 'completed',
                    TaskAssignment.created_at.isnot(None),
                    TaskAssignment.updated_at.isnot(None)
                )
            )
            
            if user_id:
                completed_tasks = completed_tasks.filter(TaskAssignment.created_by == user_id)
            if project_id:
                completed_tasks = completed_tasks.filter(TaskAssignment.project_id == project_id)
            
            avg_completion_time = db.session.query(
                func.avg(
                    func.julianday(TaskAssignment.updated_at) - 
                    func.julianday(TaskAssignment.created_at)
                )
            ).filter(completed_tasks.whereclause).scalar() or 0
            
            return {
                'status_distribution': [
                    {'status': record.status, 'count': record.count}
                    for record in status_distribution
                ],
                'priority_distribution': [
                    {'priority': record.priority, 'count': record.count}
                    for record in priority_distribution
                ],
                'completion_metrics': {
                    'average_completion_days': round(avg_completion_time, 2),
                    'total_completed': completed_tasks.count()
                }
            }
            
        except Exception as e:
            logging.error(f"Failed to get task analytics: {e}")
            return {}
    
    def get_user_productivity(self, user_id, days=30):
        """Get user productivity metrics"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # User's meetings
            user_meetings = MeetingSummary.query.filter(
                and_(
                    MeetingSummary.created_by == user_id,
                    MeetingSummary.created_at >= start_date,
                    MeetingSummary.created_at <= end_date
                )
            )
            
            # User's tasks
            user_tasks = TaskAssignment.query.filter(
                and_(
                    TaskAssignment.created_by == user_id,
                    TaskAssignment.created_at >= start_date,
                    TaskAssignment.created_at <= end_date
                )
            )
            
            # User's projects
            user_projects = Project.query.filter(
                and_(
                    Project.created_by == user_id,
                    Project.created_at >= start_date,
                    Project.created_at <= end_date
                )
            )
            
            return {
                'meetings_created': user_meetings.count(),
                'tasks_created': user_tasks.count(),
                'tasks_completed': user_tasks.filter(TaskAssignment.status == 'completed').count(),
                'projects_created': user_projects.count(),
                'productivity_score': self._calculate_productivity_score(user_id, start_date, end_date)
            }
            
        except Exception as e:
            logging.error(f"Failed to get user productivity: {e}")
            return {}
    
    def get_project_insights(self, project_id):
        """Get detailed project insights"""
        try:
            project = Project.query.get(project_id)
            if not project:
                return {}
            
            # Project meetings
            project_meetings = MeetingSummary.query.filter(
                MeetingSummary.project_id == project_id
            )
            
            # Project tasks
            project_tasks = TaskAssignment.query.filter(
                TaskAssignment.project_id == project_id
            )
            
            # Team members
            team_members = TeamMember.query.filter(
                TeamMember.project_id == project_id
            )
            
            return {
                'project_info': {
                    'name': project.name,
                    'client': project.client,
                    'status': project.status,
                    'created_at': project.created_at.isoformat()
                },
                'meetings': {
                    'total': project_meetings.count(),
                    'recent': project_meetings.filter(
                        MeetingSummary.created_at >= datetime.utcnow() - timedelta(days=7)
                    ).count()
                },
                'tasks': {
                    'total': project_tasks.count(),
                    'completed': project_tasks.filter(TaskAssignment.status == 'completed').count(),
                    'pending': project_tasks.filter(TaskAssignment.status == 'pending').count(),
                    'overdue': project_tasks.filter(
                        and_(
                            TaskAssignment.due_date < datetime.utcnow(),
                            TaskAssignment.status.in_(['pending', 'in_progress'])
                        )
                    ).count()
                },
                'team': {
                    'total_members': team_members.count(),
                    'active_members': team_members.filter(TeamMember.is_active == True).count()
                }
            }
            
        except Exception as e:
            logging.error(f"Failed to get project insights: {e}")
            return {}
    
    def _calculate_completion_rate(self, query):
        """Calculate completion rate for meetings"""
        try:
            total = query.count()
            if total == 0:
                return 0
            # This would be based on meeting status or follow-up completion
            return 85.0  # Mock value
        except:
            return 0
    
    def _calculate_project_completion_rate(self, query):
        """Calculate project completion rate"""
        try:
            total = query.count()
            completed = query.filter(Project.status == 'completed').count()
            return (completed / total * 100) if total > 0 else 0
        except:
            return 0
    
    def _calculate_user_engagement(self):
        """Calculate user engagement rate"""
        try:
            total_users = User.query.count()
            active_users = User.query.filter(
                User.last_login >= datetime.utcnow() - timedelta(days=7)
            ).count()
            return (active_users / total_users * 100) if total_users > 0 else 0
        except:
            return 0
    
    def _calculate_productivity_score(self, user_id, start_date, end_date):
        """Calculate user productivity score"""
        try:
            # This would be a complex calculation based on various factors
            # For now, return a mock score
            return 78.5
        except:
            return 0

# Global analytics engine
analytics_engine = AnalyticsEngine()
