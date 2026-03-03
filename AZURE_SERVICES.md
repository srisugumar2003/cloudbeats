# Azure Services Used in CloudBeats

## Active Services

### 1. Azure Blob Storage
- **Purpose:** Store and serve uploaded music files (MP3, WAV, M4A, OGG)
- **Container:** `music-container`
- **Access:** Public blob-level access for audio streaming
- **SDK:** `azure-storage-blob==12.19.0`
- **Free Tier:** 5 GB storage

### 2. Azure Storage Account
- **Name:** `cloudbeatsstorage`
- **Type:** StorageV2, Standard_LRS
- **Region:** East US
- **Purpose:** Parent resource for Blob Storage

## Deployment Service

### 3. Azure App Service
- **Plan:** F1 Free Tier (Linux)
- **Runtime:** Python 3.10
- **WSGI Server:** Gunicorn
- **Purpose:** Hosts the Flask web application
- **Free Tier:** 1 GB RAM, 60 min/day CPU

## Architecture

```
User Browser  →  Azure App Service (Flask)  →  Azure Blob Storage
                         ↕
                    SQLite (local DB)
```

## Not Used
- Azure SQL Database (using SQLite locally)
- Azure CDN
- Azure Functions
- Azure Active Directory
