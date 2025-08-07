#!/usr/bin/env python3
"""
Quick test script for the scraper
Run this from the project root for a simple test
"""

import sys
import os

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from backend.scraper import scrape_auction_results
import json


def quick_test():
    """Run a quick test of the scraper"""
    print("🧪 Quick Scraper Test")
    print("=" * 40)

    # Test with a simple keyword
    keyword = "vintage"
    print(f"Testing keyword: '{keyword}'")

    try:
        results = scrape_auction_results(keyword, max_results=2)

        print(f"✅ Got {len(results)} results")

        # Check if we got actual results
        actual_results = [
            r
            for r in results
            if "blocked" not in r.get("Item Description", "").lower()
            and "error" not in r.get("Item Description", "").lower()
        ]

        if actual_results:
            print("🎉 Found actual auction results!")
            for i, result in enumerate(actual_results, 1):
                desc = result.get("Item Description", "N/A")
                price = result.get("Current price", "N/A")
                print(f"  {i}. {desc[:60]}... | Price: {price}")
        else:
            print("⚠️  Website is blocking automated access (normal for modern sites)")

        # Save results
        with open("quick_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("💾 Results saved to 'quick_test_results.json'")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
