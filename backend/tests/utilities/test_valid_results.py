#!/usr/bin/env python3
"""
Test script to verify that valid results get written to Google Sheets
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from backend.google_sheets import get_gspread_client, write_results
from backend.config import get_service_account_path, get_sheet_id


def test_valid_results():
    """Test with valid auction results"""
    print("🧪 Testing write_results with valid auction data")
    print("=" * 50)

    try:
        # Get credentials and client
        service_account_path = get_service_account_path()
        sheet_id = get_sheet_id()
        client = get_gspread_client(service_account_path)

        print(f"✅ Connected to Google Sheets")

        # Valid auction results (simulating what the scraper should return)
        valid_results = [
            {
                "Item Description": "Gore-Tex Jacket - North Face",
                "Current price": "$45.00",
                "Auction end date": "2024-12-31 23:59:59",
                "Auction image / thumbnail URL (extra credit)": "https://example.com/jacket.jpg",
            },
            {
                "Item Description": "Vintage Rolex Watch",
                "Current price": "$1,200.00",
                "Auction end date": "2024-12-30 15:30:00",
                "Auction image / thumbnail URL (extra credit)": "https://example.com/watch.jpg",
            },
            {
                "Item Description": "Arc'teryx Beta AR Jacket",
                "Current price": "$89.99",
                "Auction end date": "2024-12-29 18:00:00",
                "Auction image / thumbnail URL (extra credit)": "https://example.com/arcteryx.jpg",
            },
        ]

        print(f"📝 Writing {len(valid_results)} valid auction results...")
        print("Sample result:", valid_results[0])

        # Write valid results
        write_results(sheet_id, "gore-tex", valid_results, client)

        print("✅ Successfully wrote valid auction results to RESULTS TEMPLATE")
        print("📋 Check your Google Sheet - you should see 3 rows of auction data!")

    except Exception as e:
        print(f"❌ Error testing valid results: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_valid_results()
