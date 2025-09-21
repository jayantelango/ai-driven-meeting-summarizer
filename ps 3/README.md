# 🧠 AI Meeting Summarizer

A powerful B2B enterprise application that transforms meeting transcripts into actionable insights using Google's Gemini AI.

## ✨ Features

- **AI-Powered Analysis**: Extract summaries, sentiment, tasks, and action items from meeting transcripts
- **Multiple Input Methods**: Text input, file upload (PDF, DOCX, TXT), and live recording
- **Task Management**: Visual task board with priority classification and status tracking
- **Email Integration**: Automatic notifications for critical tasks
- **Team Management**: Manage team members and their contact information
- **PDF Export**: Generate professional reports for stakeholders
- **AI Assistant**: Dual-mode assistant for application guidance and meeting analysis

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
python setup.py
```

### Option 2: Manual Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Copy the environment template
   cp env_template.txt .env
   
   # Edit .env file and add your API keys
   ```

4. **Get Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key to your `.env` file

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the Application**
   - Open your browser to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required: Google Gemini AI API Key
GEMINI_API_KEY=your_actual_api_key_here

# Optional: Email Configuration
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
NOTIFICATION_RECIPIENTS=admin@company.com,manager@company.com

# Optional: Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### API Key Setup

1. **Get Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated key

2. **Configure Email (Optional)**:
   - For Gmail: Use App Passwords (not your regular password)
   - Enable 2-factor authentication first
   - Generate an App Password in Google Account settings

## 📁 Project Structure

```
ps 3/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── ai_engine.py           # AI processing engine
├── file_processor.py      # File upload processing
├── knowledge_base.py      # Application knowledge base
├── demo_data.py           # Sample meeting data
├── requirements.txt       # Python dependencies
├── setup.py              # Automated setup script
├── env_template.txt      # Environment template
├── instance/             # Database files
├── templates/            # HTML templates
│   ├── index.html        # Main interface
│   └── dashboard.html    # Dashboard view
└── tests/                # Test files
```

## 🎯 Usage

### 1. Meeting Analysis

1. **Enter Context**: Provide client name and project name
2. **Add Transcript**: 
   - Paste text directly
   - Upload a file (PDF, DOCX, TXT)
   - Use live recording (browser-based)
3. **Analyze**: Click "Analyze Meeting" to get AI insights

### 2. Task Management

- View tasks organized by priority (Critical, Moderate, Normal)
- Track task status (Pending, In Progress, Completed)
- Assign tasks to team members
- Send email notifications for critical tasks

### 3. AI Assistant

- **Application Guide**: Ask questions about features and usage
- **Meeting Expert**: Analyze specific meeting content
- Access via the floating chat button

## 🔍 API Endpoints

- `POST /api/summarize` - Analyze meeting transcript
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/tasks` - List all tasks
- `PUT /api/tasks/<id>` - Update task status
- `POST /api/upload` - Upload and process files
- `POST /api/send-mail` - Send custom emails
- `POST /api/assistant` - AI assistant queries
- `GET /api/validate-setup` - Check configuration

## 🛠️ Troubleshooting

### Common Issues

1. **"AI Setup Required" Message**
   - Check your `.env` file has a valid `GEMINI_API_KEY`
   - Ensure the API key is not a placeholder value
   - Restart the application after adding the key

2. **Import Errors**
   - Make sure you're in the virtual environment
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Database Errors**
   - Delete the `instance/` folder and restart
   - Check file permissions in the project directory

4. **Email Not Working**
   - Verify email credentials in `.env`
   - Use App Passwords for Gmail
   - Check firewall/network settings

### Debug Mode

Run with debug logging:
```bash
export FLASK_DEBUG=True
python app.py
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 📊 Demo Data

The application includes sample meeting transcripts for testing:
- TechCorp Solutions - Digital Transformation
- GlobalBank Financial - Risk Management
- MedTech Innovations - Healthcare Platform
- RetailMax Corporation - E-commerce Modernization

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Use environment variables for production deployments
- Regularly rotate your API keys
- Implement proper authentication for production use

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the application logs
3. Create an issue with detailed error information

---

**Made with ❤️ for better meeting productivity**
