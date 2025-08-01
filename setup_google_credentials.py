#!/usr/bin/env python3
"""
Setup script for Google Cloud credentials
Helps configure the service account JSON file for the Coemeta WebScraper project.
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


def setup_credentials():
    """Main setup function"""
    print("🚀 Google Cloud Credentials Setup")
    print("=" * 50)

    # Check if already configured
    existing_path = check_existing_credentials()
    if existing_path:
        if validate_json_structure(existing_path):
            print("\n✅ Credentials are already properly configured!")
            return True
        else:
            print("\n⚠️  Existing credentials are invalid. Please provide a new file.")

    print("\n📋 Setup Instructions:")
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

    print("\n📁 Place the downloaded JSON file in this project directory")
    print("   and rename it to 'service_account.json'")

    # Check for downloaded files
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

    print("\n📝 Manual Setup:")
    print("1. Download your service account JSON from Google Cloud Console")
    print("2. Place it in this project directory")
    print("3. Rename it to 'service_account.json'")
    print("4. Run this script again to validate")

    return False


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


if __name__ == "__main__":
    print("🔧 Google Cloud Credentials Setup for Coemeta WebScraper")
    print("=" * 60)

    if setup_credentials():
        print("\n🎉 Setup completed successfully!")

        if test_credentials():
            print("✅ All tests passed! Your credentials are working.")
        else:
            print("⚠️  Credentials are configured but authentication failed.")
            print("   Please check your Google Cloud project settings.")
    else:
        print("\n❌ Setup incomplete. Please follow the instructions above.")
        print("   Run this script again after placing the JSON file.")
