#!/usr/bin/env python3
"""
Status check script for Visual Neural Network project.
Verifies that all necessary files are in place and the project is ready for Git.
"""

import os
import sys
from pathlib import Path

def check_file(file_path, description):
    """Check if a file exists and return status."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (missing)")
        return False

def check_directory(dir_path, description):
    """Check if a directory exists and return status."""
    if Path(dir_path).is_dir():
        print(f"✅ {description}: {dir_path}/")
        return True
    else:
        print(f"❌ {description}: {dir_path}/ (missing)")
        return False

def check_file_content(file_path, required_content, description):
    """Check if a file contains required content."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            if required_content in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} (content missing)")
                return False
    except FileNotFoundError:
        print(f"❌ {description} (file missing)")
        return False

def main():
    """Run all status checks."""
    print("🧠 Visual Neural Network - Project Status Check")
    print("=" * 60)
    
    all_checks_passed = True
    
    print("\n📁 Core Application Files:")
    checks = [
        ("app.py", "Main Flask application"),
        ("index.html", "Frontend interface"),
        ("requirements.txt", "Python dependencies"),
        ("config.py", "Configuration management"),
    ]
    
    for file_path, description in checks:
        if not check_file(file_path, description):
            all_checks_passed = False
    
    print("\n📚 Documentation Files:")
    doc_checks = [
        ("README.md", "Project documentation"),
        ("LICENSE", "MIT license file"),
        ("CONTRIBUTING.md", "Contribution guidelines"),
    ]
    
    for file_path, description in doc_checks:
        if not check_file(file_path, description):
            all_checks_passed = False
    
    print("\n🔧 Development Files:")
    dev_checks = [
        (".gitignore", "Git ignore rules"),
        ("deploy.py", "Deployment script"),
        (".github/workflows/ci.yml", "CI/CD pipeline"),
    ]
    
    for file_path, description in dev_checks:
        if not check_file(file_path, description):
            all_checks_passed = False
    
    print("\n📂 Example Files:")
    example_checks = [
        ("examples/demo.py", "API demo script"),
    ]
    
    for file_path, description in example_checks:
        if not check_file(file_path, description):
            all_checks_passed = False
    
    print("\n🔍 Content Checks:")
    content_checks = [
        ("README.md", "# 🧠 Visual Neural Network", "README has proper title"),
        ("requirements.txt", "Flask", "Requirements includes Flask"),
        ("requirements.txt", "torch", "Requirements includes PyTorch"),
        ("app.py", "from flask import Flask", "App imports Flask"),
        ("index.html", "Visual Neural Network", "HTML has proper title"),
    ]
    
    for file_path, content, description in content_checks:
        if not check_file_content(file_path, content, description):
            all_checks_passed = False
    
    print("\n🎯 Project Structure:")
    structure_items = [
        ("examples", "Examples directory"),
        (".github/workflows", "GitHub Actions directory"),
    ]
    
    for dir_path, description in structure_items:
        if not check_directory(dir_path, description):
            all_checks_passed = False
    
    print("\n" + "=" * 60)
    
    if all_checks_passed:
        print("🎉 All checks passed! Your project is ready for Git.")
        print("\n📋 Next steps:")
        print("   1. git init")
        print("   2. git add .")
        print("   3. git commit -m 'Initial commit: Visual Neural Network'")
        print("   4. git remote add origin <your-repo-url>")
        print("   5. git push -u origin main")
        print("\n💡 Recommended:")
        print("   - Update GitHub repository URL in README.md")
        print("   - Add demo screenshots to the repository")
        print("   - Test the deployment script: python deploy.py --mode dev")
        print("   - Run the API demo: python examples/demo.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n🔧 To fix missing files, you can:")
        print("   - Re-run the setup commands")
        print("   - Check for typos in file names")
        print("   - Ensure all files were created properly")
        return 1

if __name__ == "__main__":
    sys.exit(main())
