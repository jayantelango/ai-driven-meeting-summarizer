"""
Rate limiting implementation using Redis or in-memory storage
Prevents API abuse and ensures fair usage
"""

import time
import json
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify, g
import logging

class RateLimiter:
    """In-memory rate limiter (for development) - use Redis in production"""
    
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = 3600  # Clean up old entries every hour
        self.last_cleanup = time.time()
    
    def is_allowed(self, key, limit, window):
        """Check if request is allowed based on rate limit"""
        current_time = time.time()
        
        # Clean up old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries()
            self.last_cleanup = current_time
        
        # Get request history for this key - ensure it's a deque
        if key not in self.requests:
            self.requests[key] = deque()
        request_times = self.requests[key]
        
        # Remove requests outside the window
        cutoff_time = current_time - window
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Check if under limit
        if len(request_times) < limit:
            request_times.append(current_time)
            return True, {
                'limit': limit,
                'remaining': limit - len(request_times),
                'reset_time': int(current_time + window)
            }
        else:
            return False, {
                'limit': limit,
                'remaining': 0,
                'reset_time': int(request_times[0] + window) if request_times else int(current_time + window)
            }
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leaks"""
        current_time = time.time()
        keys_to_remove = []
        
        for key, request_times in self.requests.items():
            # Remove entries older than 24 hours
            cutoff_time = current_time - 86400
            while request_times and request_times[0] < cutoff_time:
                request_times.popleft()
            
            # Remove empty entries
            if not request_times:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.requests[key]

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def rate_limit(requests=100, window=3600, per='ip'):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine the key for rate limiting
            if per == 'ip':
                key = f"ip:{get_client_ip()}"
            elif per == 'user':
                # Use user ID if authenticated
                user = getattr(g, 'current_user', None)
                if user:
                    key = f"user:{user.id}"
                else:
                    key = f"ip:{get_client_ip()}"
            else:
                key = f"ip:{get_client_ip()}"
            
            # Check rate limit
            allowed, info = rate_limiter.is_allowed(key, requests, window)
            
            if not allowed:
                logging.warning(f"Rate limit exceeded for {key}: {info}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Limit: {info["limit"]} per {window} seconds',
                    'retry_after': info['reset_time'] - int(time.time())
                }), 429
            
            # Add rate limit info to response headers
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(info['limit'])
                response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(info['reset_time'])
            
            return response
        
        return decorated_function
    return decorator

def api_rate_limit():
    """Apply rate limiting based on endpoint"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            endpoint = request.endpoint
            if endpoint:
                # Get rate limit config for this endpoint
                limit_config = RATE_LIMITS.get(endpoint, RATE_LIMITS['default'])
                requests = limit_config['requests']
                window = limit_config['window']
                
                # Apply rate limiting
                key = f"endpoint:{endpoint}:{get_client_ip()}"
                allowed, info = rate_limiter.is_allowed(key, requests, window)
                
                if not allowed:
                    logging.warning(f"API rate limit exceeded for {endpoint}: {info}")
                    return jsonify({
                        'error': 'API rate limit exceeded',
                        'message': f'Too many requests to {endpoint}. Limit: {info["limit"]} per {window} seconds',
                        'retry_after': info['reset_time'] - int(time.time())
                    }), 429
                
                # Store rate limit info for response headers
                g.rate_limit_info = info
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Import RATE_LIMITS from validators
try:
    from validators import RATE_LIMITS
except ImportError:
    # Fallback if validators module is not available
    RATE_LIMITS = {
        'api/summarize': {'requests': 10, 'window': 3600},
        'api/upload': {'requests': 5, 'window': 3600},
        'api/send-mail': {'requests': 20, 'window': 3600},
        'api/assistant': {'requests': 30, 'window': 3600},
        'default': {'requests': 100, 'window': 3600}
    }
