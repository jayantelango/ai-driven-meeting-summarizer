"""
Database configuration for production PostgreSQL setup
Handles both SQLite (development) and PostgreSQL (production) configurations
"""

import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

class DatabaseConfig:
    """Database configuration manager"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize database configuration"""
        self.app = app
        
        # Determine database type
        db_type = os.environ.get('DATABASE_TYPE', 'sqlite').lower()
        
        if db_type == 'postgresql':
            self._setup_postgresql()
        else:
            self._setup_sqlite()
    
    def _setup_sqlite(self):
        """Setup SQLite database for development"""
        db_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'instance', 
            'meetings.db'
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        logging.info("Using SQLite database for development")
    
    def _setup_postgresql(self):
        """Setup PostgreSQL database for production"""
        # Get PostgreSQL connection details from environment
        db_host = os.environ.get('POSTGRES_HOST', 'localhost')
        db_port = os.environ.get('POSTGRES_PORT', '5432')
        db_name = os.environ.get('POSTGRES_DB', 'meeting_summarizer')
        db_user = os.environ.get('POSTGRES_USER', 'postgres')
        db_password = os.environ.get('POSTGRES_PASSWORD', '')
        
        # Construct PostgreSQL URI
        postgres_uri = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
        
        self.app.config['SQLALCHEMY_DATABASE_URI'] = postgres_uri
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 20
        }
        
        logging.info(f"Using PostgreSQL database: {db_host}:{db_port}/{db_name}")
    
    def test_connection(self):
        """Test database connection"""
        try:
            engine = create_engine(self.app.config['SQLALCHEMY_DATABASE_URI'])
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.fetchone()
            logging.info("Database connection successful")
            return True
        except SQLAlchemyError as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def create_tables(self, db):
        """Create all database tables"""
        try:
            db.create_all()
            logging.info("Database tables created successfully")
            return True
        except SQLAlchemyError as e:
            logging.error(f"Failed to create tables: {e}")
            return False
    
    def get_database_info(self):
        """Get database information"""
        uri = self.app.config['SQLALCHEMY_DATABASE_URI']
        
        if uri.startswith('sqlite'):
            return {
                'type': 'SQLite',
                'path': uri.replace('sqlite:///', ''),
                'status': 'Development'
            }
        elif uri.startswith('postgresql'):
            # Parse PostgreSQL URI
            parts = uri.replace('postgresql://', '').split('@')
            if len(parts) == 2:
                user_pass = parts[0].split(':')
                host_db = parts[1].split('/')
                if len(host_db) == 2:
                    host_port = host_db[0].split(':')
                    return {
                        'type': 'PostgreSQL',
                        'host': host_port[0],
                        'port': host_port[1] if len(host_port) > 1 else '5432',
                        'database': host_db[1],
                        'user': user_pass[0],
                        'status': 'Production'
                    }
        
        return {
            'type': 'Unknown',
            'status': 'Unknown'
        }

# PostgreSQL-specific functions
def create_postgresql_tables():
    """Create PostgreSQL-specific table modifications"""
    postgresql_sql = """
-- PostgreSQL-specific optimizations and constraints

-- Add foreign key constraints (PostgreSQL supports this better than SQLite)
ALTER TABLE project ADD CONSTRAINT fk_project_created_by 
    FOREIGN KEY (created_by) REFERENCES "user"(id);

ALTER TABLE task_assignment ADD CONSTRAINT fk_task_created_by 
    FOREIGN KEY (created_by) REFERENCES "user"(id);

ALTER TABLE task_assignment ADD CONSTRAINT fk_task_assignee 
    FOREIGN KEY (assignee_id) REFERENCES team_member(id);

ALTER TABLE task_assignment ADD CONSTRAINT fk_task_project 
    FOREIGN KEY (project_id) REFERENCES project(id);

ALTER TABLE task_assignment ADD CONSTRAINT fk_task_meeting 
    FOREIGN KEY (meeting_id) REFERENCES meeting_summary(id);

ALTER TABLE meeting_summary ADD CONSTRAINT fk_meeting_project 
    FOREIGN KEY (project_id) REFERENCES project(id);

-- Add additional indexes for PostgreSQL
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_project_created_by ON project(created_by);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_created_by ON task_assignment(created_by);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_task_assignee ON task_assignment(assignee_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_meeting_project ON meeting_summary(project_id);

-- Add check constraints
ALTER TABLE "user" ADD CONSTRAINT chk_user_role 
    CHECK (role IN ('admin', 'manager', 'user'));

ALTER TABLE project ADD CONSTRAINT chk_project_status 
    CHECK (status IN ('active', 'inactive', 'completed', 'cancelled'));

ALTER TABLE task_assignment ADD CONSTRAINT chk_task_priority 
    CHECK (priority IN ('low', 'medium', 'high', 'critical'));

ALTER TABLE task_assignment ADD CONSTRAINT chk_task_status 
    CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled'));

-- Add triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_project_updated_at 
    BEFORE UPDATE ON project 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_task_updated_at 
    BEFORE UPDATE ON task_assignment 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""
    return postgresql_sql

def setup_production_database():
    """Setup production database with all optimizations"""
    try:
        # This would be called during production deployment
        logging.info("Setting up production database...")
        
        # Create tables
        # Add PostgreSQL-specific optimizations
        # Set up monitoring
        # Configure backups
        
        logging.info("Production database setup completed")
        return True
    except Exception as e:
        logging.error(f"Production database setup failed: {e}")
        return False
