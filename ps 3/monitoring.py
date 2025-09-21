"""
Enhanced monitoring and logging system
Provides comprehensive application monitoring, metrics, and alerting
"""

import os
import logging
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import request, g, current_app
import threading

# Try to import psutil, fallback to mock if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Mock psutil for development
    class MockPsutil:
        @staticmethod
        def cpu_percent(interval=1):
            return 25.0
        
        @staticmethod
        def virtual_memory():
            class MockMemory:
                percent = 45.0
                available = 1024 * 1024 * 1024  # 1GB
            return MockMemory()
        
        @staticmethod
        def disk_usage(path):
            class MockDisk:
                percent = 50.0
                free = 1024 * 1024 * 1024 * 10  # 10GB
            return MockDisk()
    
    psutil = MockPsutil()

class ApplicationMonitor:
    """Comprehensive application monitoring system"""
    
    def __init__(self, app=None):
        self.app = app
        self.metrics = defaultdict(list)
        self.performance_data = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.start_time = time.time()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize monitoring for the Flask app"""
        self.app = app
        
        # Configure logging
        self._setup_logging()
        
        # Register monitoring hooks
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration"""
        # Create logs directory
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging format
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # File handler for all logs
        file_handler = logging.FileHandler(
            os.path.join(log_dir, 'app.log'),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Error handler for errors only
        error_handler = logging.FileHandler(
            os.path.join(log_dir, 'errors.log'),
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(log_format))
        
        # Security handler for security events
        security_handler = logging.FileHandler(
            os.path.join(log_dir, 'security.log'),
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[file_handler, error_handler, security_handler]
        )
        
        # Create specific loggers
        self.app_logger = logging.getLogger('app')
        self.security_logger = logging.getLogger('security')
        self.performance_logger = logging.getLogger('performance')
    
    def before_request(self):
        """Monitor request start"""
        g.start_time = time.time()
        g.request_id = f"{int(time.time() * 1000)}_{id(request)}"
        
        # Log request
        self.app_logger.info(f"Request started: {request.method} {request.path} from {request.remote_addr}")
        
        # Track request count
        self.request_counts[request.path] += 1
    
    def after_request(self, response):
        """Monitor request completion"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Log performance
            self.performance_logger.info(f"Request completed: {request.method} {request.path} in {duration:.3f}s")
            
            # Store performance data
            self.performance_data.append({
                'timestamp': datetime.utcnow().isoformat(),
                'method': request.method,
                'path': request.path,
                'duration': duration,
                'status_code': response.status_code,
                'remote_addr': request.remote_addr
            })
            
            # Track errors
            if response.status_code >= 400:
                self.error_counts[f"{request.method} {request.path}"] += 1
                self.app_logger.warning(f"Error response: {response.status_code} for {request.method} {request.path}")
        
        return response
    
    def _start_background_monitoring(self):
        """Start background monitoring thread"""
        def monitor_loop():
            while True:
                try:
                    self._collect_system_metrics()
                    self._cleanup_old_data()
                    time.sleep(60)  # Monitor every minute
                except Exception as e:
                    self.app_logger.error(f"Background monitoring error: {e}")
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Application uptime
            uptime = time.time() - self.start_time
            
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': disk.percent,
                'disk_free': disk.free,
                'uptime_seconds': uptime,
                'request_count': sum(self.request_counts.values()),
                'error_count': sum(self.error_counts.values())
            }
            
            self.metrics['system'].append(metrics)
            
            # Log high resource usage
            if cpu_percent > 80:
                self.app_logger.warning(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 80:
                self.app_logger.warning(f"High memory usage: {memory.percent}%")
            
            if disk.percent > 90:
                self.app_logger.warning(f"High disk usage: {disk.percent}%")
                
        except Exception as e:
            self.app_logger.error(f"Failed to collect system metrics: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # Clean up performance data
        while self.performance_data and self.performance_data[0]['timestamp'] < cutoff_time.isoformat():
            self.performance_data.popleft()
        
        # Clean up metrics (keep last 1000 entries)
        for key in self.metrics:
            if len(self.metrics[key]) > 1000:
                self.metrics[key] = self.metrics[key][-1000:]
    
    def get_health_status(self):
        """Get application health status"""
        try:
            # Check database connection
            db_healthy = self._check_database_health()
            
            # Check system resources
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            # Determine overall health
            if not db_healthy:
                status = 'unhealthy'
                message = 'Database connection failed'
            elif cpu_percent > 90 or memory_percent > 90:
                status = 'degraded'
                message = 'High resource usage'
            elif cpu_percent > 80 or memory_percent > 80:
                status = 'warning'
                message = 'Elevated resource usage'
            else:
                status = 'healthy'
                message = 'All systems operational'
            
            return {
                'status': status,
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': time.time() - self.start_time,
                'database': 'healthy' if db_healthy else 'unhealthy',
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'request_count': sum(self.request_counts.values()),
                'error_count': sum(self.error_counts.values())
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Health check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _check_database_health(self):
        """Check database connection health"""
        try:
            from models import db
            db.session.execute('SELECT 1')
            return True
        except Exception:
            return False
    
    def get_performance_metrics(self, hours=24):
        """Get performance metrics for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        # Filter performance data
        recent_data = [
            entry for entry in self.performance_data
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        
        if not recent_data:
            return {
                'total_requests': 0,
                'average_response_time': 0,
                'error_rate': 0,
                'requests_per_minute': 0
            }
        
        # Calculate metrics
        total_requests = len(recent_data)
        total_duration = sum(entry['duration'] for entry in recent_data)
        average_response_time = total_duration / total_requests if total_requests > 0 else 0
        
        error_count = sum(1 for entry in recent_data if entry['status_code'] >= 400)
        error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
        
        requests_per_minute = total_requests / (hours * 60)
        
        return {
            'total_requests': total_requests,
            'average_response_time': round(average_response_time, 3),
            'error_rate': round(error_rate, 2),
            'requests_per_minute': round(requests_per_minute, 2),
            'error_count': error_count,
            'success_count': total_requests - error_count
        }
    
    def get_error_summary(self):
        """Get error summary"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_breakdown': dict(self.error_counts),
            'recent_errors': list(self.performance_data)[-10:]  # Last 10 errors
        }
    
    def log_security_event(self, event_type, details):
        """Log security-related events"""
        self.security_logger.warning(f"Security Event: {event_type} - {details}")
        
        # Store security metrics
        self.metrics['security'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'remote_addr': request.remote_addr if request else 'unknown'
        })
    
    def get_monitoring_dashboard_data(self):
        """Get data for monitoring dashboard"""
        return {
            'health': self.get_health_status(),
            'performance': self.get_performance_metrics(),
            'errors': self.get_error_summary(),
            'system_metrics': self.metrics['system'][-10:] if self.metrics['system'] else [],
            'recent_requests': list(self.performance_data)[-20:] if self.performance_data else []
        }

# Global monitor instance
monitor = ApplicationMonitor()

def init_monitoring(app):
    """Initialize monitoring for the app"""
    monitor.init_app(app)
    return monitor
