from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, Response, send_file
import os
import uuid
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import sys
import io
import mimetypes
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

# Try to import Azure SDKs
try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False
    print("Warning: azure-storage-blob not available.")

try:
    from azure.cosmos import CosmosClient, PartitionKey
    AZURE_COSMOS_AVAILABLE = True
except ImportError:
    AZURE_COSMOS_AVAILABLE = False
    print("Warning: azure-cosmos not available.")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("SUCCESS: Environment variables loaded")
except ImportError:
    print("WARNING: python-dotenv not available.")

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')
UPLOAD_FOLDER = os.path.join(base_dir, 'uploads')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.environ.get('SECRET_KEY', 'cloudbeats-secret-key-123')

# --- Database Setup (Cosmos DB with SQLite Fallback) ---
COSMOS_ENDPOINT = os.environ.get('COSMOS_ENDPOINT')
COSMOS_KEY = os.environ.get('COSMOS_KEY')
COSMOS_DATABASE_NAME = os.environ.get('COSMOS_DATABASE_NAME', 'CloudBeatsDB')
COSMOS_CONTAINER_NAME = os.environ.get('COSMOS_CONTAINER_NAME', 'songs')

class DatabaseManager:
    def __init__(self):
        self.use_cosmos = False
        self.cosmos_container = None
        self.sqlite_db = os.path.join(base_dir, 'songs.db')
        
        if AZURE_COSMOS_AVAILABLE and COSMOS_ENDPOINT and COSMOS_KEY:
            try:
                client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
                database = client.create_database_if_not_exists(id=COSMOS_DATABASE_NAME)
                self.cosmos_container = database.create_container_if_not_exists(
                    id=COSMOS_CONTAINER_NAME, 
                    partition_key=PartitionKey(path="/artist"),
                    offer_throughput=400
                )
                self.use_cosmos = True
                print("CONFIG: Using Azure Cosmos DB")
            except Exception as e:
                print(f"Warning: Failed to connect to Cosmos DB, falling back to SQLite: {e}")
        
        if not self.use_cosmos:
            print("CONFIG: Using Local SQLite Database")
            self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(self.sqlite_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                title TEXT,
                artist TEXT,
                album TEXT,
                file_size INTEGER,
                upload_date TEXT,
                blob_url TEXT,
                local_path TEXT
            )
        """)
        conn.commit()
        conn.close()

    def get_songs(self):
        if self.use_cosmos:
            query = "SELECT * FROM c ORDER BY c.upload_date DESC"
            items = list(self.cosmos_container.query_items(query=query, enable_cross_partition_query=True))
            return items
        else:
            conn = sqlite3.connect(self.sqlite_db)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM songs ORDER BY upload_date DESC").fetchall()
            songs = [dict(row) for row in rows]
            conn.close()
            return songs

    def add_song(self, song_data):
        if self.use_cosmos:
            self.cosmos_container.upsert_item(song_data)
        else:
            conn = sqlite3.connect(self.sqlite_db)
            conn.execute("""
                INSERT INTO songs (id, filename, original_name, title, artist, album, file_size, upload_date, blob_url, local_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                song_data['id'], song_data['filename'], song_data['original_name'],
                song_data['title'], song_data['artist'], song_data['album'],
                song_data['file_size'], song_data['upload_date'],
                song_data.get('blob_url'), song_data.get('local_path')
            ))
            conn.commit()
            conn.close()

    def delete_song(self, song_id):
        if self.use_cosmos:
            # Need partition key to delete in Cosmos
            query = f"SELECT * FROM c WHERE c.id = '{song_id}'"
            items = list(self.cosmos_container.query_items(query=query, enable_cross_partition_query=True))
            if items:
                self.cosmos_container.delete_item(item=song_id, partition_key=items[0]['artist'])
                return items[0]
        else:
            conn = sqlite3.connect(self.sqlite_db)
            song = conn.execute("SELECT * FROM songs WHERE id = ?", (song_id,)).fetchone()
            if song:
                conn.execute("DELETE FROM songs WHERE id = ?", (song_id,))
                conn.commit()
                conn.close()
                return {'filename': song[1], 'local_path': song[9]}
            conn.close()
        return None

    def update_song_blob_url(self, song_id: str, blob_url: str) -> bool:
        if self.use_cosmos:
            query = f"SELECT * FROM c WHERE c.id = '{song_id}'"
            items = list(self.cosmos_container.query_items(query=query, enable_cross_partition_query=True))
            if not items:
                return False
            item = items[0]
            item["blob_url"] = blob_url
            self.cosmos_container.upsert_item(item)
            return True
        else:
            conn = sqlite3.connect(self.sqlite_db)
            conn.execute("UPDATE songs SET blob_url = ? WHERE id = ?", (blob_url, song_id))
            conn.commit()
            conn.close()
            return True

db_manager = DatabaseManager()

# --- Azure Storage setup ---
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'music-container')

blob_service_client = None
if AZURE_STORAGE_AVAILABLE and AZURE_STORAGE_CONNECTION_STRING:
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
        try:
            container_client.get_container_properties()
        except Exception:
            container_client.create_container()
        print("SUCCESS: Azure Blob client initialized")
    except Exception as e:
        print(f"Warning: Failed to initialize Azure Blob client: {e}")

_upload_executor = ThreadPoolExecutor(max_workers=int(os.environ.get("UPLOAD_WORKERS", "2")))

def upload_to_azure(file_path, filename):
    if not blob_service_client:
        return None
    try:
        blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=filename)
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            # Reasonable fallbacks for common audio types
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            content_type = {
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav',
                'm4a': 'audio/mp4',
                'ogg': 'audio/ogg',
            }.get(ext, 'application/octet-stream')
        with open(file_path, "rb") as data:
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )
        return blob_client.url
    except Exception as e:
        print(f"Error uploading to Azure: {e}")
        return None

