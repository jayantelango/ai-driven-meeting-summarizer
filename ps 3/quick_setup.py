#!/usr/bin/env python3
"""
Quick Setup Script - Manual API Key Configuration
This script helps you set up your API key manually.
"""

import os
from pathlib import Path

def main():
    print("🔑 Quick API Key Setup")
    print("=" * 40)
    print()
    
    # Check if .env exists
    if not Path('.env').exists():
        print("❌ .env file not found!")
        print("   Please run: copy env_template.txt .env")
        return
    
    print("📋 To set up your API key:")
    print("1. Get your API key from: https://makersuite.google.com/app/apikey")
    print("2. Open the .env file in a text editor")
    print("3. Replace 'your_gemini_api_key_here' with your actual key")
    print("4. Save the file")
    print("5. Run: python app.py")
    print()
    
    # Show current .env content
    with open('.env', 'r') as f:
        content = f.read()
    
    print("📄 Current .env file content:")
    print("-" * 40)
    print(content)
    print("-" * 40)
    print()
    
    # Check if API key is still placeholder
    if 'your_gemini_api_key_here' in content:
        print("⚠️  API key is still set to placeholder value")
        print("   Please update the GEMINI_API_KEY in .env file")
    else:
        print("✅ API key appears to be configured")
        print("   You can now run: python app.py")

if __name__ == "__main__":
    main()
