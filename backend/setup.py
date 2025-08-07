#!/usr/bin/env python3
"""
Setup script for Coemeta WebScraper.
Creates virtual environment and installs dependencies.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def create_venv():
    """Create a virtual environment if it doesn't exist."""
    # Get the project root directory (one level up from backend)
    root_dir = Path(__file__).parent.parent
    venv_path = root_dir / "venv"
    
    if venv_path.exists():
        print("Virtual environment already exists.")
    else:
        print("Creating virtual environment...")
        venv.create(str(venv_path), with_pip=True)
        print("Virtual environment created.")
    
    return venv_path


def get_venv_python_path():
    """Get the path to the Python executable in the virtual environment."""
    # Get the project root directory (one level up from backend)
    root_dir = Path(__file__).parent.parent
    venv_path = root_dir / "venv"
    
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"
    
    return str(python_path)


def install_requirements(python_path):
    """Install the requirements using the virtual environment's pip."""
    # Get the project root directory (one level up from backend)
    root_dir = Path(__file__).parent.parent
    requirements_path = root_dir / "requirements.txt"
    
    print("Installing dependencies...")
    subprocess.run([python_path, "-m", "pip", "install", "-r", str(requirements_path)])
    print("Dependencies installed successfully!")


def main():
    """Main setup function."""
    # Create or verify virtual environment
    venv_path = create_venv()
    
    # Get the path to the Python executable in the virtual environment
    python_path = get_venv_python_path()
    
    # Install requirements
    install_requirements(python_path)
    
    print("\n✅ Setup complete! You can now run the application:")
    print(f"\n1. To use the command-line scraper:")
    print(f"   {python_path} -m backend.main")
    print(f"\n2. To use the Streamlit web interface:")
    print(f"   {python_path} -m streamlit run frontend/streamlit_app.py")
    

if __name__ == "__main__":
    main()
