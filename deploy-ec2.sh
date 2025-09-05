#!/bin/bash
# EC2 Deployment Script for Visual Neural Network (Lightweight Version)

set -e  # Exit on any error

echo "🚀 Deploying Visual Neural Network to EC2 (Lightweight Version)"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run as root. Use a regular user with sudo privileges."
    exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# Create project directory
PROJECT_DIR="/home/$(whoami)/visual-nn"
print_status "Setting up project directory: $PROJECT_DIR"
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Copy project files (assuming you're running this from the project directory)
if [ -f "app.py" ]; then
    print_status "Copying project files..."
    cp -r . $PROJECT_DIR/
else
    print_warning "Project files not found in current directory. Please copy them manually."
fi

# Set up Python virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install lightweight dependencies
print_status "Installing lightweight dependencies..."
pip install --upgrade pip

# Use CPU-only PyTorch (much smaller)
print_status "Installing CPU-only PyTorch (lightweight version)..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
pip install Flask Flask-CORS Pillow numpy gunicorn

# Verify installation size
print_status "Checking installation size..."
du -sh venv/
print_status "Installation complete! Total size: $(du -sh venv/ | cut -f1)"

# Set up environment variables
print_status "Setting up environment variables..."
export FLASK_ENV=production
export SECRET_KEY="your-super-secret-key-change-this-in-production"
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5001

# Create systemd service
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/visual-nn.service > /dev/null << EOF
[Unit]
Description=Visual Neural Network Flask App
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-super-secret-key-change-this-in-production"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -w 2 -b 0.0.0.0:5001 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable visual-nn
sudo systemctl start visual-nn

# Wait for service to start
sleep 3

# Check service status
if sudo systemctl is-active --quiet visual-nn; then
    print_status "Flask service is running"
else
    print_error "Flask service failed to start"
    sudo systemctl status visual-nn
    exit 1
fi

# Set up Nginx
print_status "Setting up Nginx..."

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)
print_status "Detected public IP: $PUBLIC_IP"

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/visual-nn > /dev/null << EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    # Serve static files (frontend)
    location / {
        root /var/www/html;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Add CORS headers for frontend
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type";
    }

    # Proxy API requests to Flask backend
    location /process-layers {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Handle CORS preflight requests
        if (\$request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin *;
            add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
            add_header Access-Control-Allow-Headers "Content-Type";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type "text/plain; charset=utf-8";
            add_header Content-Length 0;
            return 204;
        }
        
        # Add CORS headers for actual requests
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5001/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Increase upload size for images
    client_max_body_size 10M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
EOF

# Copy index.html to Nginx directory
print_status "Copying frontend to Nginx..."
sudo cp index.html /var/www/html/
sudo chown www-data:www-data /var/www/html/index.html

# Enable site and restart Nginx
sudo ln -sf /etc/nginx/sites-available/visual-nn /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
if sudo nginx -t; then
    print_status "Nginx configuration is valid"
else
    print_error "Nginx configuration is invalid"
    exit 1
fi

sudo systemctl restart nginx

# Configure firewall
print_status "Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Test the deployment
print_status "Testing deployment..."

# Test backend
if curl -s http://localhost:5001/ | grep -q "Server is running"; then
    print_status "Backend API is working"
else
    print_error "Backend API is not responding"
fi

# Test frontend
if curl -s http://localhost/ | grep -q "Visual Neural Network"; then
    print_status "Frontend is accessible"
else
    print_error "Frontend is not accessible"
fi

# Test API through Nginx
if curl -s http://localhost/health | grep -q "Server is running"; then
    print_status "API proxy through Nginx is working"
else
    print_error "API proxy through Nginx is not working"
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "======================================"
echo "🌐 Frontend: http://$PUBLIC_IP"
echo "🔧 Backend API: http://$PUBLIC_IP/process-layers"
echo "❤️  Health Check: http://$PUBLIC_IP/health"
echo ""
echo "📋 Useful commands:"
echo "   Check service status: sudo systemctl status visual-nn"
echo "   View logs: sudo journalctl -u visual-nn -f"
echo "   Restart service: sudo systemctl restart visual-nn"
echo "   Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo ""
echo "🔒 Security:"
echo "   - Change SECRET_KEY in /etc/systemd/system/visual-nn.service"
echo "   - Consider setting up HTTPS with Let's Encrypt"
echo "   - Update firewall rules as needed"
echo ""
echo "💡 Next steps:"
echo "   1. Open http://$PUBLIC_IP in your browser"
echo "   2. Upload an image and test the CNN visualization"
echo "   3. Monitor logs for any issues"
