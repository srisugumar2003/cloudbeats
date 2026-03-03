#!/usr/bin/env python3
"""
Test upload functionality
"""

import requests
import os

def test_upload():
    """Test the upload functionality"""
    print("🧪 Testing Upload Functionality...")
    print("=" * 40)
    
    # Check if the app is running
    try:
        response = requests.get('http://localhost:5000')
        if response.status_code == 200:
            print("✅ Application is running")
        else:
            print(f"❌ Application returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to application: {e}")
        return False
    
    # Check if uploads directory exists
    uploads_dir = 'uploads'
    if os.path.exists(uploads_dir):
        print("✅ Uploads directory exists")
    else:
        print("❌ Uploads directory missing")
        os.makedirs(uploads_dir, exist_ok=True)
        print("✅ Created uploads directory")
    
    # Check if database exists
    if os.path.exists('songs.db'):
        print("✅ Database exists")
    else:
        print("❌ Database missing - will be created on first run")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'AWS_ACCESS_KEY_ID' in content and 'AWS_SECRET_ACCESS_KEY' in content:
                print("✅ AWS credentials configured")
            else:
                print("❌ AWS credentials missing")
    else:
        print("❌ .env file missing")
    
    print("\n📋 Upload Test Instructions:")
    print("1. Make sure you have a test MP3 file")
    print("2. Open http://localhost:5000 in browser")
    print("3. Click 'Upload Song' button")
    print("4. Select your MP3 file")
    print("5. Fill in title, artist, album")
    print("6. Click 'Upload' button")
    print("7. Check the terminal for any error messages")
    
    return True

if __name__ == '__main__':
    test_upload()
