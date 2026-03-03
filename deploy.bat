@echo off
echo 🎶 Cloud Music Locker - Windows Deployment Script
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Create virtual environment
echo 🔧 Setting up virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing Python dependencies...
pip install -r requirements.txt

REM Create uploads directory
echo 📁 Creating uploads directory...
if not exist uploads mkdir uploads

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo 📝 Please create a .env file with your AWS credentials
    echo    Copy env.example to .env and fill in your values
    pause
    exit /b 1
)

echo ✅ Configuration files found

REM Install Gunicorn for production
echo 🚀 Installing Gunicorn for production...
pip install gunicorn

echo.
echo 🎉 Setup complete!
echo.
echo 🚀 To run the application:
echo    python app.py
echo.
echo 🌐 Your app will be available at: http://localhost:5000
echo.
echo 📋 For production deployment on Windows:
echo    1. Use IIS with FastCGI
echo    2. Or use a reverse proxy like Nginx
echo    3. Or run with: gunicorn -w 4 -b 0.0.0.0:80 app:app
echo.
pause
