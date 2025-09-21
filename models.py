from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    client = db.Column(db.String(100), nullable=False)
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'client': self.client}

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'role': self.role, 'email': self.email}

class MeetingSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transcript = db.Column(db.Text, nullable=False)
    ai_result = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    def to_dict(self):
        return {'id': self.id, 'ai_result': self.ai_result, 'created_at': self.created_at.isoformat()}

class TaskAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting_summary.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('team_member.id'))
    assignee = db.relationship('TeamMember', backref='tasks')
    def to_dict(self):
        return {
            'id': self.id,
            'task_description': self.task_description,
            'priority': self.priority,
            'status': self.status,
            'assignee': self.assignee.name if self.assignee else 'Unassigned'
        }

class MeetingTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    default_prompt = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'default_prompt': self.default_prompt}
