#!/usr/bin/env python3
"""
Consolidated Setup Script for Coemeta WebScraper
This script helps users set up their Google Service Account credentials securely
and provides comprehensive setup guidance for the entire project.
"""

import os
import json
import shutil
from pathlib import Path


def check_existing_credentials():
    """Check if credentials are already configured"""
    print("🔍 Checking existing credentials...")

    # Check environment variable
    env_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
    if env_path and os.path.exists(env_path):
        print(f"✅ Found credentials via environment variable: {env_path}")
        return env_path

    # Check default location
    default_path = "service_account.json"
    if os.path.exists(default_path):
        print(f"✅ Found credentials in default location: {default_path}")
        return default_path

    print("❌ No credentials found")
    return None


def validate_json_structure(file_path):
    """Validate that the JSON file has the correct structure"""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        required_fields = [
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
            "client_id",
        ]

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            print(f"❌ Invalid service account JSON. Missing fields: {missing_fields}")
            return False

        print("✅ Service account JSON structure is valid")
        return True

    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return False
    except Exception as e:
        print(f"❌ Error reading JSON file: {e}")
        return False


def setup_environment_variable():
    """Guide user through setting up environment variable"""
    print("\n📝 Setting up environment variable...")

    # Get the path from user
    while True:
        path = input("Enter the full path to your service account JSON file: ").strip()

        if not path:
            print("❌ Path cannot be empty")
            continue

        if not os.path.exists(path):
            print("❌ File does not exist")
            continue

        if not validate_json_structure(path):
            continue

        break

    # Show user how to set environment variable
    print(f"\n✅ Valid credentials found at: {path}")
    print("\n📋 To set the environment variable, run one of these commands:")
    print(f"\nFor macOS/Linux (temporary):")
    print(f'export GOOGLE_SERVICE_ACCOUNT_PATH="{path}"')

    print(f"\nFor macOS/Linux (permanent - add to ~/.zshrc or ~/.bashrc):")
    print(f"echo 'export GOOGLE_SERVICE_ACCOUNT_PATH=\"{path}\"' >> ~/.zshrc")

    print(f"\nFor Windows (Command Prompt):")
    print(f'set GOOGLE_SERVICE_ACCOUNT_PATH="{path}"')

    print(f"\nFor Windows (PowerShell):")
    print(f'$env:GOOGLE_SERVICE_ACCOUNT_PATH = "{path}"')


def setup_local_file():
    """Guide user through setting up local credentials file"""
    print("\n📁 Setting up local credentials file...")

    # Get the path from user
    while True:
        path = input("Enter the full path to your service account JSON file: ").strip()

        if not path:
            print("❌ Path cannot be empty")
            continue

        if not os.path.exists(path):
            print("❌ File does not exist")
            continue

        if not validate_json_structure(path):
            continue

        break

    # Copy file to project directory
    try:
        shutil.copy2(path, "service_account.json")
        print("✅ Credentials copied to project directory as 'service_account.json'")
        print("✅ This file is already protected by .gitignore")
        return True
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return False


def auto_detect_credentials():
    """Automatically detect and set up credentials from downloaded files"""
    print("\n🔍 Looking for potential service account files...")
    potential_files = []

    # Look for files that might be service account JSONs
    for file in os.listdir("."):
        if file.endswith(".json") and "service" in file.lower():
            potential_files.append(file)
        elif file.endswith(".json") and len(file) > 20:  # Likely a service account file
            potential_files.append(file)

    if potential_files:
        print(f"Found potential service account files: {potential_files}")
        for file in potential_files:
            if validate_json_structure(file):
                print(f"\n✅ Found valid service account file: {file}")
                choice = input(
                    f"Rename '{file}' to 'service_account.json'? (y/n): "
                ).lower()
                if choice == "y":
                    try:
                        shutil.copy2(file, "service_account.json")
                        print("✅ Successfully copied to service_account.json")
                        return True
                    except Exception as e:
                        print(f"❌ Error copying file: {e}")

    return False


