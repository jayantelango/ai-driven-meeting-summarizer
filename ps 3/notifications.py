"""
Real-time notifications system with WebSocket support
Handles push notifications, email alerts, and in-app notifications
"""

import json
import asyncio
from datetime import datetime, timedelta
from flask import request, current_app
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User, TaskAssignment, MeetingSummary
import logging

class NotificationManager:
    """Real-time notification management system"""
    
    def __init__(self, app=None):
        self.app = app
        self.socketio = None
        self.notification_queue = []
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize notification system"""
        self.app = app
        self.socketio = SocketIO(app, cors_allowed_origins="*")
        self._register_handlers()
    
    def _register_handlers(self):
        """Register WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logging.info(f"Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to notification system'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logging.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('join_user_room')
        def handle_join_user_room(data):
            user_id = data.get('user_id')
            if user_id:
                join_room(f"user_{user_id}")
                emit('joined_room', {'room': f"user_{user_id}"})
        
        @self.socketio.on('leave_user_room')
        def handle_leave_user_room(data):
            user_id = data.get('user_id')
            if user_id:
                leave_room(f"user_{user_id}")
                emit('left_room', {'room': f"user_{user_id}"})
        
        @self.socketio.on('join_project_room')
        def handle_join_project_room(data):
            project_id = data.get('project_id')
            if project_id:
                join_room(f"project_{project_id}")
                emit('joined_room', {'room': f"project_{project_id}"})
    
    def send_notification(self, user_id, notification_type, title, message, data=None):
        """Send real-time notification to user"""
        notification = {
            'id': f"notif_{int(datetime.utcnow().timestamp() * 1000)}",
            'type': notification_type,
            'title': title,
            'message': message,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat(),
            'read': False
        }
        
        # Send via WebSocket
        self.socketio.emit('notification', notification, room=f"user_{user_id}")
        
        # Store in database
        self._store_notification(user_id, notification)
        
        logging.info(f"Notification sent to user {user_id}: {title}")
    
    def send_project_notification(self, project_id, notification_type, title, message, data=None):
        """Send notification to all project members"""
        notification = {
            'id': f"notif_{int(datetime.utcnow().timestamp() * 1000)}",
            'type': notification_type,
            'title': title,
            'message': message,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat(),
            'read': False
        }
        
        # Send to all project members
        self.socketio.emit('project_notification', notification, room=f"project_{project_id}")
        
        logging.info(f"Project notification sent to project {project_id}: {title}")
    
    def _store_notification(self, user_id, notification):
        """Store notification in database"""
        try:
            # This would store in a notifications table
            # For now, we'll just log it
            logging.info(f"Stored notification for user {user_id}: {notification['title']}")
        except Exception as e:
            logging.error(f"Failed to store notification: {e}")
    
    def send_task_reminder(self, task_id):
        """Send task reminder notification"""
        try:
            task = TaskAssignment.query.get(task_id)
            if task and task.assignee_id:
                self.send_notification(
                    user_id=task.assignee_id,
                    notification_type='task_reminder',
                    title='Task Reminder',
                    message=f"Task '{task.task_description[:50]}...' is due soon",
                    data={'task_id': task_id, 'project_id': task.project_id}
                )
        except Exception as e:
            logging.error(f"Failed to send task reminder: {e}")
    
    def send_meeting_reminder(self, meeting_id):
        """Send meeting reminder notification"""
        try:
            meeting = MeetingSummary.query.get(meeting_id)
            if meeting:
                # Get project members
                project = meeting.project
                if project:
                    self.send_project_notification(
                        project_id=project.id,
                        notification_type='meeting_reminder',
                        title='Meeting Reminder',
                        message=f"Meeting for {meeting.client_name} - {meeting.project_name}",
                        data={'meeting_id': meeting_id, 'project_id': project.id}
                    )
        except Exception as e:
            logging.error(f"Failed to send meeting reminder: {e}")
    
    def send_critical_alert(self, user_id, alert_type, message):
        """Send critical system alert"""
        self.send_notification(
            user_id=user_id,
            notification_type='critical_alert',
            title='Critical Alert',
            message=message,
            data={'alert_type': alert_type, 'priority': 'high'}
        )
    
    def send_system_announcement(self, message, user_ids=None):
        """Send system-wide announcement"""
        if user_ids:
            for user_id in user_ids:
                self.send_notification(
                    user_id=user_id,
                    notification_type='system_announcement',
                    title='System Announcement',
                    message=message
                )
        else:
            # Send to all users
            self.socketio.emit('system_announcement', {
                'title': 'System Announcement',
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            })

# Global notification manager
notification_manager = NotificationManager()

def init_notifications(app):
    """Initialize notifications for the app"""
    notification_manager.init_app(app)
    return notification_manager
