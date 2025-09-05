#!/bin/bash
# Troubleshooting script for Visual Neural Network systemd service

echo "🔧 Visual Neural Network Service Troubleshooter"
echo "==============================================="

# Set variables
PROJECT_DIR="/home/ubuntu/visual-nn"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="visual-nn.service"

echo "📋 Checking service status..."
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "🔍 Checking service logs..."
journalctl -u "$SERVICE_NAME" --no-pager -n 20

echo ""
echo "📁 Checking file paths..."

# Check if project directory exists
if [ -d "$PROJECT_DIR" ]; then
    echo "✅ Project directory exists: $PROJECT_DIR"
else
    echo "❌ Project directory missing: $PROJECT_DIR"
    echo "   Please ensure the project is in the correct location"
fi

# Check if virtual environment exists
if [ -d "$VENV_DIR" ]; then
    echo "✅ Virtual environment exists: $VENV_DIR"
else
    echo "❌ Virtual environment missing: $VENV_DIR"
    echo "   Run: sudo ./setup_service.sh to create it"
fi

# Check if gunicorn exists in venv
if [ -f "$VENV_DIR/bin/gunicorn" ]; then
    echo "✅ Gunicorn found in virtual environment"
    echo "   Version: $($VENV_DIR/bin/gunicorn --version)"
else
    echo "❌ Gunicorn not found in virtual environment"
    echo "   Run: sudo ./setup_service.sh to install dependencies"
fi

# Check if app.py exists
if [ -f "$PROJECT_DIR/app.py" ]; then
    echo "✅ app.py found in project directory"
else
    echo "❌ app.py missing from project directory"
fi

# Check if service file exists
if [ -f "/etc/systemd/system/$SERVICE_NAME" ]; then
    echo "✅ Service file exists: /etc/systemd/system/$SERVICE_NAME"
else
    echo "❌ Service file missing: /etc/systemd/system/$SERVICE_NAME"
    echo "   Run: sudo ./setup_service.sh to create it"
fi

echo ""
echo "🔧 Common fixes:"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "✅ Running as root (required for systemctl commands)"
else
    echo "⚠️  Not running as root - some commands may fail"
    echo "   Use: sudo ./troubleshoot_service.sh"
fi

echo ""
echo "📋 Manual troubleshooting steps:"
echo "1. Check if virtual environment is properly set up:"
echo "   cd $PROJECT_DIR && source venv/bin/activate && pip list"
echo ""
echo "2. Test gunicorn manually:"
echo "   cd $PROJECT_DIR && source venv/bin/activate && gunicorn --version"
echo ""
echo "3. Test the app manually:"
echo "   cd $PROJECT_DIR && source venv/bin/activate && python app.py"
echo ""
echo "4. Check systemd service configuration:"
echo "   sudo systemctl cat $SERVICE_NAME"
echo ""
echo "5. Reload systemd and restart service:"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl restart $SERVICE_NAME"
echo ""
echo "6. Check detailed logs:"
echo "   sudo journalctl -u $SERVICE_NAME -f"
