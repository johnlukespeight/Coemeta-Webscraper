#!/usr/bin/env python3
"""
Test script to scrape items using keywords from the [KEYWORDS] worksheet
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from google_sheets import get_gspread_client, read_keywords, write_results
from scraper import AntiDetectionScraper
from config import get_service_account_path, get_sheet_id
import time


def test_keywords_scraping():
    """Test scraping with keywords from the [KEYWORDS] worksheet"""
    print("🔍 Testing scraper with keywords from [KEYWORDS] worksheet")
    print("=" * 60)

    try:
        # Get credentials and client
        service_account_path = get_service_account_path()
        sheet_id = get_sheet_id()
        client = get_gspread_client(service_account_path)

        print(f"✅ Connected to Google Sheets")

        # Read keywords from the [KEYWORDS] worksheet
        keywords = read_keywords(sheet_id, client)
        print(f"📋 Found {len(keywords)} keywords: {keywords}")

        if not keywords:
            print("❌ No keywords found in [KEYWORDS] worksheet")
            return

        # Initialize scraper
        scraper = AntiDetectionScraper()

        # Test with the first keyword
        test_keyword = keywords[0]
        print(f"\n🎯 Testing with keyword: '{test_keyword}'")
        print("-" * 40)

        # Scrape results
        results = scraper.scrape_with_retry(test_keyword, max_results=5)

        if results and len(results) > 0:
            print(f"✅ Successfully scraped {len(results)} results")

            # Display results
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.get('Item Description', 'N/A')}")
                print(f"     Price: {result.get('Current price', 'N/A')}")
                print(f"     End Date: {result.get('Auction end date', 'N/A')}")
                print(
                    f"     Image: {result.get('Auction image / thumbnail URL (extra credit)', 'N/A')}"
                )
                print()

            # Write results to Google Sheets
            print("📊 Writing results to Google Sheets...")
            write_results(sheet_id, test_keyword, results, client)
            print("✅ Results written to RESULTS TEMPLATE worksheet")

        else:
            print("❌ No results found for this keyword")

    except Exception as e:
        print(f"❌ Error testing keywords scraping: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_keywords_scraping()
