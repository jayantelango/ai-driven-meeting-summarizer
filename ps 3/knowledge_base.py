def get_app_features():
    """
    Returns comprehensive information about the AI Meeting Summarizer application features.
    This knowledge base is used by the AI assistant to provide accurate guidance about the application.
    """
    return """
    This application is an AI-powered Meeting Summarizer for B2B enterprises.
    
    CORE FEATURES:
    - Users can input a client name, project name, and a meeting transcript
    - Inputs can be pasted text, live voice recording, or uploaded files (PDF, DOCX, TXT)
    - The AI analyzes the transcript to produce a concise summary, assess the meeting's mood, identify key remarks about individuals, and extract a detailed list of tasks
    - Each task is assigned a priority (Critical, Moderate, Normal), assigned to a person, and includes who assigned it and any deadline
    - A task management board allows users to see all tasks categorized by status (Pending, In Progress, Completed)
    - Users can interact with an AI assistant to ask questions about the application's features or the content of the summarized meeting
    - The application can send email alerts for critical tasks
    - Users can export a PDF report of the task board
    
    INPUT METHODS:
    1. Manual Text Input: Users can paste meeting transcripts directly into the text area
    2. File Upload: Supports PDF, DOCX, TXT, and MP3 files (MP3 shows placeholder message)
    3. Demo Mode: Pre-loaded sample meetings for testing and demonstration
    
    AI ANALYSIS CAPABILITIES:
    - Meeting Summary: Concise overview of key points and decisions
    - Sentiment Analysis: Overall mood assessment (Positive/Negative/Neutral) with justification
    - Task Extraction: Identifies action items with assignee, priority, and deadlines
    - Remark Analysis: Extracts feedback and comments about specific individuals
    - Priority Classification: Automatically categorizes tasks as Critical, Moderate, or Normal
    
    TASK MANAGEMENT:
    - Visual task board with three columns: Pending, In Progress, Completed
    - Drag-and-drop functionality to move tasks between statuses
    - Priority indicators with color coding
    - Assignee management with team member database
    - Email notifications for critical priority tasks
    
    AI ASSISTANT:
    - Dual-mode operation: Application guide and meeting content expert
    - Application Guide: Answers questions about features, setup, and usage
    - Meeting Expert: Analyzes specific meeting content when transcript is provided
    - Context-aware responses based on available information
    
    EMAIL INTEGRATION:
    - Automatic alerts for critical priority tasks
    - Custom email sending functionality
    - Team member email management
    - Configurable notification recipients
    
    EXPORT CAPABILITIES:
    - PDF export of task board with client/project information
    - Structured reports with task categorization
    - Professional formatting for stakeholder sharing
    
    SETUP REQUIREMENTS:
    - Google Gemini API key for AI functionality
    - Email configuration for notifications (optional)
    - Database automatically created on first run
    - Default team members created for immediate use
    
    TECHNICAL FEATURES:
    - Flask-based web application
    - SQLite database with SQLAlchemy ORM
    - RESTful API endpoints
    - File processing for multiple formats
    - Error handling and logging
    - Responsive web interface
    """