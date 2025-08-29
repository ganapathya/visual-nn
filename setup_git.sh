#!/bin/bash
# Git setup script for Visual Neural Network project

echo "🧠 Setting up Git repository for Visual Neural Network"
echo "======================================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if already a git repository
if [ -d ".git" ]; then
    echo "⚠️  This directory is already a Git repository."
    echo "Current status:"
    git status --porcelain
    echo ""
    echo "Do you want to continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
else
    # Initialize git repository
    echo "🔄 Initializing Git repository..."
    git init
fi

# Check if files are ready
echo "🔍 Running project status check..."
python check_status.py
if [ $? -ne 0 ]; then
    echo "❌ Project status check failed. Please fix issues before proceeding."
    exit 1
fi

# Add all files
echo "📁 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Visual Neural Network

🧠 Interactive CNN visualization tool with:
- Real-time layer processing and visualization
- Multiple visualization modes (Basic, Feature Maps, Statistics, Comparison)
- Educational features with tutorials and explanations
- Support for various layer types and kernels
- Responsive web interface with Tailwind CSS
- Flask backend with PyTorch for accurate CNN operations

Features:
✅ Conv2D, Pooling, ReLU, BatchNorm, Dropout layers
✅ Multiple kernel types (Sharpen, Blur, Sobel, Gaussian, etc.)
✅ Real-time parameter preview
✅ Interactive tutorials and explanations
✅ Receptive field calculations
✅ Multiple visualization tabs
✅ Comprehensive documentation
✅ CI/CD pipeline
✅ Docker support
✅ Example scripts"

echo ""
echo "✅ Git repository setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Create a repository on GitHub"
echo "   2. git remote add origin <your-repo-url>"
echo "   3. git branch -M main"
echo "   4. git push -u origin main"
echo ""
echo "💡 Optional improvements:"
echo "   - Add demo screenshots to README"
echo "   - Update repository URL in README.md"
echo "   - Test deployment: python deploy.py --mode dev"
echo "   - Run API demo: python examples/demo.py"
echo ""
echo "🎉 Your Visual Neural Network project is ready for the world!"
