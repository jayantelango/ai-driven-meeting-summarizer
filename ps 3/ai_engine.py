import google.generativeai as genai
import os
import logging
from typing import Dict, List
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)

class AIEngine:
    def __init__(self):
        """Initialize the AI Engine with Gemini API."""
        logging.info("Initializing Gemini AI Engine...")
        
        # Get API key from environment variable or use fallback
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            logging.warning("GEMINI_API_KEY not found in environment variables")
            # Use fallback API key for testing
            api_key = "AIzaSyDWAKdoiqpzEgDWNu-ir1NRORnXLQ6uMl4"
            logging.info("Using fallback API key for testing")
        
        try:
            # Configure the Gemini API
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Test the API key with a simple request
            test_response = self.model.generate_content("Test")
            logging.info("Gemini AI Engine initialized successfully!")
        except Exception as e:
            logging.error(f"Failed to initialize Gemini AI: {str(e)}")
            # Set model to None for graceful degradation
            self.model = None
            logging.warning("AI Engine running in fallback mode")
    
    def process_transcript(self, transcript: str, client_name: str = None, project_name: str = None) -> Dict[str, any]:
        """
        Process meeting transcript using Gemini API to extract summary, action items, and tasks.
        
        Args:
            transcript (str): The raw meeting transcript
            
        Returns:
            Dict: Dictionary containing summary, action_items, and tasks
        """
        try:
            logging.info(f"Processing transcript of length: {len(transcript)} characters")
            
            # Check if AI model is available
            if not self.model:
                logging.warning("AI model not available, using fallback processing")
                return self._fallback_parsing(transcript)
            
            # Create a highly-detailed prompt for comprehensive meeting analysis with enhanced features
            # Build context-aware prompt based on client and project information
            context_intro = ""
            if client_name and project_name:
                context_intro = f"You are analyzing a meeting for the client {client_name} regarding the project {project_name}. With this context in mind, analyze the following transcript:\n\n"
            elif client_name:
                context_intro = f"You are analyzing a meeting for the client {client_name}. With this context in mind, analyze the following transcript:\n\n"
            elif project_name:
                context_intro = f"You are analyzing a meeting regarding the project {project_name}. With this context in mind, analyze the following transcript:\n\n"
            
            prompt = f"""You are an AI assistant specialized in analyzing meeting transcripts for B2B enterprise use. {context_intro}Analyze the following meeting transcript and return a single, valid JSON object with the exact structure specified below.

CRITICAL REQUIREMENTS:
- Return ONLY valid JSON, no additional text, explanations, or formatting
- Use the exact field names and structure provided
- Ensure all strings are properly escaped for JSON
- Focus on ACCURATE extraction of key points and tasks
- Ensure proper context understanding to avoid mis-assigning tasks

JSON STRUCTURE:
{{
  "summary": "A concise executive summary of the meeting, maximum 200 words. Focus on key outcomes and decisions.",
  "mood": {{
    "overall": "Positive/Negative/Neutral",
    "justification": "Brief explanation of the mood assessment based on language, tone, and outcomes"
  }},
  "action_items": [
    {{
      "task": "A clear description of the action item or task.",
      "assignee": "The exact name of the person responsible (use names as mentioned in transcript).",
      "assigned_by": "The person who assigned the task (if mentioned).",
      "deadline": "The specified deadline if mentioned, or 'Not specified'.",
      "priority": "High/Medium/Low based on urgency and importance mentioned.",
      "confidence": "A numerical confidence score from 0.0 to 1.0 for extraction accuracy."
    }}
  ],
  "tasks": [
    {{
      "task": "Detailed task description",
      "assigned_to": "Person responsible",
      "assigned_by": "Person who assigned it",
      "deadline": "Deadline if mentioned",
      "priority": "Critical/High/Medium/Low",
      "confidence": "High/Medium/Low"
    }}
  ],
  "participants": [
    {{
      "name": "Participant name as mentioned in transcript",
      "role": "Their role or title if mentioned",
      "key_contributions": ["Their main contributions or important statements"]
    }}
  ],
  "key_decisions": [
    "List of key decisions made during the meeting"
  ],
  "next_steps": [
    "Recommended follow-up actions"
  ],
  "remarks": [
    {{
      "person": "Name of person",
      "remark": "Important quote or observation"
    }}
  ]
}}

ANALYSIS GUIDELINES:

SUMMARY:
- Provide a clear, concise summary focusing on main outcomes
- Use professional, business-focused language
- Maximum 200 words

MOOD ANALYSIS:
- Assess overall meeting sentiment: Positive (productive, collaborative, successful), Negative (conflict, problems, setbacks), Neutral (routine, informational)
- Base assessment on language tone, outcomes, and participant engagement
- Provide brief justification for the mood assessment

ACTION ITEMS & TASKS:
- Extract ALL tasks, assignments, and commitments mentioned
- Use EXACT names as they appear in the transcript
- Priority: "Critical" (urgent/emergency), "High" (important/urgent), "Medium" (important), "Low" (standard)
- Confidence: "High" (explicit assignment), "Medium" (clear implication), "Low" (suggested/uncertain)
- If assignee is unclear, use "Unassigned"
- If deadline not mentioned, use "Not specified"

PARTICIPANTS:
- Identify all people mentioned in the transcript
- Include their roles if mentioned
- Note their key contributions

KEY DECISIONS:
- List concrete decisions, agreements, or resolutions made
- Use clear, concise statements

NEXT STEPS:
- Identify recommended follow-up actions
- Focus on practical, actionable items

REMARKS:
- Extract important quotes or observations from participants
- Focus on statements that provide insight or context

ACCURACY FOCUS:
- Double-check task assignments match the transcript
- Ensure context understanding to avoid mis-assignment
- Verify all names and details are accurate

Meeting transcript:
{transcript}

Return only the JSON object:"""
            
            # Generate response using Gemini
            logging.info("Sending request to Gemini API")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            logging.info("Received response from Gemini API")
            
            # Try to parse JSON response
            try:
                # Clean up the response text to extract JSON
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end != 0:
                    json_text = response_text[json_start:json_end]
                    result = json.loads(json_text)
                    logging.info("Successfully parsed JSON response from Gemini")
                    
                    # Ensure all required fields exist
                    if 'summary' not in result:
                        result['summary'] = 'No summary available.'
                    if 'action_items' not in result:
                        result['action_items'] = []
                    if 'key_decisions' not in result:
                        result['key_decisions'] = []
                    if 'next_steps' not in result:
                        result['next_steps'] = []
                    
                    logging.info(f"Processed transcript successfully - Found {len(result.get('action_items', []))} action items, {len(result.get('key_decisions', []))} decisions, {len(result.get('next_steps', []))} next steps")
                    return result
                else:
                    # Fallback parsing if JSON structure is not found
                    logging.warning("JSON structure not found in response, using fallback parsing")
                    return self._fallback_parsing(response_text)
                    
            except json.JSONDecodeError:
                # Fallback to manual parsing
                logging.warning("JSON decode error, using fallback parsing")
                return self._fallback_parsing(response_text)
            
        except Exception as e:
            logging.error(f"Error processing transcript: {str(e)}")
            # Return a structured error or raise the exception
            raise e
    
    def _fallback_parsing(self, text: str) -> Dict[str, any]:
        """
        Fallback method to parse unstructured response.
        
        Args:
            text (str): Raw response text from Gemini
            
        Returns:
            Dict: Parsed structure with summary, action_items, and tasks
        """
        result = {
            'summary': '',
            'action_items': [],
            'participants': [],
            'key_decisions': [],
            'next_steps': []
        }
        
        try:
            # Split text into lines for analysis
            lines = text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Detect section headers
                line_lower = line.lower()
                if 'summary' in line_lower and ':' in line:
                    current_section = 'summary'
                    # Extract summary if it's on the same line
                    if ':' in line:
                        summary_part = line.split(':', 1)[1].strip()
                        if summary_part:
                            result['summary'] = summary_part
                elif 'action' in line_lower and 'item' in line_lower:
                    current_section = 'action_items'
                elif 'decision' in line_lower:
                    current_section = 'key_decisions'
                elif 'next' in line_lower and 'step' in line_lower:
                    current_section = 'next_steps'
                elif current_section:
                    # Process content based on current section
                    if current_section == 'summary' and not result['summary']:
                        result['summary'] = line
                    elif current_section in ['action_items', 'key_decisions', 'next_steps']:
                        # Clean up bullet points and numbering
                        clean_line = re.sub(r'^[\d\.\-\*\+]\s*', '', line)
                        if clean_line and len(clean_line) > 3:
                            result[current_section].append(clean_line)
            
            # Set default summary if none found
            if not result['summary']:
                # Use first meaningful sentence as summary
                sentences = [line.strip() for line in lines if line.strip() and len(line.strip()) > 20]
                if sentences:
                    result['summary'] = sentences[0][:200] + '...' if len(sentences[0]) > 200 else sentences[0]
                else:
                    result['summary'] = "Meeting transcript processed successfully."
                    
        except Exception as e:
            result['summary'] = f"Parsed with limitations: {text[:100]}..."
            
        return result
    
    # Legacy methods for backward compatibility
    def summarize(self, meeting_content: str) -> str:
        """Legacy method for backward compatibility."""
        result = self.process_transcript(meeting_content)
        return result['summary']
    
    def extract_action_items(self, meeting_content: str) -> List[str]:
        """Legacy method for backward compatibility."""
        result = self.process_transcript(meeting_content)
        # Convert action_items objects to simple strings for backward compatibility
        if result.get('action_items'):
            return [item.get('task', str(item)) if isinstance(item, dict) else str(item) for item in result['action_items']]
        return []