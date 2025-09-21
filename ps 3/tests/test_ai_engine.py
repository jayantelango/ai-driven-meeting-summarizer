import unittest
import os
from unittest.mock import patch, MagicMock
from ai_engine import AIEngine

class TestAIEngine(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Mock the environment variable
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            self.ai_engine = AIEngine()
    
    @patch('ai_engine.genai.GenerativeModel')
    def test_initialization(self, mock_model):
        """Test AI engine initialization."""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            engine = AIEngine()
            self.assertIsNotNone(engine.model)
    
    def test_initialization_no_api_key(self):
        """Test initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                AIEngine()
    
    @patch('ai_engine.genai.GenerativeModel')
    def test_process_transcript_success(self, mock_model_class):
        """Test successful transcript processing."""
        # Mock the model and response
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "summary": "Test meeting summary",
            "sentiment": {"overall": "Positive", "justification": "Good discussion"},
            "tasks": [{"task": "Complete report", "assigned_to": "John"}],
            "remarks": [{"person": "Sarah", "remark": "Great work"}],
            "action_items": ["Follow up on budget"]
        }
        '''
        mock_model.generate_content.return_value = mock_response
        
        # Create engine with mocked model
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            engine = AIEngine()
            engine.model = mock_model
            
            result = engine.process_transcript("Test meeting transcript")
            
            self.assertIn('summary', result)
            self.assertIn('sentiment', result)
            self.assertIn('tasks', result)
            self.assertIn('remarks', result)
            self.assertIn('action_items', result)
    
    def test_fallback_parsing(self):
        """Test fallback parsing functionality."""
        test_text = """
        Summary: This is a test meeting
        Action Items:
        - Complete the report
        - Review the budget
        """
        
        result = self.ai_engine._fallback_parsing(test_text)
        
        self.assertIn('summary', result)
        self.assertIn('action_items', result)
        self.assertIn('participants', result)
        self.assertIn('key_decisions', result)
        self.assertIn('next_steps', result)

if __name__ == '__main__':
    unittest.main()