def show_google_cloud_instructions():
    """Show detailed instructions for Google Cloud setup"""
    print("\n📋 Google Cloud Setup Instructions:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable Google Sheets API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Sheets API' and enable it")
    print("4. Create a Service Account:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'Service Account'")
    print("   - Name it 'coemeta-scraper' (or any name)")
    print("   - Skip optional steps and click 'Done'")
    print("5. Generate JSON Key:")
    print("   - Click on your service account email")
    print("   - Go to 'Keys' tab")
    print("   - Click 'Add Key' > 'Create new key'")
    print("   - Select 'JSON' format and click 'Create'")
    print("6. Download the JSON file")


def test_credentials():
    """Test the credentials by trying to authenticate"""
    print("\n🧪 Testing credentials...")

    try:
        from google_sheets import get_gspread_client
        from config import get_service_account_path

        service_account_path = get_service_account_path()
        if not service_account_path:
            print("❌ No service account path found")
            return False

        if not os.path.exists(service_account_path):
            print(f"❌ Service account file not found: {service_account_path}")
            return False

        # Try to authenticate
        client = get_gspread_client(service_account_path)
        print("✅ Google Sheets authentication successful!")
        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")

    required_packages = [
        "streamlit",
        "pandas",
        "gspread",
        "google-auth",
        "requests",
        "beautifulsoup4",
        "selenium",
        "webdriver-manager",
        "duckdb",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == "google-auth":
                __import__("google.auth")
            elif package == "beautifulsoup4":
                __import__("bs4")
            elif package == "duckdb":
                __import__("duckdb")
            else:
                __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies are installed!")
        return True


def setup_credentials():
    """Main credentials setup function"""
    print("🔐 Google Cloud Credentials Setup")
    print("=" * 50)

    # Check if already configured
    existing_path = check_existing_credentials()
    if existing_path:
        if validate_json_structure(existing_path):
            print("\n✅ Credentials are already properly configured!")
            return True
        else:
            print("\n⚠️  Existing credentials are invalid. Please provide a new file.")

    # Try auto-detection first
    if auto_detect_credentials():
        return True

    # Show setup instructions
    show_google_cloud_instructions()

    print("\n📁 Place the downloaded JSON file in this project directory")
    print("   and rename it to 'service_account.json'")

    print("\n📝 Manual Setup:")
    print("1. Download your service account JSON from Google Cloud Console")
    print("2. Place it in this project directory")
    print("3. Rename it to 'service_account.json'")
    print("4. Run this script again to validate")

    return False


def main():
    """Main setup function"""
    print("🚀 Coemeta WebScraper - Complete Setup")
    print("=" * 60)

    # Check dependencies first
    deps_ok = check_dependencies()

    # Check current credentials status
    if check_existing_credentials():
        print("\n✅ Credentials are already configured!")

        if test_credentials():
            print("✅ All tests passed! Your setup is complete.")
            return
        else:
            print("⚠️  Credentials are configured but authentication failed.")
            print("   Please check your Google Cloud project settings.")
            return

    print("\n❌ No credentials found. Let's set them up securely.")
    print("\nChoose your preferred method:")
    print("1. Environment Variable (Recommended for production)")
    print("2. Local File (Easier for development)")
    print("3. Auto-detect downloaded files")
    print("4. Show Google Cloud setup instructions")

    while True:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            setup_environment_variable()
            break
        elif choice == "2":
            if setup_local_file():
                break
        elif choice == "3":
            if auto_detect_credentials():
                break
        elif choice == "4":
            show_google_cloud_instructions()
            print("\nAfter following the instructions, run this script again.")
            return
        else:
            print("❌ Please enter 1, 2, 3, or 4")

    # Test the setup
    if test_credentials():
        print("\n🎉 Setup completed successfully!")
        print("✅ All tests passed! Your credentials are working.")
    else:
        print("\n⚠️  Setup complete but authentication failed.")
        print("   Please check your Google Cloud project settings.")

    print("\n💡 Next steps:")
    print("1. Run: streamlit run streamlit_app.py")
    print("2. Open your browser to the URL shown")
    print("3. Start scraping auction data!")


if __name__ == "__main__":
    main()
