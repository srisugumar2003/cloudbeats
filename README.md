# ☁️ CloudBeats

**Music streaming, simplified.**

CloudBeats is a personal cloud music locker built with Flask and Azure Blob Storage. Upload, store, and stream your music from anywhere.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3-green?logo=flask)
![Azure](https://img.shields.io/badge/Azure-Blob%20Storage-0078D4?logo=microsoftazure)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 🎵 **Upload & Stream** — Upload MP3, WAV, M4A, OGG files and stream directly from the browser
- ☁️ **Azure Blob Storage** — Files are stored securely in Azure cloud
- 🌗 **Dark / Light Theme** — Toggle between light blue and dark themes (persists across sessions)
- 📱 **Responsive Design** — Works seamlessly on desktop and mobile
- 🗑️ **Manage Library** — Delete songs from both cloud storage and database
- 🔍 **Song Metadata** — Add title, artist, and album info to your uploads

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask |
| **Storage** | Azure Blob Storage |
| **Database** | SQLite |
| **Frontend** | HTML, CSS, Bootstrap 5 |
| **Deployment** | Azure App Service (Linux) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Azure Storage Account ([create one](https://portal.azure.com))
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/srisugumar2003/cloudbeat.git
cd cloudbeat

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
# Azure Configuration
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
AZURE_STORAGE_CONTAINER_NAME=music-container

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
```

### Verify Azure Connection

```bash
python verify_azure.py
```

### Run Locally

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## ☁️ Deploy to Azure App Service

```bash
# Login to Azure
az login

# Create resources
az group create --name cloudbeats-rg --location eastus
az appservice plan create --name cloudbeats-plan --resource-group cloudbeats-rg --sku F1 --is-linux
az webapp create --resource-group cloudbeats-rg --plan cloudbeats-plan --name cloudbeats-app --runtime "PYTHON:3.10"

# Set environment variables
az webapp config appsettings set --resource-group cloudbeats-rg --name cloudbeats-app \
    --settings AZURE_STORAGE_CONNECTION_STRING="your_connection_string" \
    AZURE_STORAGE_CONTAINER_NAME="music-container"

# Deploy
az webapp up --name cloudbeats-app --resource-group cloudbeats-rg --runtime "PYTHON:3.10"

# Set startup command
az webapp config set --resource-group cloudbeats-rg --name cloudbeats-app \
    --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

---

## 📁 Project Structure

```
cloudbeat/
├── app.py                 # Flask application (routes, Azure integration)
├── requirements.txt       # Python dependencies
├── verify_azure.py        # Azure connection verification script
├── deploy_to_azure.sh     # Azure deployment script (Linux/macOS)
├── deploy.bat             # Local setup script (Windows)
├── env.example            # Environment variables template
├── .gitignore             # Git ignore rules
├── static/
│   └── style.css          # Custom styles (light/dark theme)
├── templates/
│   └── index.html         # Main UI template
├── uploads/               # Local file storage (git-ignored)
└── songs.db               # SQLite database (git-ignored)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/srisugumar2003">srisugumar2003</a>
</p>
