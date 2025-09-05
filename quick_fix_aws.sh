#!/bin/bash
# Quick fix script for Visual Neural Network systemd service on AWS

echo "🔧 Quick Fix for Visual Neural Network Service"
echo "============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root or with sudo"
    echo "Usage: sudo ./quick_fix_aws.sh"
    exit 1
fi

# Set variables
PROJECT_DIR="/home/ubuntu/visual-nn"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/visual-nn.service"

echo "📁 Checking project directory..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory $PROJECT_DIR does not exist"
    echo "Please ensure your project files are in $PROJECT_DIR"
    exit 1
fi

echo "✅ Project directory found"

# Stop the service if it's running
echo "🛑 Stopping service if running..."
systemctl stop visual-nn.service 2>/dev/null || true

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🔄 Creating virtual environment..."
    cd "$PROJECT_DIR"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment exists"
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd "$PROJECT_DIR"
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
if [ -f "requirements-light.txt" ]; then
    echo "📋 Installing from requirements-light.txt..."
    pip install -r requirements-light.txt
else
    echo "📋 Installing from requirements.txt..."
    pip install -r requirements.txt
fi

# Verify gunicorn is installed
if ! "$VENV_DIR/bin/gunicorn" --version > /dev/null 2>&1; then
    echo "❌ Gunicorn not found, installing..."
    pip install gunicorn>=21.0.0
fi

echo "✅ Dependencies installed"

# Set proper permissions
echo "🔐 Setting permissions..."
chown -R ubuntu:ubuntu "$PROJECT_DIR"
chmod +x "$VENV_DIR/bin/gunicorn"

# Create/update service file
echo "🔧 Creating systemd service file..."
cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=Visual Neural Network Flask App
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/visual-nn
Environment=PATH=/home/ubuntu/visual-nn/venv/bin
Environment=FLASK_ENV=production
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/ubuntu/visual-nn/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5001 --timeout 120 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=visual-nn

[Install]
WantedBy=multi-user.target
EOF

# Set service file permissions
chmod 644 "$SERVICE_FILE"

# Reload systemd and restart service
echo "🔄 Reloading systemd and starting service..."
systemctl daemon-reload
systemctl enable visual-nn.service
systemctl start visual-nn.service

# Check if service started successfully
sleep 3
if systemctl is-active --quiet visual-nn.service; then
    echo "✅ Service started successfully!"
    echo "🌐 Application should be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5001"
else
    echo "❌ Service failed to start"
    echo "📋 Checking service logs..."
    journalctl -u visual-nn.service --no-pager -n 10
    exit 1
fi

echo ""
echo "🎉 Quick fix complete!"
echo ""
echo "📋 Service management:"
echo "   Status:  systemctl status visual-nn"
echo "   Logs:    journalctl -u visual-nn -f"
echo "   Restart: systemctl restart visual-nn"
echo "   Stop:    systemctl stop visual-nn"
