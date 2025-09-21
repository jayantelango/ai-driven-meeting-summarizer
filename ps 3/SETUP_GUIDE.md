# AI Meeting Summarizer - Setup Guide

## 🚀 Quick Start

### 1. Get Your Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Configure the Application
1. Open the `.env` file in the project root
2. Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

### 5. Open in Browser
Navigate to: http://localhost:5000

## 🧪 Test Your Setup
Run the test script to verify everything is working:
```bash
python test_setup.py
```

## 📋 Features

### ✅ What's Working Now:
- **Meeting Analysis**: Upload transcripts or paste text
- **AI-Powered Summaries**: Get executive summaries
- **Mood Analysis**: Detect meeting sentiment with color coding
- **Task Extraction**: Automatically identify action items and assignments
- **Priority Classification**: Tasks are categorized as Critical/High/Medium/Low
- **Participant Tracking**: Identify who said what
- **Key Decisions**: Extract important decisions made
- **Color-Coded Results**: Visual indicators for mood and priority levels

### 🎨 Visual Features:
- **Mood Badges**: Green (Positive), Red (Negative), Yellow (Neutral)
- **Priority Badges**: Red (Critical/High), Yellow (Medium), Green (Low)
- **Interactive UI**: Modern, responsive design
- **Real-time Processing**: Live analysis with loading indicators

## 🔧 Troubleshooting

### API Key Issues:
- Make sure your API key is valid and active
- Check that it's properly set in the `.env` file
- Verify you have access to the Gemini API

### Common Errors:
1. **"API key not valid"**: Update your API key in `.env`
2. **"AI service not available"**: Check your internet connection
3. **"No transcript found"**: Make sure you've entered text or uploaded a file

## 📁 File Support
- **Text Files**: .txt
- **Documents**: .pdf, .docx
- **Audio**: .mp3, .wav (requires ffmpeg)

## 🎯 Sample Usage

1. **Fill in the form**:
   - Client Name: "TechCorp Solutions"
   - Project Name: "Q4 Dashboard Redesign"
   - Meeting Transcript: (paste or upload)

2. **Click "Analyze Meeting"**

3. **View Results**:
   - Executive Summary
   - Mood Analysis (with color coding)
   - Action Items (with priorities)
   - Task Assignments
   - Key Decisions
   - Next Steps

## 🚀 Advanced Features

### Task Management:
- View all tasks in organized columns
- Track progress (Pending, In Progress, Completed)
- Filter by priority and assignee

### Project Management:
- Create and manage projects
- Track meeting history
- Export reports

### Analytics:
- Meeting effectiveness metrics
- Task completion rates
- Team productivity insights

## 📞 Support

If you encounter any issues:
1. Check the console for error messages
2. Verify your API key is correct
3. Ensure all dependencies are installed
4. Try the test script: `python test_setup.py`

## 🎉 You're Ready!

Your AI Meeting Summarizer is now configured and ready to analyze meetings with advanced AI capabilities, color-coded results, and comprehensive task management!
