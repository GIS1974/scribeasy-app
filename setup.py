#!/usr/bin/env python3
"""
ScribeEasy Setup Script
Helps set up the development environment for the ScribeEasy application.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def check_requirements():
    """Check if required tools are installed."""
    print("Checking requirements...")
    
    # Check Python
    try:
        result = run_command("python --version")
        print(f"✓ Python found: {result.stdout.strip()}")
    except:
        print("✗ Python not found. Please install Python 3.8+")
        return False
    
    # Check Node.js
    try:
        result = run_command("node --version")
        print(f"✓ Node.js found: {result.stdout.strip()}")
    except:
        print("✗ Node.js not found. Please install Node.js 18+")
        return False
    
    # Check npm
    try:
        result = run_command("npm --version")
        print(f"✓ npm found: {result.stdout.strip()}")
    except:
        print("✗ npm not found. Please install npm")
        return False
    
    return True

def setup_backend():
    """Set up the backend environment."""
    print("\n=== Setting up Backend ===")
    
    backend_dir = Path("backend")
    
    # Create virtual environment
    print("Creating Python virtual environment...")
    run_command("python -m venv venv", cwd=backend_dir)
    
    # Determine activation script path
    if os.name == 'nt':  # Windows
        activate_script = backend_dir / "venv" / "Scripts" / "activate"
        pip_path = backend_dir / "venv" / "Scripts" / "pip"
    else:  # Unix/Linux/macOS
        activate_script = backend_dir / "venv" / "bin" / "activate"
        pip_path = backend_dir / "venv" / "bin" / "pip"
    
    # Install dependencies
    print("Installing Python dependencies...")
    run_command(f"{pip_path} install -r requirements.txt", cwd=backend_dir)
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        shutil.copy(env_example, env_file)
        print("⚠️  Please edit backend/.env and add your AssemblyAI API key!")
    
    print("✓ Backend setup complete!")

def setup_frontend():
    """Set up the frontend environment."""
    print("\n=== Setting up Frontend ===")
    
    frontend_dir = Path("frontend")
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    # Create .env file if it doesn't exist
    env_file = frontend_dir / ".env"
    env_example = frontend_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        shutil.copy(env_example, env_file)
    
    print("✓ Frontend setup complete!")

def create_directories():
    """Create necessary directories."""
    print("\n=== Creating directories ===")
    
    # Create upload directory
    upload_dir = Path("backend/temp_uploads")
    upload_dir.mkdir(exist_ok=True)
    print(f"✓ Created {upload_dir}")

def print_next_steps():
    """Print instructions for next steps."""
    print("\n" + "="*50)
    print("🎉 Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Add your AssemblyAI API key to backend/.env")
    print("   Get your API key from: https://www.assemblyai.com/")
    print("\n2. Start the backend server:")
    print("   cd backend")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   python main.py")
    print("\n3. In a new terminal, start the frontend:")
    print("   cd frontend")
    print("   npm run dev")
    print("\n4. Open your browser to http://localhost:5173")
    print("\nFor Docker deployment:")
    print("   docker-compose up -d")

def main():
    """Main setup function."""
    print("ScribeEasy Setup Script")
    print("======================")
    
    if not check_requirements():
        print("\nPlease install the required tools and run this script again.")
        sys.exit(1)
    
    setup_backend()
    setup_frontend()
    create_directories()
    print_next_steps()

if __name__ == "__main__":
    main()
