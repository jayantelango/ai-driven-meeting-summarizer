"""
Enhanced error handling and user feedback system
Provides comprehensive error handling with user-friendly messages
"""

from flask import jsonify, request, render_template
from werkzeug.exceptions import HTTPException
import logging
import traceback
from datetime import datetime

class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handlers for the Flask app"""
        self.app = app
        
        # Register error handlers
        app.register_error_handler(400, self.handle_bad_request)
        app.register_error_handler(401, self.handle_unauthorized)
        app.register_error_handler(403, self.handle_forbidden)
        app.register_error_handler(404, self.handle_not_found)
        app.register_error_handler(429, self.handle_rate_limit)
        app.register_error_handler(500, self.handle_internal_error)
        app.register_error_handler(Exception, self.handle_generic_error)
        
        # Log all errors
        app.before_request(self.log_request)
        app.after_request(self.log_response)
    
    def log_request(self):
        """Log incoming requests"""
        logging.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
    
    def log_response(self, response):
        """Log outgoing responses"""
        logging.info(f"Response: {response.status_code} for {request.method} {request.path}")
        return response
    
    def handle_bad_request(self, error):
        """Handle 400 Bad Request errors"""
        error_data = {
            'error': 'Bad Request',
            'message': 'The request was invalid or malformed',
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path
        }
        
        # Add specific error details if available
        if hasattr(error, 'description'):
            error_data['details'] = error.description
        
        logging.warning(f"Bad Request: {request.path} - {error_data.get('details', 'No details')}")
        
        if request.is_json:
            return jsonify(error_data), 400
        else:
            return render_template('error.html', 
                                 error_code=400,
                                 error_message="Invalid request. Please check your input and try again."), 400
    
    def handle_unauthorized(self, error):
        """Handle 401 Unauthorized errors"""
        error_data = {
            'error': 'Unauthorized',
            'message': 'Authentication required. Please log in to access this resource.',
            'status_code': 401,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path
        }
        
        logging.warning(f"Unauthorized access attempt: {request.path} from {request.remote_addr}")
        
        if request.is_json:
            return jsonify(error_data), 401
        else:
            return render_template('error.html',
                                 error_code=401,
                                 error_message="Please log in to access this page."), 401
    
    def handle_forbidden(self, error):
        """Handle 403 Forbidden errors"""
        error_data = {
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
            'status_code': 403,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path
        }
        
        logging.warning(f"Forbidden access attempt: {request.path} from {request.remote_addr}")
        
        if request.is_json:
            return jsonify(error_data), 403
        else:
            return render_template('error.html',
                                 error_code=403,
                                 error_message="You don't have permission to access this page."), 403
    
    def handle_not_found(self, error):
        """Handle 404 Not Found errors"""
        error_data = {
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'status_code': 404,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path
        }
        
        logging.info(f"404 Not Found: {request.path}")
        
        if request.is_json:
            return jsonify(error_data), 404
        else:
            return render_template('error.html',
                                 error_code=404,
                                 error_message="The page you're looking for doesn't exist."), 404
    
    def handle_rate_limit(self, error):
        """Handle 429 Rate Limit errors"""
        error_data = {
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please slow down and try again later.',
            'status_code': 429,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path,
            'retry_after': getattr(error, 'retry_after', 60)
        }
        
        logging.warning(f"Rate limit exceeded: {request.path} from {request.remote_addr}")
        
        if request.is_json:
            return jsonify(error_data), 429
        else:
            return render_template('error.html',
                                 error_code=429,
                                 error_message="Too many requests. Please wait a moment and try again."), 429
    
    def handle_internal_error(self, error):
        """Handle 500 Internal Server errors"""
        error_id = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        
        error_data = {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path,
            'error_id': error_id
        }
        
        # Log the full error with traceback
        logging.error(f"Internal Server Error {error_id}: {request.path}")
        logging.error(f"Error: {str(error)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        
        if request.is_json:
            return jsonify(error_data), 500
        else:
            return render_template('error.html',
                                 error_code=500,
                                 error_message="Something went wrong. Please try again later.",
                                 error_id=error_id), 500
    
    def handle_generic_error(self, error):
        """Handle all other exceptions"""
        error_id = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        
        error_data = {
            'error': 'Unexpected Error',
            'message': 'An unexpected error occurred. Please try again later.',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat(),
            'path': request.path,
            'error_id': error_id
        }
        
        # Log the full error
        logging.error(f"Unexpected Error {error_id}: {request.path}")
        logging.error(f"Error: {str(error)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        
        if request.is_json:
            return jsonify(error_data), 500
        else:
            return render_template('error.html',
                                 error_code=500,
                                 error_message="Something went wrong. Please try again later.",
                                 error_id=error_id), 500

# Custom exception classes
class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class AuthenticationError(Exception):
    """Custom authentication error"""
    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)

class AuthorizationError(Exception):
    """Custom authorization error"""
    def __init__(self, message="Access denied"):
        self.message = message
        super().__init__(self.message)

class RateLimitError(Exception):
    """Custom rate limit error"""
    def __init__(self, message="Rate limit exceeded", retry_after=60):
        self.message = message
        self.retry_after = retry_after
        super().__init__(self.message)

# Utility functions for error handling
def handle_validation_error(error):
    """Handle validation errors with specific field information"""
    return jsonify({
        'error': 'Validation Error',
        'message': error.message,
        'field': error.field,
        'status_code': 400,
        'timestamp': datetime.utcnow().isoformat()
    }), 400

def handle_authentication_error(error):
    """Handle authentication errors"""
    return jsonify({
        'error': 'Authentication Error',
        'message': error.message,
        'status_code': 401,
        'timestamp': datetime.utcnow().isoformat()
    }), 401

def handle_authorization_error(error):
    """Handle authorization errors"""
    return jsonify({
        'error': 'Authorization Error',
        'message': error.message,
        'status_code': 403,
        'timestamp': datetime.utcnow().isoformat()
    }), 403

def handle_rate_limit_error(error):
    """Handle rate limit errors"""
    return jsonify({
        'error': 'Rate Limit Error',
        'message': error.message,
        'retry_after': error.retry_after,
        'status_code': 429,
        'timestamp': datetime.utcnow().isoformat()
    }), 429