def _background_upload_and_update(song_id: str, local_path: str, filename: str):
    try:
        blob_url = upload_to_azure(local_path, filename)
        if blob_url:
            db_manager.update_song_blob_url(song_id, blob_url)
    except Exception as e:
        print(f"Background upload failed for {song_id}: {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    songs = db_manager.get_songs()
    return render_template('index.html', songs=songs)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        original_name = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}.{original_name.rsplit('.', 1)[1].lower()}"
        local_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(local_path)
        
        song_data = {
            'id': str(uuid.uuid4()),
            'filename': unique_filename,
            'original_name': original_name,
            'title': request.form.get('title', original_name.rsplit('.', 1)[0]),
            'artist': request.form.get('artist', 'Unknown Artist'),
            'album': request.form.get('album', 'Unknown Album'),
            'file_size': os.path.getsize(local_path),
            'upload_date': datetime.utcnow().isoformat(),
            'local_path': local_path
        }

        # Save the record immediately so the request returns quickly.
        # Uploading to Azure can be slow; do it in the background.
        db_manager.add_song(song_data)
        if blob_service_client:
            _upload_executor.submit(_background_upload_and_update, song_data["id"], local_path, unique_filename)
            flash(f'Uploaded: {original_name}. Syncing to cloud in the background...')
        else:
            flash(f'Successfully uploaded: {original_name}')
    else:
        flash('Invalid file type.')
    
    return redirect(url_for('index'))

@app.route('/play/<string:song_id>')
def play_song(song_id):
    songs = db_manager.get_songs()
    song = next((s for s in songs if str(s['id']) == song_id), None)
    
    if song:
        # Always stream through the app so playback works even when the blob container is private.
        return jsonify({'url': url_for('stream_song', song_id=song_id), 'name': song.get('original_name')})
    
    return jsonify({'error': 'Song not found'}), 404

def _parse_range_header(range_header: Optional[str], size: int):
    """
    Parse a simple single range header: "bytes=start-end".
    Returns (start, end) inclusive, or None when no valid range requested.
    """
    if not range_header:
        return None
    if not range_header.startswith("bytes="):
        return None
    value = range_header.replace("bytes=", "", 1).strip()
    if "," in value:
        # Multiple ranges not supported
        return None
    if "-" not in value:
        return None
    start_s, end_s = value.split("-", 1)
    try:
        if start_s == "":
            # suffix-byte-range-spec: "-<length>"
            suffix_len = int(end_s)
            if suffix_len <= 0:
                return None
            start = max(0, size - suffix_len)
            end = size - 1
            return (start, end)
        start = int(start_s)
        end = int(end_s) if end_s else (size - 1)
    except ValueError:
        return None
    if start < 0 or start >= size:
        return None
    end = min(end, size - 1)
    if end < start:
        return None
    return (start, end)

@app.route('/stream/<string:song_id>')
def stream_song(song_id):
    songs = db_manager.get_songs()
    song = next((s for s in songs if str(s['id']) == song_id), None)
    if not song:
        return jsonify({'error': 'Song not found'}), 404

    original_name = song.get('original_name') or song.get('filename') or 'audio'
    filename = song.get('filename') or original_name
    mimetype, _ = mimetypes.guess_type(original_name)
    if not mimetype:
        mimetype, _ = mimetypes.guess_type(filename)
    if not mimetype:
        mimetype = 'application/octet-stream'

    # Prefer local file when present (fast, supports range via send_file)
    local_path = song.get('local_path')
    if local_path and os.path.exists(local_path):
        return send_file(local_path, mimetype=mimetype, conditional=True, download_name=original_name)

    # Otherwise, stream from Azure Blob Storage (supports private containers).
    if not blob_service_client or not filename:
        return jsonify({'error': 'Audio file not available'}), 404

    try:
        blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=filename)
        props = blob_client.get_blob_properties()
        size = int(props.size)

        byte_range = _parse_range_header(request.headers.get("Range"), size)
        if byte_range:
            start, end = byte_range
            length = end - start + 1
            stream = blob_client.download_blob(offset=start, length=length)

            def generate():
                for chunk in stream.chunks():
                    yield chunk

            rv = Response(generate(), status=206, mimetype=mimetype)
            rv.headers["Content-Range"] = f"bytes {start}-{end}/{size}"
            rv.headers["Accept-Ranges"] = "bytes"
            rv.headers["Content-Length"] = str(length)
            return rv

        stream = blob_client.download_blob()

        def generate_all():
            for chunk in stream.chunks():
                yield chunk

        rv = Response(generate_all(), mimetype=mimetype)
        rv.headers["Accept-Ranges"] = "bytes"
        rv.headers["Content-Length"] = str(size)
        return rv
    except Exception as e:
        print(f"Error streaming from Azure Blob: {e}")
        return jsonify({'error': 'Failed to stream audio'}), 500

@app.route('/file/<filename>')
def serve_file(filename):
    from flask import send_from_directory
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete/<string:song_id>', methods=['POST'])
def delete_song(song_id):
    song = db_manager.delete_song(song_id)
    if song:
        if os.path.exists(song['local_path']):
            os.remove(song['local_path'])
        
        if blob_service_client and song['filename']:
            try:
                blob_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=song['filename'])
                blob_client.delete_blob()
            except Exception:
                pass
        flash('Song deleted successfully')
    else:
        flash('Song not found')
    return redirect(url_for('index'))

@app.route('/api/songs')
def api_songs():
    return jsonify(db_manager.get_songs())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
