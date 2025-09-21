"""
Input validation and sanitization module
Handles data validation, sanitization, and security checks
"""

import re
import html
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.utils import secure_filename
import os
from typing import Dict, Any

class InputValidator:
    """Centralized input validation and sanitization"""
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input to prevent XSS and injection attacks"""
        if not text:
            return ""
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # HTML escape to prevent XSS
        text = html.escape(text, quote=True)
        
        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        result = {
            'valid': True,
            'errors': []
        }
        
        if len(password) < 8:
            result['valid'] = False
            result['errors'].append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            result['valid'] = False
            result['errors'].append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            result['valid'] = False
            result['errors'].append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            result['valid'] = False
            result['errors'].append("Password must contain at least one number")
        
        return result
    
    @staticmethod
    def validate_file_upload(file, allowed_extensions=None, max_size_mb=10):
        """Validate file upload"""
        if allowed_extensions is None:
            allowed_extensions = ['.pdf', '.docx', '.txt', '.mp3', '.wav']
        
        result = {
            'valid': True,
            'errors': [],
            'filename': None
        }
        
        if not file or file.filename == '':
            result['valid'] = False
            result['errors'].append("No file selected")
            return result
        
        # Check file extension
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            result['valid'] = False
            result['errors'].append(f"File type not allowed. Allowed: {', '.join(allowed_extensions)}")
            return result
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            result['valid'] = False
            result['errors'].append(f"File too large. Maximum size: {max_size_mb}MB")
            return result
        
        result['filename'] = filename
        return result

# Marshmallow Schemas for API validation
class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=[
        validate.Length(min=3, max=50),
        validate.Regexp(r'^[a-zA-Z0-9_]+$', error="Username can only contain letters, numbers, and underscores")
    ])
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    role = fields.Str(validate=validate.OneOf(['user', 'admin', 'manager']))

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class MeetingSchema(Schema):
    transcript = fields.Str(required=True, validate=[
        validate.Length(min=10, max=50000),
        validate.Regexp(r'^[^<>]*$', error="Transcript contains invalid characters")
    ])
    client_name = fields.Str(required=True, validate=[
        validate.Length(min=2, max=100),
        validate.Regexp(r'^[a-zA-Z0-9\s\-_&.,]+$', error="Client name contains invalid characters")
    ])
    project_name = fields.Str(required=True, validate=[
        validate.Length(min=2, max=100),
        validate.Regexp(r'^[a-zA-Z0-9\s\-_&.,]+$', error="Project name contains invalid characters")
    ])
    template_id = fields.Int(validate=validate.Range(min=1))

class ProjectSchema(Schema):
    name = fields.Str(required=True, validate=[
        validate.Length(min=2, max=100),
        validate.Regexp(r'^[a-zA-Z0-9\s\-_&.,]+$', error="Project name contains invalid characters")
    ])
    client = fields.Str(required=True, validate=[
        validate.Length(min=2, max=100),
        validate.Regexp(r'^[a-zA-Z0-9\s\-_&.,]+$', error="Client name contains invalid characters")
    ])
    description = fields.Str(validate=validate.Length(max=1000))

class TaskSchema(Schema):
    task_description = fields.Str(required=True, validate=[
        validate.Length(min=5, max=1000),
        validate.Regexp(r'^[^<>]*$', error="Task description contains invalid characters")
    ])
    priority = fields.Str(validate=validate.OneOf(['low', 'medium', 'high', 'critical']))
    status = fields.Str(validate=validate.OneOf(['pending', 'in_progress', 'completed', 'cancelled']))
    project_id = fields.Int(required=True, validate=validate.Range(min=1))
    assignee_id = fields.Int(validate=validate.Range(min=1))
    due_date = fields.DateTime(allow_none=True)

class EmailSchema(Schema):
    recipient_email = fields.Email(required=True)
    subject = fields.Str(required=True, validate=[
        validate.Length(min=1, max=200),
        validate.Regexp(r'^[^<>]*$', error="Subject contains invalid characters")
    ])
    message = fields.Str(required=True, validate=[
        validate.Length(min=1, max=5000),
        validate.Regexp(r'^[^<>]*$', error="Message contains invalid characters")
    ])

# Rate limiting configuration
RATE_LIMITS = {
    'api/summarize': {'requests': 10, 'window': 3600},  # 10 requests per hour
    'api/upload': {'requests': 5, 'window': 3600},      # 5 requests per hour
    'api/send-mail': {'requests': 20, 'window': 3600},  # 20 requests per hour
    'api/assistant': {'requests': 30, 'window': 3600},  # 30 requests per hour
    'default': {'requests': 100, 'window': 3600}        # 100 requests per hour
}
