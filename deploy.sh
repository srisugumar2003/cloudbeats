#!/bin/bash

# CloudBeats - Linux/macOS Deployment Script
# This script helps deploy the application locally or prepare for Azure

echo "CloudBeats - Deployment Script"
echo "======================================"

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip if not present
echo "Installing Python and pip..."
sudo apt install python3 python3-pip python3-venv -y

# Create virtual environment
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p uploads

# Set proper permissions
echo "Setting permissions..."
chmod 755 uploads
chmod 644 app.py
chmod 644 requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[WARN] .env file not found!"
    echo "Please create a .env file with your Azure credentials"
    echo "Copy env.example to .env and fill in your values"
    exit 1
fi

echo "[OK] Configuration files found"

# Install Gunicorn for production
echo "Installing Gunicorn for production..."
pip install gunicorn

# Create systemd service file
echo "Creating systemd service..."
sudo tee /etc/systemd/system/cloudbeats.service > /dev/null <<EOF
[Unit]
Description=CloudBeats Music App
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
echo "Starting service..."
sudo systemctl daemon-reload
sudo systemctl enable cloudbeats
sudo systemctl start cloudbeats

# Check service status
echo "Checking service status..."
sudo systemctl status cloudbeats --no-pager

echo ""
echo "Deployment complete!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status cloudbeats     # Check status"
echo "  sudo systemctl restart cloudbeats    # Restart app"
echo "  sudo systemctl stop cloudbeats       # Stop app"
echo "  sudo journalctl -u cloudbeats -f     # View logs"
echo ""
echo "To deploy to Azure App Service, see the Azure deployment guide."
