#!/usr/bin/env python3
"""
AI Meeting Summarizer - API Key Setup Script
This script helps you configure your Google Gemini API key quickly and easily.
"""

import os
import sys
import webbrowser
from pathlib import Path
import google.generativeai as genai

def print_banner():
    """Print the setup banner"""
    print("=" * 60)
    print("🔑 AI Meeting Summarizer - API Key Setup")
    print("=" * 60)
    print()

def check_env_file():
    """Check if .env file exists and is properly configured"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found!")
        print("   Creating .env file from template...")
        
        # Create .env from template
        template_path = Path('env_template.txt')
        if template_path.exists():
            with open(template_path, 'r') as template:
                with open('.env', 'w') as env_file:
                    env_file.write(template.read())
            print("✅ .env file created successfully!")
        else:
            print("❌ Template file not found!")
            return False
    else:
        print("✅ .env file found!")
    
    return True

def get_api_key_from_user():
    """Get API key from user input"""
    print("\n📋 API Key Setup:")
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Sign in with your Google account")
    print("3. Click 'Create API Key'")
    print("4. Copy the generated key")
    print()
    
    # Ask if user wants to open browser
    open_browser = input("🌐 Open browser to get API key? (y/N): ").strip().lower()
    if open_browser == 'y':
        webbrowser.open("https://makersuite.google.com/app/apikey")
        print("🌐 Browser opened! Please get your API key and return here.")
        print()
    
    # Get API key from user
    api_key = input("📋 Paste your Gemini API key here: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return None
    
    return api_key

def validate_api_key(api_key):
    """Validate the API key format and test it"""
    print("\n🧪 Validating API key...")
    
    # Basic format validation
    if not api_key.startswith('AIza'):
        print("⚠️  Warning: API key doesn't look like a valid Gemini key")
        print("   Valid keys usually start with 'AIza'")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return False
    
    if len(api_key) < 20:
        print("❌ API key appears too short")
        return False
    
    # Test the API key
    try:
        print("🔌 Testing API connection...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple test
        response = model.generate_content("Hello, this is a test.")
        if response and response.text:
            print("✅ API key is working!")
            print(f"📝 Test response: {response.text.strip()}")
            return True
        else:
            print("❌ API responded but with empty content")
            return False
            
    except Exception as e:
        print(f"❌ API key test failed: {str(e)}")
        
        # Provide specific error guidance
        if "API_KEY_INVALID" in str(e):
            print("🔧 Diagnosis: Invalid API key")
        elif "PERMISSION_DENIED" in str(e):
            print("🔧 Diagnosis: Permission denied - check API key permissions")
        elif "QUOTA_EXCEEDED" in str(e):
            print("🔧 Diagnosis: API quota exceeded")
        else:
            print("🔧 Diagnosis: Network or configuration issue")
        
        return False

def update_env_file(api_key):
    """Update the .env file with the real API key"""
    try:
        # Read current content
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace the placeholder
        new_content = content.replace('your_gemini_api_key_here', api_key)
        
        # Write back
        with open('.env', 'w') as f:
            f.write(new_content)
        
        print("✅ API key updated in .env file!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_application():
    """Test if the application can start properly"""
    print("\n🚀 Testing application startup...")
    
    try:
        # Import the main app to test configuration
        from app import initialize_gemini, validate_api_key
        
        # Test AI initialization
        model = initialize_gemini()
        if model:
            print("✅ AI engine initialized successfully!")
            
            # Test API key validation
            is_valid, message = validate_api_key()
            if is_valid:
                print(f"✅ API key validation: {message}")
                return True
            else:
                print(f"❌ API key validation failed: {message}")
                return False
        else:
            print("❌ AI engine initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ app.py not found! Please run this script from the project directory.")
        return False
    
    # Step 1: Check/create .env file
    if not check_env_file():
        return False
    
    # Step 2: Get API key from user
    api_key = get_api_key_from_user()
    if not api_key:
        return False
    
    # Step 3: Validate API key
    if not validate_api_key(api_key):
        return False
    
    # Step 4: Update .env file
    if not update_env_file(api_key):
        return False
    
    # Step 5: Test application
    if test_application():
        print("\n" + "=" * 60)
        print("🎉 SETUP COMPLETE!")
        print("✅ API key configured and working")
        print("✅ Application ready to run")
        print()
        print("🚀 Next steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Start analyzing meetings!")
        print("=" * 60)
        return True
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
