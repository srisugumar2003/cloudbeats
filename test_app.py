#!/usr/bin/env python3
"""
Test script for Cloud Music Locker
This script tests the basic functionality of the application
"""

import os
import sys
import sqlite3
import tempfile
from pathlib import Path

def test_database_connection():
    """Test database initialization and connection"""
    print("🔍 Testing database connection...")
    
    try:
        # Test database creation
        conn = sqlite3.connect('test_songs.db')
        conn.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                title TEXT,
                artist TEXT,
                album TEXT,
                duration INTEGER,
                file_size INTEGER,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                s3_url TEXT,
                local_path TEXT
            )
        """)
        
        # Test insert
        conn.execute("""
            INSERT INTO songs (filename, original_name, title, artist, album)
            VALUES (?, ?, ?, ?, ?)
        """, ('test.mp3', 'test.mp3', 'Test Song', 'Test Artist', 'Test Album'))
        
        # Test select
        result = conn.execute("SELECT * FROM songs WHERE title = ?", ('Test Song',)).fetchone()
        
        conn.close()
        os.remove('test_songs.db')
        
        if result:
            print("✅ Database connection test passed")
            return True
        else:
            print("❌ Database connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def test_file_operations():
    """Test file upload directory creation"""
    print("🔍 Testing file operations...")
    
    try:
        # Test upload directory creation
        upload_dir = Path('uploads')
        upload_dir.mkdir(exist_ok=True)
        
        # Test file creation
        test_file = upload_dir / 'test.txt'
        test_file.write_text('test content')
        
        # Test file reading
        content = test_file.read_text()
        
        # Cleanup
        test_file.unlink()
        
        if content == 'test content':
            print("✅ File operations test passed")
            return True
        else:
            print("❌ File operations test failed")
            return False
            
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    required_modules = [
        'flask',
        'werkzeug',
        'sqlite3',
        'uuid',
        'datetime'
    ]
    
    optional_modules = [
        'boto3'
    ]
    
    failed_imports = []
    optional_failed = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed_imports.append(module)
    
    for module in optional_modules:
        try:
            __import__(module)
            print(f"  ✅ {module} (optional)")
        except ImportError:
            print(f"  ⚠️  {module} (optional - AWS features disabled)")
            optional_failed.append(module)
    
    if failed_imports:
        print(f"❌ Import test failed. Missing required modules: {', '.join(failed_imports)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required imports successful")
        if optional_failed:
            print("⚠️  Some optional modules missing - AWS features will be disabled")
        return True

def test_aws_configuration():
    """Test AWS configuration (optional)"""
    print("🔍 Testing AWS configuration...")
    
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    s3_bucket = os.environ.get('S3_BUCKET')
    
    if aws_key and aws_secret and s3_bucket:
        print("✅ AWS credentials found")
        try:
            import boto3
            s3 = boto3.client('s3')
            # Test S3 connection (this will fail if credentials are invalid)
            s3.list_buckets()
            print("✅ AWS S3 connection successful")
            return True
        except ImportError:
            print("⚠️  boto3 not available - AWS features disabled")
            print("💡 App will work in local mode without S3")
            return False
        except Exception as e:
            print(f"⚠️  AWS S3 connection failed: {e}")
            print("💡 App will work in local mode without S3")
            return False
    else:
        print("⚠️  AWS credentials not found")
        print("💡 App will work in local mode without S3")
        return False

def main():
    """Run all tests"""
    print("🎶 Cloud Music Locker - Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_database_connection,
        test_file_operations,
        test_aws_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your app is ready to run.")
        print("🚀 Start the app with: python app.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Make sure to install dependencies: pip install -r requirements.txt")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
