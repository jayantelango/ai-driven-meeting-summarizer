#!/usr/bin/env python3
"""
Direct API Key Test - Test the current .env configuration
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.environ.get('GEMINI_API_KEY')

print(f"🔍 API Key Check:")
print(f"✅ API Key found: {api_key[:15]}..." if api_key else "❌ No API key found")

# Check if it's a placeholder
if api_key == 'your_gemini_api_key_here':
    print("❌ Still using placeholder value")
    exit(1)
elif api_key == 'AIzaSyD9X1234567890abcdefghijklmnopqrstuv':
    print("❌ Using example/sample API key - this won't work")
    exit(1)

# Test the API
try:
    print("🧪 Testing API connection...")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Hello World' if this API key is working")
    
    if response and response.text:
        print(f"✅ SUCCESS! API Response: {response.text.strip()}")
        print("🎉 Your API key is working perfectly!")
    else:
        print("❌ API responded but with empty content")
        
except Exception as e:
    print(f"❌ API Error: {str(e)}")
    if "API_KEY_INVALID" in str(e):
        print("💡 The API key format might be correct, but Google says it's invalid.")
        print("📋 Please double-check that you copied the key correctly from Google AI Studio")
    elif "PERMISSION_DENIED" in str(e):
        print("💡 API key exists but doesn't have permission for Gemini API")
    elif "QUOTA_EXCEEDED" in str(e):
        print("💡 API quota has been exceeded")