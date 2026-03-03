# 🎶 Cloud Music Locker (Mini Spotify)

A personal cloud music library where users can upload songs (MP3s) and stream them from anywhere using AWS services.

## 🌟 Features

- ✅ **Upload MP3 files** - Support for MP3, WAV, M4A, and OGG formats
- ✅ **Cloud Storage** - Store songs securely in AWS S3
- ✅ **Stream Music** - Play songs directly in browser via HTML5 audio player
- ✅ **Music Library** - List available songs with metadata (title, artist, album)
- ✅ **Modern UI** - Spotify-like interface with responsive design
- ✅ **Free Tier Friendly** - Uses EC2 + S3 only (stays within AWS free tier limits)
- ✅ **Local Fallback** - Works without AWS S3 (stores files locally)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask App     │◄──►│   AWS S3        │
│   (Frontend)    │    │   (EC2)         │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQLite DB     │
                       │   (Metadata)    │
                       └─────────────────┘
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd cloud-music-locker
pip install -r requirements.txt
```

### 2. AWS Configuration (Optional)

Create a `.env` file in the project root:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET=your-music-bucket-name
```

**Note:** If you don't configure AWS credentials, the app will work in local mode (files stored locally).

### 3. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` to access your music locker!

## 🛠️ AWS Setup (Free Tier)

### 1. Create S3 Bucket

1. Go to AWS S3 Console
2. Create a new bucket (e.g., `my-music-bucket-123`)
3. Configure bucket for public read access (for streaming)
4. Note the bucket name for your `.env` file

### 2. Create IAM User

1. Go to AWS IAM Console
2. Create a new user with programmatic access
3. Attach policy: `AmazonS3FullAccess`
4. Save the Access Key ID and Secret Access Key

### 3. Launch EC2 Instance

1. Launch a t2.micro instance (free tier eligible)
2. Install Python 3.8+ and pip
3. Clone your repository
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python app.py`

## 📁 Project Structure

```
cloud-music-locker/
├── app.py                 # Flask backend application
├── templates/
│   └── index.html        # Main UI template
├── static/
│   └── style.css         # Custom styling
├── uploads/              # Local file storage (if not using S3)
├── songs.db              # SQLite database (auto-created)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

## 🎵 Usage

### Uploading Songs

1. Click the "Upload Song" button
2. Select an audio file (MP3, WAV, M4A, OGG)
3. Optionally fill in title, artist, and album information
4. Click "Upload"

### Playing Music

1. Browse your music library in the table
2. Click the play button (▶️) next to any song
3. Use the audio controls to play, pause, and seek

### Managing Songs

- **Play**: Click the play button to start playback
- **Delete**: Click the trash button to remove songs
- **View Details**: Hover over songs to see metadata

## 💰 Free Tier Considerations

### AWS Free Tier Limits (12 months)

- **EC2 (t2.micro)**: 750 hours/month
- **S3**: 5GB storage, 20,000 GET requests, 2,000 PUT requests
- **Data Transfer**: 15GB out per month
- **EBS**: 30GB storage

### Estimated Usage

- **Storage**: ~100 songs (5GB) = 1,000 MP3s at 5MB each
- **Streaming**: ~500 hours of music per month
- **Uploads**: ~2,000 songs per month

**Result**: Perfect for personal use within free tier limits!

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET` | AWS S3 bucket name | `my-music-bucket-123` |
| `AWS_ACCESS_KEY_ID` | AWS access key | None (local mode) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | None (local mode) |
| `AWS_REGION` | AWS region | `us-east-1` |

### Supported Audio Formats

- MP3 (`.mp3`)
- WAV (`.wav`)
- M4A (`.m4a`)
- OGG (`.ogg`)

## 🚀 Deployment

### Production Deployment

1. **Use Gunicorn**:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:80 app:app
   ```

2. **Set up reverse proxy** (Nginx):
   ```nginx
   server {
       listen 80;
       location / {
           proxy_pass http://127.0.0.1:80;
       }
   }
   ```

3. **Configure SSL** (Let's Encrypt):
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🔒 Security Considerations

- **File Validation**: Only audio files are accepted
- **Secure Filenames**: UUIDs prevent path traversal
- **AWS IAM**: Use least-privilege access
- **HTTPS**: Always use SSL in production
- **Input Sanitization**: All user inputs are sanitized

## 🐛 Troubleshooting

### Common Issues

1. **"AWS credentials not found"**
   - Check your `.env` file
   - Verify AWS credentials are correct
   - App will work in local mode without AWS

2. **"Permission denied" on S3**
   - Check IAM user permissions
   - Verify bucket policy allows public read
   - Ensure bucket name is correct

3. **Audio won't play**
   - Check browser console for errors
   - Verify file format is supported
   - Check S3 bucket CORS configuration

### S3 CORS Configuration

Add this CORS configuration to your S3 bucket:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

## 🚀 Future Enhancements

- [ ] **User Authentication** - Multi-user support
- [ ] **Playlists** - Create and manage playlists
- [ ] **Search & Filter** - Find songs by title, artist, album
- [ ] **Mobile App** - React Native or Flutter app
- [ ] **Music Metadata** - Auto-extract from MP3 tags
- [ ] **Streaming Optimization** - Adaptive bitrate streaming
- [ ] **Social Features** - Share playlists with friends
- [ ] **Offline Mode** - Download songs for offline listening

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section
2. Search existing issues
3. Create a new issue with detailed information

---

**Happy Listening! 🎵**

*Built with ❤️ using Flask, AWS S3, and modern web technologies.*
