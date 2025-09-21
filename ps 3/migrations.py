"""
Database migration script for adding user authentication tables
Handles migration from existing database to new schema with user management
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask
from models import db, User, Role, UserRole, Project, TeamMember, MeetingSummary, TaskAssignment, MeetingTemplate
import logging

def create_migration_script():
    """Create SQL migration script for database schema changes"""
    
    migration_sql = """
-- Migration: Add User Authentication Tables
-- Date: {date}
-- Description: Add User, Role, UserRole tables and update existing tables

-- Create User table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    role VARCHAR(20) DEFAULT 'user' NOT NULL,
    is_active BOOLEAN DEFAULT 1 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);

-- Create Role table
CREATE TABLE IF NOT EXISTS role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(200),
    permissions JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create UserRole junction table
CREATE TABLE IF NOT EXISTS user_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (role_id) REFERENCES role (id),
    UNIQUE(user_id, role_id)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_username ON user(username);
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
CREATE INDEX IF NOT EXISTS idx_user_role ON user(role);
CREATE INDEX IF NOT EXISTS idx_user_active ON user(is_active);

-- Update existing tables to add user references
-- Add created_by column to project table
ALTER TABLE project ADD COLUMN created_by INTEGER;
ALTER TABLE project ADD COLUMN description TEXT;
ALTER TABLE project ADD COLUMN status VARCHAR(20) DEFAULT 'active';
ALTER TABLE project ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE project ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Add created_by column to task_assignment table
ALTER TABLE task_assignment ADD COLUMN created_by INTEGER;
ALTER TABLE task_assignment ADD COLUMN due_date DATETIME;
ALTER TABLE task_assignment ADD COLUMN completion_notes TEXT;

-- Add foreign key constraints
-- Note: SQLite doesn't support adding foreign keys to existing tables easily
-- These would be added in a proper migration system

-- Insert default roles
INSERT OR IGNORE INTO role (name, description, permissions) VALUES 
('admin', 'Administrator with full access', '{{"all": true}}'),
('manager', 'Manager with project management access', '{{"projects": true, "meetings": true, "tasks": true}}'),
('user', 'Regular user with basic access', '{{"meetings": true, "tasks": true}}');

-- Create default admin user (password: admin123)
-- Note: This should be changed in production
INSERT OR IGNORE INTO user (username, email, password_hash, role, is_active) VALUES 
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Qz8K2O', 'admin', 1);

-- Update existing projects to have a default user
UPDATE project SET created_by = 1 WHERE created_by IS NULL;

-- Update existing tasks to have a default user
UPDATE task_assignment SET created_by = 1 WHERE created_by IS NULL;
""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    return migration_sql

def run_migration(app):
    """Run the database migration"""
    try:
        with app.app_context():
            # Get database path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            # Check if migration is needed
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if user table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='user'
            """)
            
            if cursor.fetchone():
                logging.info("User tables already exist. Migration not needed.")
                conn.close()
                return True
            
            # Run migration
            logging.info("Starting database migration...")
            migration_sql = create_migration_script()
            
            # Execute migration in parts
            statements = migration_sql.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            conn.commit()
            conn.close()
            
            logging.info("Database migration completed successfully!")
            return True
            
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        return False

def create_admin_user(app):
    """Create default admin user if it doesn't exist"""
    try:
        with app.app_context():
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # Create admin user
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    role='admin',
                    is_active=True
                )
                admin_user.set_password('admin123')  # Change this in production!
                
                db.session.add(admin_user)
                db.session.commit()
                
                logging.info("Default admin user created: admin/admin123")
                return True
            else:
                logging.info("Admin user already exists")
                return True
                
    except Exception as e:
        logging.error(f"Failed to create admin user: {e}")
        return False

def verify_migration(app):
    """Verify that migration was successful"""
    try:
        with app.app_context():
            # Check if all tables exist
            tables = ['user', 'role', 'user_role']
            for table in tables:
                result = db.engine.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not result.fetchone():
                    logging.error(f"Table {table} not found after migration")
                    return False
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                logging.error("Admin user not found after migration")
                return False
            
            logging.info("Migration verification successful!")
            return True
            
    except Exception as e:
        logging.error(f"Migration verification failed: {e}")
        return False

if __name__ == '__main__':
    # This can be run as a standalone script
    from app import app
    
    logging.basicConfig(level=logging.INFO)
    
    print("Starting database migration...")
    if run_migration(app):
        print("Migration completed successfully!")
        if create_admin_user(app):
            print("Admin user created successfully!")
        if verify_migration(app):
            print("Migration verification passed!")
        else:
            print("Migration verification failed!")
    else:
        print("Migration failed!")
