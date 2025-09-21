#!/usr/bin/env python3
"""
Test script to verify the AI Meeting Summarizer setup and functionality
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test if environment variables are properly configured"""
    print("🔧 Testing Environment Configuration...")
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found. Please create one from env_template.txt")
        return False
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    if api_key == 'your_gemini_api_key_here':
        print("⚠️  GEMINI_API_KEY is still set to placeholder value")
        print("   Please update it with your actual API key from https://makersuite.google.com/app/apikey")
        return False
    
    if len(api_key) < 20:
        print("⚠️  GEMINI_API_KEY appears to be invalid (too short)")
        return False
    
    print("✅ GEMINI_API_KEY is configured")
    return True

def test_ai_engine():
    """Test the AI engine functionality"""
    print("\n🤖 Testing AI Engine...")
    
    try:
        from ai_engine import AIEngine
        ai_engine = AIEngine()
        print("✅ AI Engine initialized successfully")
        
        # Test with sample transcript
        sample_transcript = """
        David Lee: We need to finalize the project timeline by Friday.
        Sarah Chen: I'll prepare the presentation slides by Thursday.
        Mike Wilson: The budget review is critical - we need to prioritize this.
        """
        
        print("📝 Testing with sample transcript...")
        result = ai_engine.process_transcript(sample_transcript, "Test Client", "Test Project")
        
        if result and 'summary' in result:
            print("✅ AI analysis completed successfully")
            print(f"📊 Summary: {result['summary'][:100]}...")
            
            if 'mood' in result:
                print(f"😊 Mood: {result['mood'].get('overall', 'Unknown')}")
            
            if 'action_items' in result:
                print(f"✅ Action Items: {len(result['action_items'])} found")
            
            return True
        else:
            print("❌ AI analysis failed - no summary returned")
            return False
            
    except Exception as e:
        print(f"❌ AI Engine test failed: {e}")
        return False

def test_flask_app():
    """Test if Flask app can start"""
    print("\n🌐 Testing Flask Application...")
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
        
        # Test if we can create app context
        with app.app_context():
            print("✅ Flask app context created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Meeting Summarizer - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("AI Engine", test_ai_engine),
        ("Flask Application", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application:")
        print("   python app.py")
        print("\n🌐 Then open: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        print("\n📋 Setup Checklist:")
        print("   1. Create .env file from env_template.txt")
        print("   2. Get API key from https://makersuite.google.com/app/apikey")
        print("   3. Update GEMINI_API_KEY in .env file")
        print("   4. Install dependencies: pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
