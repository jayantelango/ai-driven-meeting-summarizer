#!/usr/bin/env python3
"""
Quick API Key Setup for AI Meeting Summarizer
This script helps you get and configure your Gemini API key.
"""

import webbrowser
import os
from pathlib import Path

def open_api_key_page():
    """Open the Google AI Studio page in browser"""
    print("🚀 Opening Google AI Studio...")
    print("=" * 50)
    print("📋 Follow these steps:")
    print("1. Sign in with your Google account")
    print("2. Click 'Get API Key' or 'Create API Key'")
    print("3. Copy the generated key")
    print("4. Come back here and paste it")
    print()
    
    # Open the browser
    webbrowser.open("https://makersuite.google.com/app/apikey")
    
    print("🌐 Browser opened! Please get your API key and return here.")
    print()

def update_env_file(api_key):
    """Update the .env file with the real API key"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
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

def test_api_key(api_key):
    """Test if the API key works"""
    try:
        import google.generativeai as genai
        
        print("🧪 Testing API key...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple test
        response = model.generate_content("Hello, this is a test.")
        print("✅ API key is working!")
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def main():
    """Main function"""
    print("🔑 Gemini API Key Setup")
    print("=" * 50)
    
    # Check if .env exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("   Please run setup_env.py first")
        return
    
    # Open browser for API key
    open_api_key_page()
    
    # Get API key from user
    api_key = input("📋 Paste your Gemini API key here: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return
    
    # Validate API key format
    if not api_key.startswith('AIza'):
        print("⚠️  Warning: API key doesn't look like a valid Gemini key")
        print("   Valid keys usually start with 'AIza'")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return
    
    # Test the API key
    if test_api_key(api_key):
        # Update .env file
        if update_env_file(api_key):
            print("\n🎉 Setup complete!")
            print("🚀 You can now run: python app.py")
            print("🌐 Then open: http://localhost:5000")
        else:
            print("❌ Failed to update .env file")
    else:
        print("❌ API key test failed. Please check your key and try again.")

if __name__ == "__main__":
    main()

