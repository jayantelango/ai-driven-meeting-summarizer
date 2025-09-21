import os
from dotenv import load_dotenv

def test_api_key():
    """Test if the GEMINI_API_KEY is properly configured."""
    print("🔍 Testing GEMINI_API_KEY configuration...")
    print("=" * 50)
    
    # Load environment variables from .env file
    print("📁 Loading .env file...")
    load_dotenv()
    
    # Attempt to get the API key
    print("🔑 Attempting to retrieve GEMINI_API_KEY...")
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        # Check if it's still the placeholder value
        if api_key == 'your_gemini_api_key_here':
            print("❌ ERROR: GEMINI_API_KEY is still set to placeholder value!")
            print("   The .env file contains: 'your_gemini_api_key_here'")
            print("   You need to replace this with your actual Google Gemini API key.")
            print("\n🔧 How to fix:")
            print("   1. Go to https://makersuite.google.com/app/apikey")
            print("   2. Create a new API key")
            print("   3. Copy the key and replace 'your_gemini_api_key_here' in the .env file")
            print("   4. Save the .env file and run this test again")
            return False
        else:
            print("✅ SUCCESS: GEMINI_API_KEY found!")
            print(f"   Key length: {len(api_key)} characters")
            print(f"   Key starts with: {api_key[:10]}...")
            print("   Your AI features should work properly now!")
            return True
    else:
        print("❌ ERROR: GEMINI_API_KEY not found!")
        print("\n🔍 Troubleshooting steps:")
        print("   1. Check if .env file exists in the current directory")
        print("   2. Verify the variable name is exactly 'GEMINI_API_KEY' (case-sensitive)")
        print("   3. Make sure there are no spaces around the = sign")
        print("   4. Ensure the .env file is in the same directory as this script")
        
        # Check if .env file exists
        if os.path.exists('.env'):
            print("\n📄 .env file found in current directory")
            print("   The file exists but GEMINI_API_KEY variable is missing or misnamed")
        else:
            print("\n📄 .env file NOT found in current directory")
            print("   You need to create a .env file with your API key")
            print("   Example .env file content:")
            print("   GEMINI_API_KEY=your_actual_api_key_here")
        
        return False

if __name__ == "__main__":
    print("🚀 AI Meeting Summarizer - API Key Test")
    print("=" * 50)
    
    success = test_api_key()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All good! Your API key is properly configured.")
    else:
        print("⚠️  Please fix the API key configuration and run this test again.")
    
    print("\nPress Enter to exit...")
    input()