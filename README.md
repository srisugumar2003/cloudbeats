# ☁️ CloudBeats

**Music streaming, simplified.**

CloudBeats is a personal cloud music locker built with Flask and Azure Blob Storage. Upload, store, and stream your music from anywhere.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![Azure](https://img.shields.io/badge/Azure-Blob%20Storage-0078D4)

---

## ✨ Features

- 🎵 **Upload & Stream** — Upload MP3, WAV, M4A, OGG files and play them in-browser
- ☁️ **Azure Blob Storage** — Files are stored securely in Azure cloud
- 🌙 **Dark/Light Theme** — Toggle between light blue and dark themes (persisted in browser)
- 📱 **Responsive Design** — Works on desktop, tablet, and mobile
- 🗑️ **Manage Library** — Delete songs from both cloud storage and local database
- 🔍 **Auto-fill Metadata** — Title auto-fills from filename on upload

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask |
| **Database** | SQLite |
| **Cloud Storage** | Azure Blob Storage |
| **Frontend** | HTML5, CSS3, Bootstrap 5, Font Awesome |
| **Server** | Gunicorn (production) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Azure Storage Account ([create one here](https://portal.azure.com))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/srisugumar2003/cloudbeat.git
   cd cloudbeat
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   ```
   Edit `.env` and add your Azure Storage connection string:
   ```env
   AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
   AZURE_STORAGE_CONTAINER_NAME=music-container
   ```

5. **Verify Azure connection**
   ```bash
   python verify_azure.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```
   Open `http://localhost:5000` in your browser.

---

## 📁 Project Structure

```
cloudbeat/
├── app.py                 # Flask application (routes, Azure integration)
├── requirements.txt       # Python dependencies
├── verify_azure.py        # Azure connection verification script
├── deploy_to_azure.sh     # Azure App Service deployment script
├── deploy.bat             # Windows local setup script
├── env.example            # Environment variables template
├── .gitignore             # Git ignore rules
├── songs.db               # SQLite database (auto-generated)
├── uploads/               # Local file uploads (auto-generated)
├── static/
│   └── style.css          # Custom styles (light/dark themes)
└── templates/
    └── index.html         # Main UI template
```

---

## ☁️ Deploy to Azure App Service

```bash
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

## 📸 Screenshots

| Light Theme | Dark Theme |
|-------------|------------|
| Light blue UI with white cards | Deep navy with soft blue accents |

---

## 📄 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main page with music library |
| `POST` | `/upload` | Upload a new song |
| `GET` | `/play/<id>` | Get song URL for playback |
| `POST` | `/delete/<id>` | Delete a song |
| `GET` | `/api/songs` | Get all songs as JSON |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/awesome`)
3. Commit your changes (`git commit -m 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/awesome`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

Made with ❤️ by [srisugumar2003](https://github.com/srisugumar2003)
