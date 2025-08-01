"""
Configuration file for Coemeta WebScraper
Handles secure credential management and configuration settings.
"""

import os
from pathlib import Path


def get_service_account_path():
    """
    Get the service account JSON file path from environment variable or default.
    Returns the path to the service account credentials file.
    """
    # First try environment variable
    env_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # Fallback to default location
    default_path = "service_account.json"
    if os.path.exists(default_path):
        return default_path

    # If neither exists, return None
    return None


def get_sheet_id():
    """
    Get the Google Sheet ID from environment variable or default.
    Returns the Google Sheet ID for keywords and results.
    """
    return os.getenv("GOOGLE_SHEET_ID", "1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo")


def validate_credentials():
    """
    Validate that the service account credentials exist and are accessible.
    Returns True if credentials are valid, False otherwise.
    """
    service_account_path = get_service_account_path()
    if not service_account_path:
        print("❌ No service account credentials found!")
        print("Please set GOOGLE_SERVICE_ACCOUNT_PATH environment variable")
        print("or place your service account JSON file as 'service_account.json'")
        return False

    if not os.path.exists(service_account_path):
        print(f"❌ Service account file not found: {service_account_path}")
        return False

    print(f"✅ Service account credentials found: {service_account_path}")
    return True


# Configuration constants
DEFAULT_MAX_RESULTS = 10
DEFAULT_SHEET_ID = "1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo"
