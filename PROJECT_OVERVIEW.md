# CloudBeats - Project Overview

## Architecture

```
+------------------+     +------------------+     +---------------------+
|   Web Browser    |<--->|   Flask App      |<--->| Azure Blob Storage  |
|   (Frontend)     |     |   (Backend)      |     |   (Cloud Storage)   |
+------------------+     +--------+---------+     +---------------------+
                                  |
                         +--------+---------+
                         |     SQLite DB     |
                         |   (Metadata)      |
                         +------------------+
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10, Flask 2.3 |
| Frontend | HTML5, CSS3, Bootstrap 5, Font Awesome |
| Database | SQLite |
| Cloud Storage | Azure Blob Storage |
| Deployment | Azure App Service (Linux, F1 Free Tier) |
| WSGI Server | Gunicorn |

## Features

- **Music Upload** - Upload MP3, WAV, M4A, OGG files
- **Cloud Storage** - Azure Blob Storage integration with local fallback
- **Streaming** - Stream music directly from Azure Blob URLs
- **Library Management** - View, play, and delete songs
- **Dark/Light Theme** - Toggle between light blue and dark themes
- **Responsive Design** - Works on desktop and mobile
- **Song Metadata** - Title, artist, album info
- **Environment Configuration** - Flexible Azure setup via `.env`

## File Structure

```
cloudbeat/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── verify_azure.py        # Azure connection verification
├── test_app.py            # Application test suite
├── test_upload.py         # Upload functionality test
├── deploy_to_azure.sh     # Azure App Service deployment script
├── deploy.sh              # Linux local deployment script
├── deploy.bat             # Windows local setup script
├── env.example            # Environment variables template
├── .env                   # Environment variables (git-ignored)
├── .gitignore             # Git ignore rules
├── songs.db               # SQLite database (git-ignored)
├── static/
│   └── style.css          # Custom styles (light/dark theme)
├── templates/
│   └── index.html         # Main UI template
└── uploads/               # Local file storage (git-ignored)
```

## How It Works

### Upload Flow
1. User selects an audio file and fills in metadata
2. Flask saves the file locally to `uploads/`
3. If Azure is configured, the file is uploaded to Azure Blob Storage
4. Song metadata and Azure URL are stored in SQLite

### Playback Flow
1. User clicks Play on a song
2. Flask looks up the Azure Blob URL (or local path as fallback)
3. Browser streams the audio directly from the URL

### Delete Flow
1. User confirms deletion
2. Flask deletes the blob from Azure Blob Storage
3. Flask deletes the local file
4. Flask removes the database record

## Azure Free Tier Limits

| Service | Free Allowance |
|---|---|
| Blob Storage | 5 GB storage |
| App Service (F1) | 1 GB RAM, 60 min/day CPU |
| Bandwidth | 5 GB outbound/month |

## Status

- **Cloud Integration** - Azure Blob Storage working
- **Free Tier Compatible** - Stays within Azure limits
- **Theme Support** - Light blue and dark mode
- **Full-Width Layout** - Responsive design
