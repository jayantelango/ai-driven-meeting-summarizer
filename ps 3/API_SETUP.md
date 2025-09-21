# API Key Setup Guide

## Google Gemini API Key Setup

### Step 1: Get Your API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### Step 2: Set Up Environment Variable

#### Option A: Environment Variable (Recommended)
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"

# Windows Command Prompt
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY="your_api_key_here"
```

#### Option B: Direct Code Update (Quick Test)
Edit `ps 3/ai_engine.py` and uncomment line 26, then add your API key:
```python
# api_key = "YOUR_ACTUAL_API_KEY_HERE"
```

### Step 3: Test the API
Run the application and test with a meeting transcript to verify the API is working.

### Step 4: Create .env File (Optional)
Create a `.env` file in the `ps 3` directory:
```
GEMINI_API_KEY=your_api_key_here
```

## Troubleshooting

- **API Key Invalid**: Make sure you copied the complete API key
- **Quota Exceeded**: Check your Google Cloud billing and quotas
- **Permission Denied**: Ensure the API key has proper permissions

## Security Note
Never commit your API key to version control. Use environment variables or .env files that are gitignored.
