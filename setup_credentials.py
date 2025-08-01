#!/usr/bin/env python3
"""
Credential Setup Helper for Coemeta WebScraper
This script helps users set up their Google Service Account credentials securely.
"""

import os
import json
from pathlib import Path


def check_credentials():
    """Check if credentials are properly configured"""
    print("🔍 Checking credential configuration...")

    # Check environment variables
    env_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
    if env_path:
        if os.path.exists(env_path):
            print(f"✅ Environment variable set: {env_path}")
            return True
        else:
            print(f"❌ Environment variable points to non-existent file: {env_path}")

    # Check local file
    local_path = "service_account.json"
    if os.path.exists(local_path):
        print(f"✅ Local credentials file found: {local_path}")
        return True

    print("❌ No credentials found")
    return False


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
        print(f"❌ Error reading file: {e}")
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
        import shutil

        shutil.copy2(path, "service_account.json")
        print("✅ Credentials copied to project directory as 'service_account.json'")
        print("✅ This file is already protected by .gitignore")
        return True
    except Exception as e:
        print(f"❌ Error copying file: {e}")
        return False


def main():
    """Main setup function"""
    print("🔐 Coemeta WebScraper - Credential Setup")
    print("=" * 50)

    # Check current status
    if check_credentials():
        print("\n✅ Credentials are already configured!")
        return

    print("\n❌ No credentials found. Let's set them up securely.")
    print("\nChoose your preferred method:")
    print("1. Environment Variable (Recommended for production)")
    print("2. Local File (Easier for development)")

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()

        if choice == "1":
            setup_environment_variable()
            break
        elif choice == "2":
            setup_local_file()
            break
        else:
            print("❌ Please enter 1 or 2")

    print("\n✅ Setup complete! You can now run the scraper.")
    print(
        "💡 Remember to keep your credentials secure and never commit them to version control."
    )


if __name__ == "__main__":
    main()
