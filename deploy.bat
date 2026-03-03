@echo off
echo CloudBeats - Windows Setup Script
echo ================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [OK] Python is installed

REM Create virtual environment
echo Setting up virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create uploads directory
echo Creating uploads directory...
if not exist uploads mkdir uploads

REM Check if .env file exists
if not exist .env (
    echo [WARN] .env file not found!
    echo Please create a .env file with your Azure credentials
    echo Copy env.example to .env and fill in your values
    pause
    exit /b 1
)

echo [OK] Configuration files found

REM Install Gunicorn for production
echo Installing Gunicorn for production...
pip install gunicorn

echo.
echo Setup complete!
echo.
echo To run the application:
echo    python app.py
echo.
echo Your app will be available at: http://localhost:5000
echo.
echo For Azure deployment:
echo    See the Azure deployment guide in the README.
echo.
pause
