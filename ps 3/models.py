from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and authorization"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    projects = db.relationship('Project', backref='created_by_user', lazy=True)
    tasks_created = db.relationship('TaskAssignment', foreign_keys='TaskAssignment.created_by', backref='creator', lazy=True)
    tasks_assigned = db.relationship('TaskAssignment', foreign_keys='TaskAssignment.assignee_id', backref='assignee', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

class Role(db.Model):
    """Role model for role-based access control"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON)  # Store permissions as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat()
        }

class UserRole(db.Model):
    """Many-to-many relationship between users and roles"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id', name='unique_user_role'),)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    client = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    summaries = db.relationship('MeetingSummary', backref='project', lazy=True)
    tasks = db.relationship('TaskAssignment', backref='project', lazy=True)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'client': self.client}

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tasks = db.relationship('TaskAssignment', backref='assignee', lazy=True)
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'role': self.role, 'email': self.email}

class MeetingSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transcript = db.Column(db.Text, nullable=False)
    ai_result = db.Column(db.JSON, nullable=False)
    meeting_type = db.Column(db.String(50), default="General")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    tasks = db.relationship('TaskAssignment', backref='meeting', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id, 
            'ai_result': self.ai_result, 
            'created_at': self.created_at.isoformat(),
            'meeting_type': self.meeting_type,
            'project_id': self.project_id
        }

class TaskAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting_summary.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('team_member.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.DateTime)
    completion_notes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id, 
            'task_description': self.task_description,
            'priority': self.priority,
            'status': self.status,
            'assignee': self.assignee.name if self.assignee else 'Unassigned',
            'assignee_id': self.assignee_id,
            'project_id': self.project_id,
            'meeting_id': self.meeting_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class MeetingTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # 'sales', 'project', 'client', 'internal'
    description = db.Column(db.Text, nullable=True)
    default_prompt = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_type': self.template_type,
            'description': self.description,
            'default_prompt': self.default_prompt,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }