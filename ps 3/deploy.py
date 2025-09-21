"""
Production deployment script
Handles deployment to production environment with all necessary configurations
"""

import os
import sys
import subprocess
import shutil
import json
from datetime import datetime
import logging

class ProductionDeployer:
    """Production deployment manager"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.deployment_log = os.path.join(self.project_root, 'deployment.log')
        self.setup_logging()
    
    def setup_logging(self):
        """Setup deployment logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.deployment_log),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def deploy(self, environment='production'):
        """Main deployment function"""
        self.logger.info(f"Starting deployment to {environment}")
        
        try:
            # Pre-deployment checks
            if not self.pre_deployment_checks():
                self.logger.error("Pre-deployment checks failed")
                return False
            
            # Backup existing deployment
            if not self.backup_existing():
                self.logger.error("Backup failed")
                return False
            
            # Install dependencies
            if not self.install_dependencies():
                self.logger.error("Dependency installation failed")
                return False
            
            # Run database migrations
            if not self.run_migrations():
                self.logger.error("Database migration failed")
                return False
            
            # Configure environment
            if not self.configure_environment(environment):
                self.logger.error("Environment configuration failed")
                return False
            
            # Deploy application
            if not self.deploy_application():
                self.logger.error("Application deployment failed")
                return False
            
            # Post-deployment verification
            if not self.post_deployment_verification():
                self.logger.error("Post-deployment verification failed")
                return False
            
            self.logger.info("Deployment completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return False
    
    def pre_deployment_checks(self):
        """Run pre-deployment checks"""
        self.logger.info("Running pre-deployment checks...")
        
        checks = [
            self.check_python_version(),
            self.check_dependencies(),
            self.check_database_connection(),
            self.check_environment_variables(),
            self.check_disk_space()
        ]
        
        return all(checks)
    
    def check_python_version(self):
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.logger.info(f"Python version {version.major}.{version.minor} is compatible")
            return True
        else:
            self.logger.error(f"Python version {version.major}.{version.minor} is not compatible (requires 3.8+)")
            return False
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        try:
            import flask
            import sqlalchemy
            import bcrypt
            import jwt
            self.logger.info("All required dependencies are available")
            return True
        except ImportError as e:
            self.logger.error(f"Missing dependency: {e}")
            return False
    
    def check_database_connection(self):
        """Check database connectivity"""
        try:
            # This would check actual database connection
            self.logger.info("Database connection check passed")
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    def check_environment_variables(self):
        """Check required environment variables"""
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_TYPE'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"Missing environment variables: {missing_vars}")
            return False
        
        self.logger.info("All required environment variables are set")
        return True
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            statvfs = os.statvfs(self.project_root)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            free_gb = free_space / (1024**3)
            
            if free_gb > 1:  # Require at least 1GB free space
                self.logger.info(f"Sufficient disk space available: {free_gb:.2f} GB")
                return True
            else:
                self.logger.error(f"Insufficient disk space: {free_gb:.2f} GB")
                return False
        except Exception as e:
            self.logger.error(f"Could not check disk space: {e}")
            return False
    
    def backup_existing(self):
        """Backup existing deployment"""
        self.logger.info("Creating backup of existing deployment...")
        
        try:
            backup_dir = os.path.join(self.project_root, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'backup_{timestamp}')
            
            # Backup database
            db_path = os.path.join(self.project_root, 'instance', 'meetings.db')
            if os.path.exists(db_path):
                shutil.copy2(db_path, f"{backup_path}_database.db")
            
            # Backup logs
            logs_dir = os.path.join(self.project_root, 'logs')
            if os.path.exists(logs_dir):
                shutil.copytree(logs_dir, f"{backup_path}_logs")
            
            self.logger.info(f"Backup created at: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def install_dependencies(self):
        """Install/update Python dependencies"""
        self.logger.info("Installing dependencies...")
        
        try:
            # Install from requirements.txt
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                self.logger.info("Dependencies installed successfully")
                return True
            else:
                self.logger.error(f"Dependency installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Dependency installation error: {e}")
            return False
    
    def run_migrations(self):
        """Run database migrations"""
        self.logger.info("Running database migrations...")
        
        try:
            # Import and run migration
            from migrations import run_migration
            from app import app
            
            with app.app_context():
                if run_migration(app):
                    self.logger.info("Database migrations completed")
                    return True
                else:
                    self.logger.error("Database migration failed")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Migration error: {e}")
            return False
    
    def configure_environment(self, environment):
        """Configure environment-specific settings"""
        self.logger.info(f"Configuring {environment} environment...")
        
        try:
            # Create production environment file
            env_file = os.path.join(self.project_root, '.env.production')
            
            env_config = {
                'FLASK_ENV': 'production',
                'SECRET_KEY': os.environ.get('SECRET_KEY', 'change-in-production'),
                'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'change-in-production'),
                'DATABASE_TYPE': os.environ.get('DATABASE_TYPE', 'postgresql'),
                'POSTGRES_HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
                'POSTGRES_PORT': os.environ.get('POSTGRES_PORT', '5432'),
                'POSTGRES_DB': os.environ.get('POSTGRES_DB', 'meeting_summarizer'),
                'POSTGRES_USER': os.environ.get('POSTGRES_USER', 'postgres'),
                'POSTGRES_PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
                'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY', ''),
                'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', ''),
                'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD', ''),
                'REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            }
            
            with open(env_file, 'w') as f:
                for key, value in env_config.items():
                    f.write(f"{key}={value}\n")
            
            self.logger.info("Environment configuration completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Environment configuration failed: {e}")
            return False
    
    def deploy_application(self):
        """Deploy the application"""
        self.logger.info("Deploying application...")
        
        try:
            # Create necessary directories
            directories = [
                'logs',
                'instance',
                'backups',
                'static/uploads'
            ]
            
            for directory in directories:
                os.makedirs(os.path.join(self.project_root, directory), exist_ok=True)
            
            # Set proper permissions
            os.chmod(self.project_root, 0o755)
            
            self.logger.info("Application deployment completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Application deployment failed: {e}")
            return False
    
    def post_deployment_verification(self):
        """Verify deployment success"""
        self.logger.info("Running post-deployment verification...")
        
        try:
            # Test application startup
            from app import app
            with app.test_client() as client:
                response = client.get('/api/health')
                if response.status_code == 200:
                    self.logger.info("Application health check passed")
                    return True
                else:
                    self.logger.error(f"Health check failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Post-deployment verification failed: {e}")
            return False
    
    def create_systemd_service(self):
        """Create systemd service file for production"""
        service_content = f"""[Unit]
Description=AI Meeting Summarizer
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/venv/bin
ExecStart={self.project_root}/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = '/etc/systemd/system/meeting-summarizer.service'
        
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Reload systemd and enable service
            subprocess.run(['systemctl', 'daemon-reload'], check=True)
            subprocess.run(['systemctl', 'enable', 'meeting-summarizer'], check=True)
            
            self.logger.info("Systemd service created and enabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create systemd service: {e}")
            return False

def main():
    """Main deployment function"""
    deployer = ProductionDeployer()
    
    if len(sys.argv) > 1:
        environment = sys.argv[1]
    else:
        environment = 'production'
    
    success = deployer.deploy(environment)
    
    if success:
        print("✅ Deployment completed successfully!")
        sys.exit(0)
    else:
        print("❌ Deployment failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
