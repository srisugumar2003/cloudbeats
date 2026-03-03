from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import os
import sqlite3
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import json

# Try to import azure-storage-blob
try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("Warning: azure-storage-blob not available. Azure features will be disabled.")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("SUCCESS: Environment variables loaded from .env file")
except ImportError:
    print("WARNING: python-dotenv not available. Using system environment variables only.")

# Configure directories for production
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'your-secret-key-change-this'

# Azure Storage setup
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'music-container')

# Initialize Azure Blob client
if AZURE_AVAILABLE and AZURE_STORAGE_CONNECTION_STRING:
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        # Ensure container exists
        container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
        try:
            container_client.get_container_properties()
            print(f"SUCCESS: Azure Blob container '{AZURE_STORAGE_CONTAINER_NAME}' found")
        except Exception:
            container_client.create_container()
            print(f"SUCCESS: Azure Blob container '{AZURE_STORAGE_CONTAINER_NAME}' created")
        print("SUCCESS: Azure Blob service client initialized successfully")
    except Exception as e:
        blob_service_client = None
        print(f"Warning: Failed to initialize Azure Blob client: {e}")
else:
    blob_service_client = None
    if not AZURE_AVAILABLE:
        print("Warning: azure-storage-blob not available. Azure functionality will be disabled.")
    else:
        print("Warning: Azure connection string not found. Azure functionality will be disabled.")

# Database setup (SQLite for free tier)
DB = "songs.db"
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    """Initialize the SQLite database with songs table"""
    conn = sqlite3.connect(DB)
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
            blob_url TEXT,
            local_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_azure(file_path, filename):
    """Upload file to Azure Blob Storage and return public URL"""
    if not blob_service_client:
        return None
    
    try:
        blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=filename)
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(
                data, 
                overwrite=True,
                content_settings=ContentSettings(content_type='audio/mpeg')
            )
        
        return blob_client.url
    except Exception as e:
        print(f"Error uploading to Azure: {e}")
        return None

@app.route('/')
def index():
    """Main page showing upload form and song list"""
    # Debug print for Azure logs
    print(f"DEBUG: Working directory: {os.getcwd()}")
    print(f"DEBUG: Base dir: {base_dir}")
    print(f"DEBUG: Template dir exists: {os.path.exists(template_dir)}")
    if os.path.exists(template_dir):
        print(f"DEBUG: Templates content: {os.listdir(template_dir)}")

    conn = sqlite3.connect(DB)
    songs = conn.execute("""
        SELECT id, original_name, title, artist, album, duration, upload_date, blob_url, local_path
        FROM songs 
        ORDER BY upload_date DESC
    """).fetchall()
    conn.close()
    
    return render_template('index.html', songs=songs)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        original_name = secure_filename(file.filename)
        file_extension = original_name.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Save file locally
        local_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(local_path)
        
        # Get file info
        file_size = os.path.getsize(local_path)
        
        # Extract metadata from form or filename
        title = request.form.get('title', original_name.rsplit('.', 1)[0])
        artist = request.form.get('artist', 'Unknown Artist')
        album = request.form.get('album', 'Unknown Album')
        
        # Upload to Azure if available
        blob_url = upload_to_azure(local_path, unique_filename)
        
        # Save to database
        conn = sqlite3.connect(DB)
        conn.execute("""
            INSERT INTO songs (filename, original_name, title, artist, album, file_size, blob_url, local_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (unique_filename, original_name, title, artist, album, file_size, blob_url, local_path))
        conn.commit()
        conn.close()
        
        flash(f'Successfully uploaded: {original_name}')
    else:
        flash('Invalid file type. Please upload MP3, WAV, M4A, or OGG files.')
    
    return redirect(url_for('index'))

@app.route('/play/<int:song_id>')
def play_song(song_id):
    """Get song URL for playback"""
    conn = sqlite3.connect(DB)
    song = conn.execute("""
        SELECT blob_url, local_path, original_name 
        FROM songs 
        WHERE id = ?
    """, (song_id,)).fetchone()
    conn.close()
    
    if song:
        # Prefer Azure Blob URL if available, otherwise serve local file
        if song[0]:  # blob_url
            return jsonify({'url': song[0], 'name': song[2]})
        else:  # local_path
            return jsonify({'url': url_for('serve_file', filename=os.path.basename(song[1])), 'name': song[2]})
    
    return jsonify({'error': 'Song not found'}), 404

@app.route('/file/<filename>')
def serve_file(filename):
    """Serve local files"""
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    """Delete a song"""
    conn = sqlite3.connect(DB)
    song = conn.execute("SELECT local_path, filename FROM songs WHERE id = ?", (song_id,)).fetchone()
    
    if song:
        # Delete local file
        if os.path.exists(song[0]):
            os.remove(song[0])
        
        # Delete from Azure if exists
        if blob_service_client and song[1]:
            try:
                blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=song[1])
                blob_client.delete_blob()
            except Exception as e:
                print(f"Error deleting from Azure: {e}")
        
        # Delete from database
        conn.execute("DELETE FROM songs WHERE id = ?", (song_id,))
        conn.commit()
        flash('Song deleted successfully')
    else:
        flash('Song not found')
    
    conn.close()
    return redirect(url_for('index'))

@app.route('/api/songs')
def api_songs():
    """API endpoint to get all songs as JSON"""
    conn = sqlite3.connect(DB)
    songs = conn.execute("""
        SELECT id, original_name, title, artist, album, duration, upload_date
        FROM songs 
        ORDER BY upload_date DESC
    """).fetchall()
    conn.close()
    
    songs_list = []
    for song in songs:
        songs_list.append({
            'id': song[0],
            'original_name': song[1],
            'title': song[2],
            'artist': song[3],
            'album': song[4],
            'duration': song[5],
            'upload_date': song[6]
        })
    
    return jsonify(songs_list)

# Initialize database on startup
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
