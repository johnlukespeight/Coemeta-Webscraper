#!/usr/bin/env python3
"""
Test script to verify image integration with Google Sheets
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from backend.google_sheets import get_gspread_client, write_results
from backend.config import get_service_account_path, get_sheet_id


def test_image_integration():
    """Test writing results with images to Google Sheets"""
    print("🖼️ Testing image integration with Google Sheets")
    print("=" * 50)

    try:
        # Get credentials and client
        service_account_path = get_service_account_path()
        sheet_id = get_sheet_id()
        client = get_gspread_client(service_account_path)

        print(f"✅ Connected to Google Sheets")

        # Test data with real image URLs
        test_results = [
            {
                "Item Description": "Gore-Tex Jacket - North Face",
                "Current price": "$45.00",
                "Auction end date": "2024-12-31 23:59:59",
                "Auction image / thumbnail URL (extra credit)": "https://via.placeholder.com/150x150/0066cc/ffffff?text=Jacket",
            },
            {
                "Item Description": "Vintage Rolex Watch",
                "Current price": "$1,200.00",
                "Auction end date": "2024-12-30 15:30:00",
                "Auction image / thumbnail URL (extra credit)": "https://via.placeholder.com/150x150/cc6600/ffffff?text=Watch",
            },
            {
                "Item Description": "Arc'teryx Beta AR Jacket",
                "Current price": "$89.99",
                "Auction end date": "2024-12-29 18:00:00",
                "Auction image / thumbnail URL (extra credit)": "https://via.placeholder.com/150x150/00cc66/ffffff?text=Arc'teryx",
            },
        ]

        print(f"📝 Writing {len(test_results)} results with images...")
        for i, result in enumerate(test_results, 1):
            print(
                f"  {i}. {result['Item Description']} - Image: {result['Auction image / thumbnail URL (extra credit)']}"
            )

        # Write results with images
        write_results(sheet_id, "test-images", test_results, client)

        print("✅ Successfully wrote results with images to RESULTS TEMPLATE")
        print("📋 Check your Google Sheet - you should see images in column E!")

    except Exception as e:
        print(f"❌ Error testing image integration: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_image_integration()
