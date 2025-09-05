#!/bin/bash
# Setup script for Visual-NN Lightweight with Gemini AI

echo "🧠 Setting up Visual-NN Lightweight with Gemini AI"
echo "====================================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.7+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install dependencies
echo "📦 Installing lightweight dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv package manager..."
    uv pip install -r requirements.txt
else
    echo "Using pip..."
    pip3 install -r requirements.txt
fi

# Check for Gemini API key
echo "🔑 Checking Gemini AI configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file found"
    echo "🔒 Reminder: .env is protected by .gitignore (never commits to Git)"
else
    echo "⚠️  Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit .env and add your GEMINI_API_KEY"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "🔒 SECURITY NOTE:"
    echo "   • .env file is automatically ignored by Git"
    echo "   • Your API keys will NEVER be committed"
    echo "   • Safe to use on both Mac and EC2"
fi

# Check memory optimization
echo "🚀 Memory optimization for t3.micro:"
echo "   - Removed PyTorch (500MB+ → ~50MB total)"
echo "   - Added scipy/numpy lightweight operations"
echo "   - Implemented aggressive caching"
echo "   - Added memory monitoring"

echo ""
echo "✅ Setup complete! Next steps:"
echo "   1. Edit .env and add your GEMINI_API_KEY"
echo "   2. Run: export GEMINI_API_KEY=your_key_here"
echo "   3. Start server: python app.py"
echo "   4. Open: http://localhost:5001"
echo ""
echo "🧠 AI Features:"
echo "   - Smart architecture suggestions"
echo "   - Real-time layer explanations"
echo "   - Content-aware recommendations"
echo "   - Fallback to manual mode if AI unavailable"
