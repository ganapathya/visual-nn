#!/bin/bash
# Setup script for Visual Neural Network systemd service

echo "🧠 Setting up Visual Neural Network systemd service"
echo "=================================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root or with sudo"
    echo "Usage: sudo ./setup_service.sh"
    exit 1
fi

# Set variables
PROJECT_DIR="/home/ubuntu/visual-nn"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/visual-nn.service"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory $PROJECT_DIR does not exist"
    echo "Please clone or copy the project to $PROJECT_DIR first"
    exit 1
fi

echo "📁 Project directory: $PROJECT_DIR"

# Navigate to project directory
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "🔄 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install requirements (use requirements-light.txt for EC2)
if [ -f "requirements-light.txt" ]; then
    echo "📋 Installing from requirements-light.txt..."
    pip install -r requirements-light.txt
else
    echo "📋 Installing from requirements.txt..."
    pip install -r requirements.txt
fi

# Verify gunicorn is installed
if ! "$VENV_DIR/bin/gunicorn" --version > /dev/null 2>&1; then
    echo "❌ Gunicorn not found in virtual environment"
    echo "Installing gunicorn..."
    pip install gunicorn>=21.0.0
fi

echo "✅ Dependencies installed successfully"

# Copy service file
echo "🔧 Setting up systemd service..."
cp visual-nn.service "$SERVICE_FILE"

# Set proper permissions
chmod 644 "$SERVICE_FILE"

# Reload systemd daemon
systemctl daemon-reload

# Enable the service
systemctl enable visual-nn.service

echo "✅ Service setup complete!"
echo ""
echo "📋 Service management commands:"
echo "   Start:   sudo systemctl start visual-nn"
echo "   Stop:    sudo systemctl stop visual-nn"
echo "   Restart: sudo systemctl restart visual-nn"
echo "   Status:  sudo systemctl status visual-nn"
echo "   Logs:    sudo journalctl -u visual-nn -f"
echo ""
echo "🚀 Starting the service..."
systemctl start visual-nn.service

# Check service status
sleep 2
if systemctl is-active --quiet visual-nn.service; then
    echo "✅ Service started successfully!"
    echo "🌐 Application should be available at: http://your-server-ip:5001"
else
    echo "❌ Service failed to start"
    echo "📋 Checking service logs..."
    journalctl -u visual-nn.service --no-pager -n 20
    exit 1
fi

echo ""
echo "🎉 Visual Neural Network service setup complete!"
