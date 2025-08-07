#!/usr/bin/env python3
"""
Test script to debug write_results function
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.google_sheets import get_gspread_client, write_results
from backend.config import get_service_account_path, get_sheet_id


def test_write_results():
    """Test the write_results function"""
    print("🧪 Testing write_results function")
    print("=" * 40)

    try:
        # Get credentials and client
        service_account_path = get_service_account_path()
        sheet_id = get_sheet_id()
        client = get_gspread_client(service_account_path)

        print(f"✅ Connected to Google Sheets")
        print(f"📊 Sheet ID: {sheet_id}")

        # Test data
        test_results = [
            {
                "Item Description": "Test Item 1 - Gore Tex Jacket",
                "Current price": "$45.00",
                "Auction end date": "2024-12-31",
                "Auction image / thumbnail URL (extra credit)": "http://example.com/image1.jpg",
            },
            {
                "Item Description": "Test Item 2 - Vintage Watch",
                "Current price": "$120.00",
                "Auction end date": "2024-12-30",
                "Auction image / thumbnail URL (extra credit)": "http://example.com/image2.jpg",
            },
        ]

        print(f"📝 Writing {len(test_results)} test results...")

        # Write test results
        write_results(sheet_id, "test-keyword", test_results, client)

        print("✅ Successfully wrote test results to RESULTS TEMPLATE")
        print("📋 Check your Google Sheet to see the results!")

    except Exception as e:
        print(f"❌ Error testing write_results: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_write_results()
