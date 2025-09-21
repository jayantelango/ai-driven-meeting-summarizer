#!/usr/bin/env python3
"""
Test script to verify file upload functionality
"""

import requests
import os

def test_file_upload():
    """Test the file upload endpoint"""
    
    # Create a test file
    test_content = """Meeting: Project Review
Sarah: We need to complete the website by Friday
Mike: I will finish the backend integration
Lisa: The UI design is ready
John: We should also test the mobile responsiveness
Sarah: Good point, lets schedule testing for Thursday"""
    
    with open('test_upload.txt', 'w') as f:
        f.write(test_content)
    
    try:
        # Test file upload
        url = 'http://localhost:5000/api/upload'
        with open('test_upload.txt', 'rb') as f:
            files = {'file': ('test_upload.txt', f, 'text/plain')}
            response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ File upload successful!")
            return True
        else:
            print("❌ File upload failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists('test_upload.txt'):
            os.remove('test_upload.txt')

if __name__ == "__main__":
    print("📁 File Upload Tester")
    print("=" * 30)
    test_file_upload()
