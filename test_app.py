#!/usr/bin/env python3
"""
CloudBeats - Application Test Suite
Tests configuration, dependencies, database, and Azure connectivity.
"""

import os
import sys
import sqlite3

def test_environment():
    """Test Python environment"""
    print("Testing Python Environment...")
    print(f"  Python version: {sys.version}")
    print(f"  Platform: {sys.platform}")
    print("[OK] Python environment ready")
    return True

def test_dependencies():
    """Test required Python packages"""
    print("\nTesting Dependencies...")
    required = ['flask', 'werkzeug', 'dotenv']
    optional = ['azure.storage.blob']
    
    all_ok = True
    for module in required:
        try:
            __import__(module)
            print(f"  [OK] {module}")
        except ImportError:
            print(f"  [ERROR] {module} - MISSING (required)")
            all_ok = False
    
    for module in optional:
        try:
            __import__(module)
            print(f"  [OK] {module}")
        except ImportError:
            print(f"  [WARN] {module} - missing (Azure features disabled)")
    
    return all_ok

def test_database():
    """Test SQLite database"""
    print("\nTesting Database...")
    db_path = 'songs.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'songs' in tables:
            count = conn.execute("SELECT COUNT(*) FROM songs").fetchone()[0]
            print(f"  [OK] Database exists with {count} songs")
        else:
            print("  [WARN] Songs table not found - will be created on first run")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  [ERROR] Database error: {e}")
        return False

def test_azure_configuration():
    """Test Azure configuration"""
    print("\nTesting Azure Configuration...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'music-container')
    
    if connection_string and connection_string != 'your_connection_string_here':
        print(f"  [OK] Azure connection string found")
        print(f"  [OK] Container name: {container_name}")
        
        try:
            from azure.storage.blob import BlobServiceClient
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_client = blob_service_client.get_container_client(container_name)
            container_client.get_container_properties()
            print("  [OK] Azure Blob Storage connection successful")
        except ImportError:
            print("  [WARN] azure-storage-blob not installed - Azure features disabled")
        except Exception as e:
            print(f"  [WARN] Azure connection failed: {e}")
            print("  App will work in local storage mode")
    else:
        print("  [WARN] Azure credentials not configured")
        print("  App will work in local storage mode")
    
    return True

def test_file_structure():
    """Test project file structure"""
    print("\nTesting File Structure...")
    required_files = ['app.py', 'requirements.txt', 'templates/index.html', 'static/style.css']
    
    all_ok = True
    for f in required_files:
        if os.path.exists(f):
            print(f"  [OK] {f}")
        else:
            print(f"  [ERROR] {f} - MISSING")
            all_ok = False
    
    # Check uploads directory
    if os.path.exists('uploads'):
        print("  [OK] uploads/")
    else:
        os.makedirs('uploads', exist_ok=True)
        print("  [OK] uploads/ (created)")
    
    return all_ok

def main():
    print("=" * 50)
    print("CloudBeats - Application Test Suite")
    print("=" * 50)
    
    tests = [
        test_environment,
        test_dependencies,
        test_file_structure,
        test_database,
        test_azure_configuration
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  [ERROR] Test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    passed = sum(1 for r in results if r)
    print(f"Results: {passed}/{len(results)} tests passed")
    
    if all(results):
        print("[OK] All tests passed! Ready to run.")
    else:
        print("[WARN] Some tests failed. Check output above.")

if __name__ == '__main__':
    main()
