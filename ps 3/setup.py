#!/usr/bin/env python3
"""
Setup script for AI Meeting Summarizer
This script helps set up the application environment and dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    try:
        print("📦 Installing dependencies...")
        
        # Determine the correct pip path
        if os.name == 'nt':  # Windows
            pip_path = Path("venv/Scripts/pip.exe")
        else:  # Unix/Linux/Mac
            pip_path = Path("venv/bin/pip")
        
        if not pip_path.exists():
            print("❌ Virtual environment not found. Please run setup first.")
            return False
        
        # Upgrade pip first
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_path = Path(".env")
    template_path = Path("env_template.txt")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    if template_path.exists():
        try:
            shutil.copy(template_path, env_path)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  No env_template.txt found. Creating basic .env file...")
        try:
            with open(env_path, 'w') as f:
                f.write("""# AI Meeting Summarizer Environment Configuration
GEMINI_API_KEY=your_gemini_api_key_here
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
NOTIFICATION_RECIPIENTS=admin@company.com
FLASK_ENV=development
FLASK_DEBUG=True
""")
            print("✅ Created basic .env file")
            print("⚠️  Please edit .env file and add your API keys")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False

def create_directories():
    """Create necessary directories"""
    directories = ["instance", "logs", "uploads"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    """Main setup function"""
    print("🚀 AI Meeting Summarizer Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your Google Gemini API key")
    print("2. Get your API key from: https://makersuite.google.com/app/apikey")
    print("3. Run the application:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
        print("   python app.py")
    else:  # Unix/Linux/Mac
        print("   source venv/bin/activate")
        print("   python app.py")
    
    print("\n🌐 The application will be available at: http://localhost:5000")

if __name__ == "__main__":
    main()
