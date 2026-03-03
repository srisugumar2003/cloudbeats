#!/bin/bash

# Cloud Music Locker - Deployment Script
# This script helps deploy the application to production

echo "🎶 Cloud Music Locker - Deployment Script"
echo "=========================================="

# Check if running on EC2
if [ -f /sys/hypervisor/uuid ] && [ `head -c 3 /sys/hypervisor/uuid` == ec2 ]; then
    echo "✅ Running on EC2 instance"
else
    echo "⚠️  Not running on EC2 - make sure you're deploying to the right environment"
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip if not present
echo "🐍 Installing Python and pip..."
sudo apt install python3 python3-pip python3-venv -y

# Create virtual environment
echo "🔧 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads

# Set proper permissions
echo "🔒 Setting permissions..."
chmod 755 uploads
chmod 644 app.py
chmod 644 requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Please create a .env file with your AWS credentials"
    echo "   Copy env.example to .env and fill in your values"
    exit 1
fi

# Install Gunicorn for production
echo "🚀 Installing Gunicorn for production..."
pip install gunicorn

# Create systemd service file
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/cloud-music-locker.service > /dev/null <<EOF
[Unit]
Description=Cloud Music Locker
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/gunicorn -w 4 -b 0.0.0.0:80 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
echo "🔄 Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable cloud-music-locker
sudo systemctl start cloud-music-locker

# Check service status
echo "📊 Checking service status..."
sudo systemctl status cloud-music-locker --no-pager

echo ""
echo "🎉 Deployment complete!"
echo "🌐 Your app should be running at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "📋 Useful commands:"
echo "   sudo systemctl status cloud-music-locker    # Check status"
echo "   sudo systemctl restart cloud-music-locker   # Restart app"
echo "   sudo systemctl stop cloud-music-locker      # Stop app"
echo "   sudo journalctl -u cloud-music-locker -f    # View logs"
echo ""
echo "🔧 To update the app:"
echo "   1. git pull"
echo "   2. sudo systemctl restart cloud-music-locker"
