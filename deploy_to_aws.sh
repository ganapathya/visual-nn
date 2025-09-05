#!/bin/bash
# Deploy Visual Neural Network to AWS instance

echo "🚀 Deploying Visual Neural Network to AWS instance"
echo "=================================================="

# Configuration
AWS_USER="ubuntu"
AWS_HOST=""
AWS_KEY_PATH=""
PROJECT_NAME="visual-nn"

# Check if required parameters are provided
if [ -z "$AWS_HOST" ]; then
    echo "❌ Please set AWS_HOST environment variable or edit this script"
    echo "   Example: export AWS_HOST=your-ec2-instance-ip"
    exit 1
fi

if [ -z "$AWS_KEY_PATH" ]; then
    echo "❌ Please set AWS_KEY_PATH environment variable or edit this script"
    echo "   Example: export AWS_KEY_PATH=~/.ssh/your-key.pem"
    exit 1
fi

echo "📋 Configuration:"
echo "   Host: $AWS_HOST"
echo "   User: $AWS_USER"
echo "   Key: $AWS_KEY_PATH"
echo ""

# Check if SSH key exists
if [ ! -f "$AWS_KEY_PATH" ]; then
    echo "❌ SSH key not found: $AWS_KEY_PATH"
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
DEPLOY_DIR="deploy_package"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy necessary files
cp -r app.py config.py requirements-light.txt requirements.txt "$DEPLOY_DIR/"
cp -r examples/ "$DEPLOY_DIR/" 2>/dev/null || true
cp -r static/ "$DEPLOY_DIR/" 2>/dev/null || true
cp -r templates/ "$DEPLOY_DIR/" 2>/dev/null || true
cp index.html "$DEPLOY_DIR/" 2>/dev/null || true
cp README.md "$DEPLOY_DIR/" 2>/dev/null || true

# Copy service files
cp visual-nn.service "$DEPLOY_DIR/"
cp setup_service.sh "$DEPLOY_DIR/"
cp troubleshoot_service.sh "$DEPLOY_DIR/"
cp SERVICE_SETUP.md "$DEPLOY_DIR/"

# Create remote setup script
cat > "$DEPLOY_DIR/remote_setup.sh" << 'EOF'
#!/bin/bash
# Remote setup script for AWS instance

echo "🧠 Setting up Visual Neural Network on AWS instance"
echo "=================================================="

# Set variables
PROJECT_DIR="/home/ubuntu/visual-nn"
VENV_DIR="$PROJECT_DIR/venv"

# Create project directory
echo "📁 Creating project directory..."
sudo mkdir -p "$PROJECT_DIR"
sudo chown ubuntu:ubuntu "$PROJECT_DIR"

# Copy files to project directory
echo "📋 Copying project files..."
cp -r * "$PROJECT_DIR/"
cd "$PROJECT_DIR"

# Make scripts executable
chmod +x setup_service.sh
chmod +x troubleshoot_service.sh

# Set up the service
echo "🔧 Setting up systemd service..."
sudo ./setup_service.sh

echo "✅ Remote setup complete!"
echo "🌐 Your application should be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5001"
EOF

chmod +x "$DEPLOY_DIR/remote_setup.sh"

# Create deployment archive
echo "📦 Creating deployment archive..."
tar -czf "${PROJECT_NAME}_deploy.tar.gz" -C "$DEPLOY_DIR" .

# Upload to AWS instance
echo "📤 Uploading to AWS instance..."
scp -i "$AWS_KEY_PATH" "${PROJECT_NAME}_deploy.tar.gz" "${AWS_USER}@${AWS_HOST}:/tmp/"

# Execute remote setup
echo "🔧 Executing remote setup..."
ssh -i "$AWS_KEY_PATH" "${AWS_USER}@${AWS_HOST}" << 'EOF'
    cd /tmp
    tar -xzf visual-nn_deploy.tar.gz
    chmod +x remote_setup.sh
    ./remote_setup.sh
EOF

# Clean up
echo "🧹 Cleaning up..."
rm -rf "$DEPLOY_DIR"
rm "${PROJECT_NAME}_deploy.tar.gz"

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your Visual Neural Network should now be running at:"
echo "   http://$AWS_HOST:5001"
echo ""
echo "📋 Useful commands:"
echo "   Check status: ssh -i $AWS_KEY_PATH ${AWS_USER}@${AWS_HOST} 'sudo systemctl status visual-nn'"
echo "   View logs: ssh -i $AWS_KEY_PATH ${AWS_USER}@${AWS_HOST} 'sudo journalctl -u visual-nn -f'"
echo "   Restart: ssh -i $AWS_KEY_PATH ${AWS_USER}@${AWS_HOST} 'sudo systemctl restart visual-nn'"
