import unittest
import json
from app import app, db, MeetingSummary

class TestMeetingSummarizer(unittest.TestCase):
    def setUp(self):
        """Set up test client and database."""
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Create test database
        db.create_all()
    
    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index_route(self):
        """Test the main page loads correctly."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_summarize_endpoint_success(self):
        """Test successful transcript processing."""
        test_transcript = "This is a test meeting. John will complete the report by Friday. Sarah needs to review the budget."
        
        response = self.app.post('/api/summarize', 
                               json={
                                   'transcript': test_transcript,
                                   'client_name': 'Test Client',
                                   'project_name': 'Test Project'
                               },
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Check response structure
        self.assertIn('summary', data)
        self.assertIn('action_items', data)
        self.assertIn('key_decisions', data)
        self.assertIn('next_steps', data)
    
    def test_summarize_endpoint_empty_transcript(self):
        """Test empty transcript handling."""
        response = self.app.post('/api/summarize', 
                               json={
                                   'transcript': '',
                                   'client_name': 'Test Client',
                                   'project_name': 'Test Project'
                               },
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_summarize_endpoint_no_content(self):
        """Test missing transcript handling."""
        response = self.app.post('/api/summarize', 
                               json={},
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_summarize_endpoint_too_long(self):
        """Test transcript length validation."""
        long_transcript = "A" * 100001  # Over the 100k limit
        
        response = self.app.post('/api/summarize', 
                               json={
                                   'transcript': long_transcript,
                                   'client_name': 'Test Client',
                                   'project_name': 'Test Project'
                               },
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_meetings_endpoint(self):
        """Test meetings retrieval."""
        # First create a summary
        test_transcript = "Test meeting content"
        self.app.post('/api/summarize', 
                     json={
                         'transcript': test_transcript,
                         'client_name': 'Test Client',
                         'project_name': 'Test Project'
                     },
                     content_type='application/json')
        
        # Then get meetings
        response = self.app.get('/api/meetings')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIsInstance(data, list)
    
    def test_database_persistence(self):
        """Test that summaries are saved to database."""
        test_transcript = "Database test meeting"
        
        # Process transcript
        response = self.app.post('/api/summarize', 
                               json={
                                   'transcript': test_transcript,
                                   'client_name': 'Test Client',
                                   'project_name': 'Test Project'
                               },
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Check database
        summary = MeetingSummary.query.first()
        self.assertIsNotNone(summary)
        self.assertEqual(summary.transcript, test_transcript)

if __name__ == '__main__':
    unittest.main()
