import os
import sys
import json
import io
import logging
from flask import Flask, request, jsonify, render_template, send_file
from dotenv import load_dotenv
from datetime import datetime
from models import db, Project, TeamMember, MeetingSummary, TaskAssignment, MeetingTemplate
from flask_mail import Mail, Message
import google.generativeai as genai
from file_processor import process_file
from knowledge_base import get_app_features
from fpdf import FPDF
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
import docx
from docx.shared import Inches
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'meetings.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

# --- INITIALIZATION ---
db.init_app(app)
mail = Mail(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_gemini():
    try:
        # Get API key from environment variable
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            logging.warning("GEMINI_API_KEY not found in environment variables")
            # Using provided API key for testing
            api_key = "AIzaSyBS6pnTbIsen01AK1nbqGp-wE8GQfc1rnA"
            if not api_key:
                return None
            
        if len(api_key) < 20:  # Basic validation
            logging.warning("API key appears to be invalid (too short)")
            return None
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test the API key with a simple request
        test_response = model.generate_content("Test")
        logging.info("Gemini AI configured and tested successfully with provided API key")
        return model
    except Exception as e:
        logging.error(f"Failed to initialize Gemini AI: {e}")
        return None

model = initialize_gemini()

# --- MAIN ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/summarize', methods=['POST'])
def summarize_meeting():
    # Use fallback analysis if AI is not available
    if not model:
        logging.warning("AI model not available, using fallback analysis")
        data = request.get_json()
        transcript = data.get('transcript', '')
        client_name = data.get('client_name', 'Unknown Client')
        project_name = data.get('project_name', 'Unknown Project')
        
        # Create fallback analysis
        result = create_fallback_analysis(transcript, client_name, project_name)
        return jsonify(result)
    
    try:
        data = request.get_json()
        transcript = data.get('transcript', '')
        client_name = data.get('client_name', '')
        project_name = data.get('project_name', '')

        prompt = f"""
        Analyze this business meeting transcript for client '{client_name}' on project '{project_name}'. Return a single, valid JSON object with the exact structure specified below.

        TRANSCRIPT:
        {transcript}

        JSON STRUCTURE:
        {{
          "summary": "An executive summary, max 300 words.",
          "sentiment": {{ "overall": "Positive/Negative/Neutral", "justification": "A brief reason." }},
          "tasks": [ {{ "task": "Description", "assigned_to": "Name", "assigned_by": "Name", "deadline": "Date", "priority": "Critical/Moderate/Normal" }} ],
          "action_items": [ {{ "person": "Name", "remark": "Feedback or comment." }} ]
        }}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace('```json', '').replace('```', '')
        result = json.loads(response_text)
        
        # --- Database Logic ---
        project = Project.query.filter_by(name=project_name, client=client_name).first()
        if not project:
            project = Project(name=project_name, client=client_name)
            db.session.add(project)
            db.session.flush()

        summary = MeetingSummary(transcript=transcript, ai_result=result, project_id=project.id)
        db.session.add(summary)
        db.session.flush() # Flush to get summary.id for tasks

        if result.get('tasks'):
            for task_data in result['tasks']:
                assignee_name = task_data.get('assigned_to', 'Unassigned')
                assignee = TeamMember.query.filter_by(name=assignee_name).first()
                
                task = TaskAssignment(
                    task_description=task_data.get('task', ''),
                    priority=task_data.get('priority', 'normal').lower(),
                    status='pending',
                    project_id=project.id,
                    meeting_id=summary.id,
                    assignee_id=assignee.id if assignee else None
                )
                db.session.add(task)
                
                if task.priority == 'critical':
                    send_critical_task_email(task_data, client_name, project_name)
        
        db.session.commit()
        return jsonify(result)

    except Exception as e:
        logging.error(f"Error in /api/summarize: {e}")
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500

def create_fallback_analysis(transcript, client_name, project_name):
    """Create a detailed analysis when AI is not available"""
    import re
    
    # Extract basic information
    words = transcript.lower().split()
    
    # Simple sentiment analysis
    positive_words = ['good', 'great', 'excellent', 'positive', 'success', 'complete', 'finished', 'ready', 'done', 'progress']
    negative_words = ['problem', 'issue', 'error', 'failed', 'critical', 'urgent', 'delay', 'concern', 'worry', 'difficult']
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    if positive_count > negative_count:
        mood = "Positive"
        mood_justification = "Meeting had more positive language and successful outcomes"
    elif negative_count > positive_count:
        mood = "Negative" 
        mood_justification = "Meeting contained several issues and problems to address"
    else:
        mood = "Neutral"
        mood_justification = "Meeting had balanced discussion of topics"
    
    # Extract key information from transcript
    lines = [line.strip() for line in transcript.split('\n') if line.strip()]
    
    # Extract names mentioned in the meeting
    names = set()
    for line in lines:
        name_matches = re.findall(r'[A-Z][a-z]+:', line)
        names.update([name.rstrip(':') for name in name_matches])
    
    # Extract action items and key points
    action_items = []
    key_decisions = []
    next_steps = []
    
    # Split transcript into individual statements
    statements = []
    for line in lines:
        # Split by common separators and clean up
        parts = re.split(r'[.!?]+', line)
        for part in parts:
            part = part.strip()
            if part and len(part) > 10:  # Only meaningful statements
                statements.append(part)
    
    for statement in statements:
        statement_lower = statement.lower()
        
        # Extract action items from individual statements
        if any(keyword in statement_lower for keyword in ['will', 'need to', 'should', 'must', 'finish', 'complete', 'schedule', 'test', 'help with']):
            # Extract assignee name
            assignee = 'Unassigned'
            name_match = re.search(r'^([A-Z][a-z]+):', statement)
            if name_match:
                assignee = name_match.group(1)
            
            # Determine priority
            if any(word in statement_lower for word in ['critical', 'urgent', 'asap', 'immediately', 'friday']):
                priority = 'high'
            elif any(word in statement_lower for word in ['important', 'priority', 'soon', 'thursday']):
                priority = 'medium'
            else:
                priority = 'low'
            
            # Clean up the task description
            task_desc = re.sub(r'^[A-Z][a-z]+:\s*', '', statement).strip()
            if task_desc and len(task_desc) > 10:
                action_items.append({
                    'task': task_desc,
                    'assignee': assignee,
                    'assigned_by': 'Meeting',
                    'deadline': 'Not specified',
                    'priority': priority,
                    'confidence': 'Medium'
                })
        
        # Extract key decisions
        if any(keyword in statement_lower for keyword in ['decided', 'agreed', 'concluded', 'final', 'approved', 'confirmed', 'perfect']):
            key_decisions.append(statement.strip())
        
        # Extract next steps
        if any(keyword in statement_lower for keyword in ['next', 'follow up', 'schedule', 'plan', 'prepare', 'finalize']):
            next_steps.append(statement.strip())
    
    # Create a more detailed summary based on actual content
    summary_parts = []
    summary_parts.append(f"Meeting for {client_name} regarding {project_name}.")
    
    if names:
        summary_parts.append(f"Participants included: {', '.join(list(names)[:3])}.")
    
    if action_items:
        summary_parts.append(f"Key tasks identified: {len(action_items)} action items including {action_items[0]['task'][:50]}...")
    
    if key_decisions:
        summary_parts.append(f"Important decisions made: {key_decisions[0][:50]}...")
    
    summary_parts.append(f"Overall meeting mood was {mood.lower()} with focus on project deliverables and timeline.")
    
    summary = " ".join(summary_parts)
    
    # If no key decisions found, add generic ones
    if not key_decisions:
        key_decisions = [
            'Project timeline and deliverables discussed',
            'Resource allocation planned',
            'Next meeting scheduled'
        ]
    
    # If no next steps found, add generic ones
    if not next_steps:
        next_steps = [
            'Follow up on action items',
            'Prepare progress report',
            'Schedule next review meeting'
        ]
    
    # Extract action items from transcript
    action_items = []
    participants = set()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Extract speaker name (pattern: "Name: content")
        speaker_match = re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):\s*(.+)', line)
        if speaker_match:
            speaker = speaker_match.group(1).strip()
            content = speaker_match.group(2).strip()
            participants.add(speaker)
            
            # Look for action item patterns (feedback, comments, suggestions, etc.)
            action_item_keywords = [
                'feedback', 'comment', 'suggestion', 'note', 'remark', 'observation',
                'think', 'believe', 'feel', 'consider', 'recommend', 'suggest',
                'concern', 'worry', 'issue', 'problem', 'good', 'great', 'excellent',
                'bad', 'wrong', 'improve', 'better', 'change', 'update'
            ]
            
            content_lower = content.lower()
            if any(keyword in content_lower for keyword in action_item_keywords):
                # Try to identify who the remark is directed to
                given_to = 'General'
                for participant in participants:
                    if participant != speaker and participant.lower() in content_lower:
                        given_to = participant
                        break
                
                # Also check for direct addressing patterns
                direct_patterns = [
                    r'to\s+([A-Z][a-z]+)',
                    r'@([A-Z][a-z]+)',
                    r'for\s+([A-Z][a-z]+)',
                    r'([A-Z][a-z]+),?\s+you'
                ]
                
                for pattern in direct_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match and match.group(1):
                        given_to = match.group(1)
                        break
                
                action_items.append({
                    'person': speaker,
                    'remark': content,
                    'given_to': given_to
                })
    
    # If no action items found, add a generic one
    if not action_items:
        action_items = [{'person': 'System', 'remark': 'Meeting analysis completed using fallback processing', 'given_to': 'General'}]
    
    return {
        'summary': summary,
        'mood': {
            'overall': mood,
            'justification': mood_justification
        },
        'action_items': action_items[:10],  # Limit to 10 action items
        'key_decisions': key_decisions[:3],  # Limit to 3 decisions
        'next_steps': next_steps[:3]  # Limit to 3 steps
    }

# --- HELPER & OTHER ROUTES ---
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    try:
        text_content = process_file(file.stream, file.filename)
        return jsonify({"transcript": text_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/assistant', methods=['POST'])
def meeting_assistant():
    data = request.get_json()
    question = data.get('question')
    context = data.get('context')
    
    if not context: # Answer about the app
        prompt = f"Based on this app description: {get_app_features()}, answer the user's question: {question}"
    else: # Answer about the meeting
        prompt = f"Based on the following meeting: {context}, answer the user's question: {question}"
        
    response = model.generate_content(prompt)
    return jsonify({'answer': response.text})

def send_critical_task_email(task_data, client, project):
    recipients = os.environ.get('NOTIFICATION_RECIPIENTS', '').split(',')
    if not recipients or not recipients[0]:
        return
    msg = Message(
        subject=f"CRITICAL TASK ALERT: {project}",
        recipients=recipients,
        body=f"A critical priority task was detected for project '{project}' with client '{client}':\n\nTask: {task_data.get('task')}\nAssigned to: {task_data.get('assigned_to')}"
    )
    mail.send(msg)

@app.route('/api/download-meeting-pdf', methods=['POST'])
def download_meeting_pdf():
    """Generate comprehensive PDF report with meeting summary and AI analysis"""
    try:
        data = request.get_json()
        logging.info(f"PDF generation request received")
        
        client_name = data.get('client_name', 'Unknown Client')
        project_name = data.get('project_name', 'Unknown Project')
        transcript = data.get('transcript', '')
        meeting_data = data.get('meeting_data', {})
        
        logging.info(f"Processing PDF for: {client_name} - {project_name}")
        
        # Create PDF using ReportLab
        pdf_output = io.BytesIO()
        doc = SimpleDocTemplate(pdf_output, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        normal_style.spaceAfter = 6
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph("AI Meeting Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Header Information
        story.append(Paragraph("Meeting Information", heading_style))
        story.append(Paragraph(f"<b>Client:</b> {client_name}", normal_style))
        story.append(Paragraph(f"<b>Project:</b> {project_name}", normal_style))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Meeting Summary
        if meeting_data.get('summary'):
            story.append(Paragraph("Meeting Summary", heading_style))
            story.append(Paragraph(meeting_data['summary'], normal_style))
            story.append(Spacer(1, 15))
        
        # Mood Analysis
        if meeting_data.get('mood'):
            story.append(Paragraph("Mood Analysis", heading_style))
            mood = meeting_data['mood']
            mood_text = f"Overall Mood: {mood.get('overall', 'Unknown')}"
            if mood.get('justification'):
                mood_text += f"<br/>Justification: {mood['justification']}"
            story.append(Paragraph(mood_text, normal_style))
            story.append(Spacer(1, 15))
        
        # Action Items
        if meeting_data.get('action_items'):
            story.append(Paragraph("Action Items", heading_style))
            action_items = meeting_data['action_items']
            if action_items:
                for i, item in enumerate(action_items[:10], 1):  # Limit to 10 items
                    item_text = f"{i}. {item.get('task', 'Unnamed Task')}"
                    if item.get('assignee'):
                        item_text += f" (Assigned to: {item['assignee']})"
                    if item.get('priority'):
                        item_text += f" [Priority: {item['priority']}]"
                    story.append(Paragraph(item_text, normal_style))
            else:
                story.append(Paragraph("No action items identified", normal_style))
            story.append(Spacer(1, 15))
        
        # Key Decisions
        if meeting_data.get('key_decisions'):
            story.append(Paragraph("Key Decisions", heading_style))
            decisions = meeting_data['key_decisions']
            if decisions:
                for i, decision in enumerate(decisions[:5], 1):  # Limit to 5 decisions
                    story.append(Paragraph(f"{i}. {decision}", normal_style))
            else:
                story.append(Paragraph("No key decisions identified", normal_style))
            story.append(Spacer(1, 15))
        
        # Next Steps
        if meeting_data.get('next_steps'):
            story.append(Paragraph("Next Steps", heading_style))
            next_steps = meeting_data['next_steps']
            if next_steps:
                for i, step in enumerate(next_steps[:5], 1):  # Limit to 5 steps
                    story.append(Paragraph(f"{i}. {step}", normal_style))
            else:
                story.append(Paragraph("No next steps identified", normal_style))
            story.append(Spacer(1, 15))
        
        # Participants
        if meeting_data.get('participants'):
            story.append(Paragraph("Participants", heading_style))
            participants = meeting_data['participants']
            if participants:
                story.append(Paragraph(", ".join(participants), normal_style))
            else:
                story.append(Paragraph("No participants identified", normal_style))
            story.append(Spacer(1, 15))
        
        # Original Transcript (truncated)
        if transcript:
            story.append(Paragraph("Original Transcript (Excerpt)", heading_style))
            # Truncate transcript to avoid very long PDFs
            transcript_excerpt = transcript[:2000] + "..." if len(transcript) > 2000 else transcript
            story.append(Paragraph(transcript_excerpt, normal_style))
        
        # Build PDF
        doc.build(story)
        pdf_output.seek(0)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_client = "".join(c for c in client_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_project = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"Meeting_Report_{safe_client}_{safe_project}_{timestamp}.pdf"
        
        return send_file(
            pdf_output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logging.error(f"Error generating PDF: {e}")
        return jsonify({"error": "Failed to generate PDF report"}), 500

# --- DB INITIALIZATION ---
def initialize_database():
    with app.app_context():
        db.create_all()
        if TeamMember.query.count() == 0:
            default_members = [
                TeamMember(name="Sarah Johnson", role="Project Manager", email="sarah.j@example.com"),
                TeamMember(name="Mike Chen", role="Developer", email="mike.c@example.com")
            ]
            db.session.bulk_save_objects(default_members)
            db.session.commit()
            logging.info("Database seeded with default team members.")

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5000)
