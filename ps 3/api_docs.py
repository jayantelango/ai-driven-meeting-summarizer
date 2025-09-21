"""
Comprehensive API Documentation
Provides detailed API documentation and interactive testing interface
"""

from flask import Blueprint, render_template, jsonify, request
from functools import wraps
import json

api_docs_bp = Blueprint('api_docs', __name__, url_prefix='/api/docs')

def api_endpoint(methods=None, description="", parameters=None, responses=None, auth_required=False):
    """Decorator to document API endpoints"""
    def decorator(f):
        f._api_doc = {
            'methods': methods or ['GET'],
            'description': description,
            'parameters': parameters or [],
            'responses': responses or {},
            'auth_required': auth_required
        }
        return f
    return decorator

# API Documentation Data
API_DOCUMENTATION = {
    'title': 'AI Meeting Summarizer API',
    'version': '2.0.0',
    'description': 'Comprehensive API for AI-powered meeting analysis and management',
    'base_url': '/api',
    'authentication': {
        'type': 'JWT Bearer Token',
        'description': 'Include JWT token in Authorization header: Bearer <token>'
    },
    'endpoints': {
        'authentication': {
            'register': {
                'path': '/auth/register',
                'methods': ['POST'],
                'description': 'Register a new user account',
                'auth_required': False,
                'parameters': [
                    {
                        'name': 'username',
                        'type': 'string',
                        'required': True,
                        'description': 'Unique username (3-50 characters, alphanumeric and underscores only)'
                    },
                    {
                        'name': 'email',
                        'type': 'string',
                        'required': True,
                        'description': 'Valid email address'
                    },
                    {
                        'name': 'password',
                        'type': 'string',
                        'required': True,
                        'description': 'Password (minimum 8 characters, must contain uppercase, lowercase, and number)'
                    },
                    {
                        'name': 'role',
                        'type': 'string',
                        'required': False,
                        'description': 'User role (user, manager, admin)',
                        'default': 'user'
                    }
                ],
                'responses': {
                    '201': {
                        'description': 'User created successfully',
                        'example': {
                            'message': 'User created successfully',
                            'user': {
                                'id': 1,
                                'username': 'john_doe',
                                'email': 'john@example.com',
                                'role': 'user',
                                'is_active': True,
                                'created_at': '2024-01-15T10:30:00Z'
                            }
                        }
                    },
                    '400': {
                        'description': 'Validation error or user already exists',
                        'example': {
                            'error': 'Username already exists'
                        }
                    }
                }
            },
            'login': {
                'path': '/auth/login',
                'methods': ['POST'],
                'description': 'Authenticate user and receive JWT token',
                'auth_required': False,
                'parameters': [
                    {
                        'name': 'username',
                        'type': 'string',
                        'required': True,
                        'description': 'Username or email'
                    },
                    {
                        'name': 'password',
                        'type': 'string',
                        'required': True,
                        'description': 'User password'
                    }
                ],
                'responses': {
                    '200': {
                        'description': 'Login successful',
                        'example': {
                            'message': 'Login successful',
                            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                            'user': {
                                'id': 1,
                                'username': 'john_doe',
                                'role': 'user'
                            }
                        }
                    },
                    '401': {
                        'description': 'Invalid credentials',
                        'example': {
                            'error': 'Invalid credentials'
                        }
                    }
                }
            },
            'me': {
                'path': '/auth/me',
                'methods': ['GET'],
                'description': 'Get current user information',
                'auth_required': True,
                'responses': {
                    '200': {
                        'description': 'User information retrieved',
                        'example': {
                            'user': {
                                'id': 1,
                                'username': 'john_doe',
                                'email': 'john@example.com',
                                'role': 'user',
                                'is_active': True,
                                'created_at': '2024-01-15T10:30:00Z',
                                'last_login': '2024-01-15T14:30:00Z'
                            }
                        }
                    },
                    '401': {
                        'description': 'Authentication required',
                        'example': {
                            'error': 'Token is missing'
                        }
                    }
                }
            }
        },
        'meetings': {
            'summarize': {
                'path': '/summarize',
                'methods': ['POST'],
                'description': 'Analyze meeting transcript and generate summary',
                'auth_required': True,
                'rate_limit': '10 requests per hour',
                'parameters': [
                    {
                        'name': 'transcript',
                        'type': 'string',
                        'required': True,
                        'description': 'Meeting transcript text (10-50,000 characters)'
                    },
                    {
                        'name': 'client_name',
                        'type': 'string',
                        'required': True,
                        'description': 'Client name (2-100 characters)'
                    },
                    {
                        'name': 'project_name',
                        'type': 'string',
                        'required': True,
                        'description': 'Project name (2-100 characters)'
                    },
                    {
                        'name': 'template_id',
                        'type': 'integer',
                        'required': False,
                        'description': 'Meeting template ID for structured analysis'
                    }
                ],
                'responses': {
                    '200': {
                        'description': 'Meeting analysis completed',
                        'example': {
                            'summary': 'Meeting focused on project planning and resource allocation...',
                            'action_items': [
                                'Complete project proposal by Friday',
                                'Schedule follow-up meeting with stakeholders'
                            ],
                            'key_decisions': [
                                'Approved budget increase of 15%',
                                'Decided to use React for frontend development'
                            ],
                            'next_steps': [
                                'Prepare detailed project timeline',
                                'Assign tasks to team members'
                            ],
                            'participants': ['John Doe', 'Jane Smith', 'Bob Johnson'],
                            'sentiment': 'positive',
                            'meeting_type': 'project_planning',
                            'duration_minutes': 45,
                            'project_id': 1,
                            'meeting_id': 123
                        }
                    },
                    '400': {
                        'description': 'Validation error or missing required fields',
                        'example': {
                            'error': 'Please fill in all required fields'
                        }
                    },
                    '503': {
                        'description': 'AI service unavailable',
                        'example': {
                            'error': 'AI service temporarily unavailable. Please try again later.'
                        }
                    }
                }
            },
            'list': {
                'path': '/meetings',
                'methods': ['GET'],
                'description': 'Get list of all meetings',
                'auth_required': True,
                'parameters': [
                    {
                        'name': 'page',
                        'type': 'integer',
                        'required': False,
                        'description': 'Page number for pagination',
                        'default': 1
                    },
                    {
                        'name': 'limit',
                        'type': 'integer',
                        'required': False,
                        'description': 'Number of meetings per page',
                        'default': 20
                    },
                    {
                        'name': 'project_id',
                        'type': 'integer',
                        'required': False,
                        'description': 'Filter by project ID'
                    }
                ],
                'responses': {
                    '200': {
                        'description': 'Meetings retrieved successfully',
                        'example': {
                            'meetings': [
                                {
                                    'id': 1,
                                    'client_name': 'Acme Corp',
                                    'project_name': 'Website Redesign',
                                    'summary': 'Project kickoff meeting...',
                                    'created_at': '2024-01-15T10:30:00Z',
                                    'project_id': 1
                                }
                            ],
                            'total': 1,
                            'page': 1,
                            'pages': 1
                        }
                    }
                }
            }
        },
        'projects': {
            'list': {
                'path': '/projects',
                'methods': ['GET', 'POST'],
                'description': 'List all projects or create new project',
                'auth_required': True,
                'parameters': [
                    {
                        'name': 'name',
                        'type': 'string',
                        'required': True,
                        'description': 'Project name'
                    },
                    {
                        'name': 'client',
                        'type': 'string',
                        'required': True,
                        'description': 'Client name'
                    },
                    {
                        'name': 'description',
                        'type': 'string',
                        'required': False,
                        'description': 'Project description'
                    }
                ],
                'responses': {
                    '200': {
                        'description': 'Projects retrieved successfully'
                    },
                    '201': {
                        'description': 'Project created successfully'
                    }
                }
            }
        },
        'tasks': {
            'list': {
                'path': '/tasks',
                'methods': ['GET', 'POST'],
                'description': 'List all tasks or create new task',
                'auth_required': True,
                'parameters': [
                    {
                        'name': 'task_description',
                        'type': 'string',
                        'required': True,
                        'description': 'Task description'
                    },
                    {
                        'name': 'priority',
                        'type': 'string',
                        'required': False,
                        'description': 'Task priority (low, medium, high, critical)',
                        'default': 'medium'
                    },
                    {
                        'name': 'project_id',
                        'type': 'integer',
                        'required': True,
                        'description': 'Project ID'
                    },
                    {
                        'name': 'assignee_id',
                        'type': 'integer',
                        'required': False,
                        'description': 'Team member ID to assign task to'
                    }
                ],
                'responses': {
                    '200': {
                        'description': 'Tasks retrieved successfully'
                    },
                    '201': {
                        'description': 'Task created successfully'
                    }
                }
            }
        },
        'export': {
            'pdf': {
                'path': '/export/meeting/pdf/<int:meeting_id>',
                'methods': ['GET'],
                'description': 'Export meeting summary as PDF',
                'auth_required': True,
                'responses': {
                    '200': {
                        'description': 'PDF file generated successfully',
                        'content_type': 'application/pdf'
                    }
                }
            },
            'excel': {
                'path': '/export/meetings/excel',
                'methods': ['GET'],
                'description': 'Export all meetings as Excel file',
                'auth_required': True,
                'responses': {
                    '200': {
                        'description': 'Excel file generated successfully',
                        'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }
                }
            }
        },
        'monitoring': {
            'health': {
                'path': '/health',
                'methods': ['GET'],
                'description': 'Get application health status',
                'auth_required': False,
                'responses': {
                    '200': {
                        'description': 'Health status retrieved',
                        'example': {
                            'status': 'healthy',
                            'message': 'All systems operational',
                            'timestamp': '2024-01-15T14:30:00Z',
                            'uptime': 3600,
                            'database': 'healthy',
                            'cpu_percent': 25.5,
                            'memory_percent': 45.2
                        }
                    }
                }
            },
            'metrics': {
                'path': '/metrics',
                'methods': ['GET'],
                'description': 'Get application performance metrics',
                'auth_required': True,
                'responses': {
                    '200': {
                        'description': 'Metrics retrieved successfully',
                        'example': {
                            'total_requests': 1500,
                            'average_response_time': 0.245,
                            'error_rate': 2.5,
                            'requests_per_minute': 12.5
                        }
                    }
                }
            }
        }
    }
}

@api_docs_bp.route('/')
def api_documentation():
    """Main API documentation page"""
    return render_template('api_docs.html', docs=API_DOCUMENTATION)

@api_docs_bp.route('/interactive')
def interactive_docs():
    """Interactive API testing interface"""
    return render_template('api_interactive.html', docs=API_DOCUMENTATION)

@api_docs_bp.route('/endpoints')
def list_endpoints():
    """Get list of all API endpoints"""
    endpoints = []
    
    for category, category_endpoints in API_DOCUMENTATION['endpoints'].items():
        for endpoint_name, endpoint_data in category_endpoints.items():
            endpoints.append({
                'category': category,
                'name': endpoint_name,
                'path': endpoint_data['path'],
                'methods': endpoint_data['methods'],
                'description': endpoint_data['description'],
                'auth_required': endpoint_data.get('auth_required', False)
            })
    
    return jsonify({
        'endpoints': endpoints,
        'total': len(endpoints)
    })

@api_docs_bp.route('/test-endpoint', methods=['POST'])
def test_endpoint():
    """Test API endpoint with provided parameters"""
    try:
        data = request.get_json()
        endpoint = data.get('endpoint')
        method = data.get('method', 'GET')
        params = data.get('params', {})
        headers = data.get('headers', {})
        
        # This would make an actual request to the endpoint
        # For now, return a mock response
        return jsonify({
            'success': True,
            'message': f'Test request to {method} {endpoint}',
            'params': params,
            'headers': headers,
            'mock_response': {
                'status': 'success',
                'data': 'This is a mock response for testing'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def register_api_docs(app):
    """Register API documentation blueprint with the app"""
    app.register_blueprint(api_docs_bp)
