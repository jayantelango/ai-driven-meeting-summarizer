#!/usr/bin/env python3
"""
Quick API Key Validation Script
Run this after you've updated your .env file with your real API key
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def quick_validation():
    print("🔍 Quick API Key Validation")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    api_key = os.environ.get('GEMINI_API_KEY')
    
    # Check if key exists and is not placeholder
    if not api_key:
        print("❌ No API key found")
        return False
    
    if api_key == 'your_gemini_api_key_here':
        print("❌ Still using placeholder - please update .env file")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Test connection
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Reply with just 'API Working' if you receive this")
        
        if response and response.text:
            print("✅ API Connection Successful!")
            print(f"📝 Response: {response.text.strip()}")
            return True
        else:
            print("❌ API responded but with empty content")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_validation()
    if success:
        print("\n🎉 SUCCESS: API key is working!")
        print("✅ Your application should now work with AI features")
    else:
        print("\n🚨 ISSUE: Please check your API key configuration")
        print("1. Ensure you've replaced the placeholder in .env")
        print("2. Verify your API key is valid from Google AI Studio")