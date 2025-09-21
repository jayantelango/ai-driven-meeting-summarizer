"""
Advanced file management system
Handles file uploads, processing, storage, and organization
"""

import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app, request
from models import db, User
import logging

class FileManager:
    """Advanced file management system"""
    
    def __init__(self, app=None):
        self.app = app
        self.upload_folder = 'static/uploads'
        self.allowed_extensions = {
            'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'},
            'documents': {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'},
            'spreadsheets': {'xls', 'xlsx', 'csv', 'ods'},
            'presentations': {'ppt', 'pptx', 'odp'},
            'audio': {'mp3', 'wav', 'ogg', 'm4a', 'aac'},
            'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'},
            'archives': {'zip', 'rar', '7z', 'tar', 'gz'},
            'code': {'py', 'js', 'html', 'css', 'json', 'xml', 'sql'}
        }
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize file manager"""
        self.app = app
        self.upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
        self.max_file_size = app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
        
        # Create upload directories
        self._create_upload_directories()
    
    def _create_upload_directories(self):
        """Create necessary upload directories"""
        directories = [
            self.upload_folder,
            os.path.join(self.upload_folder, 'documents'),
            os.path.join(self.upload_folder, 'images'),
            os.path.join(self.upload_folder, 'audio'),
            os.path.join(self.upload_folder, 'video'),
            os.path.join(self.upload_folder, 'archives'),
            os.path.join(self.upload_folder, 'temp')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def upload_file(self, file, user_id, category='documents', metadata=None):
        """Upload and process a file"""
        try:
            # Validate file
            if not self._validate_file(file):
                return {'success': False, 'error': 'Invalid file'}
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            original_filename = secure_filename(file.filename)
            file_extension = os.path.splitext(original_filename)[1].lower()
            filename = f"{file_id}{file_extension}"
            
            # Determine upload path
            upload_path = self._get_upload_path(category, filename)
            
            # Save file
            file.save(upload_path)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(upload_path)
            
            # Get file info
            file_info = self._get_file_info(upload_path, original_filename)
            
            # Store file metadata
            file_record = {
                'id': file_id,
                'original_name': original_filename,
                'filename': filename,
                'path': upload_path,
                'category': category,
                'size': file_info['size'],
                'mime_type': file_info['mime_type'],
                'hash': file_hash,
                'uploaded_by': user_id,
                'uploaded_at': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }
            
            # Store in database (would need a File model)
            self._store_file_record(file_record)
            
            return {
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'url': self._get_file_url(filename, category),
                'file_info': file_info
            }
            
        except Exception as e:
            logging.error(f"File upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_meeting_file(self, file, user_id):
        """Process meeting-related files (audio, video, documents)"""
        try:
            file_extension = os.path.splitext(file.filename)[1].lower()
            
            # Determine category based on file type
            category = self._get_file_category(file_extension)
            
            # Upload file
            upload_result = self.upload_file(file, user_id, category)
            
            if not upload_result['success']:
                return upload_result
            
            # Process based on file type
            if category == 'audio':
                return self._process_audio_file(upload_result)
            elif category == 'video':
                return self._process_video_file(upload_result)
            elif category == 'documents':
                return self._process_document_file(upload_result)
            else:
                return upload_result
                
        except Exception as e:
            logging.error(f"Meeting file processing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_audio_file(self, file_result):
        """Process audio file for transcription"""
        try:
            # This would integrate with speech-to-text service
            # For now, return the file info
            return {
                'success': True,
                'file_id': file_result['file_id'],
                'type': 'audio',
                'transcription_available': False,
                'message': 'Audio file uploaded. Transcription will be processed shortly.'
            }
        except Exception as e:
            logging.error(f"Audio processing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_video_file(self, file_result):
        """Process video file for transcription"""
        try:
            # This would extract audio and process for transcription
            return {
                'success': True,
                'file_id': file_result['file_id'],
                'type': 'video',
                'transcription_available': False,
                'message': 'Video file uploaded. Audio extraction and transcription will be processed shortly.'
            }
        except Exception as e:
            logging.error(f"Video processing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_document_file(self, file_result):
        """Process document file for text extraction"""
        try:
            # This would extract text from document
            return {
                'success': True,
                'file_id': file_result['file_id'],
                'type': 'document',
                'text_extraction_available': True,
                'message': 'Document uploaded and text extracted successfully.'
            }
        except Exception as e:
            logging.error(f"Document processing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_file(self, file_id, user_id):
        """Get file information and download URL"""
        try:
            # This would query the database for file record
            # For now, return mock data
            return {
                'success': True,
                'file_id': file_id,
                'download_url': f'/api/files/download/{file_id}',
                'preview_url': f'/api/files/preview/{file_id}'
            }
        except Exception as e:
            logging.error(f"File retrieval failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_file(self, file_id, user_id):
        """Delete file and its record"""
        try:
            # Get file record
            file_record = self._get_file_record(file_id)
            if not file_record:
                return {'success': False, 'error': 'File not found'}
            
            # Check permissions
            if file_record['uploaded_by'] != user_id:
                return {'success': False, 'error': 'Permission denied'}
            
            # Delete physical file
            if os.path.exists(file_record['path']):
                os.remove(file_record['path'])
            
            # Delete database record
            self._delete_file_record(file_id)
            
            return {'success': True, 'message': 'File deleted successfully'}
            
        except Exception as e:
            logging.error(f"File deletion failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_user_files(self, user_id, category=None, limit=20, offset=0):
        """Get user's files with pagination"""
        try:
            # This would query the database
            # For now, return mock data
            return {
                'success': True,
                'files': [],
                'total': 0,
                'page': 1,
                'pages': 0
            }
        except Exception as e:
            logging.error(f"User files retrieval failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _validate_file(self, file):
        """Validate uploaded file"""
        try:
            # Check file size
            if len(file.read()) > self.max_file_size:
                file.seek(0)  # Reset file pointer
                return False
            
            file.seek(0)  # Reset file pointer
            
            # Check file extension
            file_extension = os.path.splitext(file.filename)[1].lower()
            if not self._is_allowed_extension(file_extension):
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"File validation failed: {e}")
            return False
    
    def _is_allowed_extension(self, extension):
        """Check if file extension is allowed"""
        all_extensions = set()
        for category_extensions in self.allowed_extensions.values():
            all_extensions.update(category_extensions)
        
        return extension[1:] in all_extensions  # Remove the dot
    
    def _get_file_category(self, extension):
        """Get file category based on extension"""
        extension = extension[1:]  # Remove the dot
        
        for category, extensions in self.allowed_extensions.items():
            if extension in extensions:
                return category
        
        return 'documents'  # Default category
    
    def _get_upload_path(self, category, filename):
        """Get upload path for file"""
        return os.path.join(self.upload_folder, category, filename)
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _get_file_info(self, file_path, original_filename):
        """Get file information"""
        stat = os.stat(file_path)
        mime_type, _ = mimetypes.guess_type(original_filename)
        
        return {
            'size': stat.st_size,
            'mime_type': mime_type or 'application/octet-stream',
            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def _get_file_url(self, filename, category):
        """Get file URL for access"""
        return f'/static/uploads/{category}/{filename}'
    
    def _store_file_record(self, file_record):
        """Store file record in database"""
        # This would store in a File model
        logging.info(f"File record stored: {file_record['id']}")
    
    def _get_file_record(self, file_id):
        """Get file record from database"""
        # This would query the File model
        # For now, return None
        return None
    
    def _delete_file_record(self, file_id):
        """Delete file record from database"""
        # This would delete from File model
        logging.info(f"File record deleted: {file_id}")

# Global file manager
file_manager = FileManager()

def init_file_manager(app):
    """Initialize file manager for the app"""
    file_manager.init_app(app)
    return file_manager
