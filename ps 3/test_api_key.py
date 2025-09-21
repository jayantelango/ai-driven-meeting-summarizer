#!/usr/bin/env python3
"""
Test script to verify Google Gemini API key
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test the Google Gemini API key"""
    
    # Get API key from environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set your API key using one of these methods:")
        print("1. Environment variable: set GEMINI_API_KEY=your_key_here")
        print("2. Edit the code directly in app.py")
        return False
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with a simple request
        print("🔄 Testing API key...")
        response = model.generate_content("Hello, this is a test. Please respond with 'API key is working!'")
        
        print("✅ API key is working!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔑 Google Gemini API Key Tester")
    print("=" * 40)
    
    if test_api_key():
        print("\n🎉 Your API key is ready to use!")
        print("You can now run the main application with AI functionality.")
    else:
        print("\n💡 To get an API key:")
        print("1. Visit: https://makersuite.google.com/app/apikey")
        print("2. Sign in with your Google account")
        print("3. Click 'Create API Key'")
        print("4. Copy the key and set it as GEMINI_API_KEY environment variable")