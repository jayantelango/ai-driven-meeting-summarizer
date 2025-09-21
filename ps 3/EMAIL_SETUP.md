# Email Configuration Instructions for AI Meeting Summarizer

## Setup Instructions:

### 1. Gmail App Password Setup (Recommended):
1. Go to Google Account settings (myaccount.google.com)
2. Navigate to Security > 2-Step Verification
3. At the bottom, click "App passwords"
4. Select "Mail" and your device
5. Copy the generated 16-character password

### 2. Update .env File:
Replace the placeholder values in your .env file:

```
MAIL_USERNAME=your-actual-gmail@gmail.com
MAIL_PASSWORD=your-16-character-app-password
NOTIFICATION_RECIPIENTS=manager@company.com,team-lead@company.com,project-manager@company.com
```

### 3. Testing the Email Feature:

The system will automatically send email alerts when:
- A meeting is processed through the AI summarizer
- Any task is classified as "Critical" priority
- The AI detects urgent language like "must", "ASAP", "critical"

### 4. Email Content:
Critical task alerts include:
- Client and project information
- Task description and priority
- Assigned person and deadline
- Confidence level
- Professional formatting with emojis

### 5. Demo Test:
Use the "🚀 Load Demo Meeting" button to load a meeting with critical tasks,
then click "Summarize Meeting" to trigger email notifications.

### Security Notes:
- Never commit your actual email credentials to version control
- Use app passwords instead of your regular Gmail password
- Keep the .env file in your .gitignore
- Consider using environment variables in production

### Alternative SMTP Providers:
For production use, consider:
- SendGrid
- Amazon SES
- Mailgun
- Office 365 SMTP

The current configuration is set up for Gmail SMTP, but can be easily
modified for other providers by updating the MAIL_SERVER and MAIL_PORT
settings in app.py.