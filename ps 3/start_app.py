#!/usr/bin/env python3
"""
Simple script to start the AI Meeting Summarizer
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("🚀 Starting AI Meeting Summarizer...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(debug=True, port=5000, host='127.0.0.1', use_reloader=False)
    
except Exception as e:
    print(f"❌ Error starting the app: {e}")
    import traceback
    traceback.print_exc()
