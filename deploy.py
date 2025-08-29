#!/usr/bin/env python3
"""
Deployment script for Visual Neural Network.
Supports various deployment environments.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors."""
    print(f"🔄 {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr.strip()}")
        return False

def check_requirements():
    """Check if all requirements are installed."""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ is required")
        return False
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt not found")
        return False
    
    print("✅ Requirements check passed")
    return True

def install_dependencies(use_uv=True):
    """Install Python dependencies."""
    if use_uv:
        return run_command("uv pip install -r requirements.txt", "Installing dependencies with uv")
    else:
        return run_command("pip install -r requirements.txt", "Installing dependencies with pip")

def run_development():
    """Run the application in development mode."""
    print("🚀 Starting development server...")
    os.environ['FLASK_ENV'] = 'development'
    os.system("python app.py")

def run_production():
    """Run the application in production mode."""
    print("🚀 Starting production server...")
    os.environ['FLASK_ENV'] = 'production'
    
    # Check if gunicorn is available for production
    try:
        subprocess.check_output(["which", "gunicorn"])
        print("🔄 Starting with Gunicorn...")
        os.system("gunicorn -w 4 -b 0.0.0.0:5001 app:app")
    except subprocess.CalledProcessError:
        print("⚠️  Gunicorn not found, using Flask development server")
        print("⚠️  For production, install gunicorn: pip install gunicorn")
        os.system("python app.py")

def create_docker_files():
    """Create Docker configuration files."""
    dockerfile_content = """FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5001

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
"""

    dockerignore_content = """__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git/
.mypy_cache/
.pytest_cache/
.hypothesis/
.DS_Store
.vscode/
.idea/
*.swp
*.swo
*~
"""

    docker_compose_content = """version: '3.8'

services:
  visual-nn:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key-here
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    networks:
      - visual-nn-network

networks:
  visual-nn-network:
    driver: bridge
"""

    # Write Docker files
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    with open(".dockerignore", "w") as f:
        f.write(dockerignore_content)
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose_content)
    
    print("✅ Docker configuration files created")
    print("🐳 To run with Docker:")
    print("   docker build -t visual-nn .")
    print("   docker run -p 5001:5001 visual-nn")
    print("🐳 Or with Docker Compose:")
    print("   docker-compose up")

def main():
    parser = argparse.ArgumentParser(description="Deploy Visual Neural Network")
    parser.add_argument("--mode", choices=["dev", "prod", "docker"], default="dev",
                       help="Deployment mode (default: dev)")
    parser.add_argument("--no-uv", action="store_true",
                       help="Use pip instead of uv for installation")
    parser.add_argument("--skip-deps", action="store_true",
                       help="Skip dependency installation")
    
    args = parser.parse_args()
    
    print("🧠 Visual Neural Network Deployment Script")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies unless skipped
    if not args.skip_deps:
        if not install_dependencies(use_uv=not args.no_uv):
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    # Run based on mode
    if args.mode == "dev":
        run_development()
    elif args.mode == "prod":
        run_production()
    elif args.mode == "docker":
        create_docker_files()
    
    print("🎉 Deployment completed!")

if __name__ == "__main__":
    main()
