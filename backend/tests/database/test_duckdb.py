#!/usr/bin/env python3
"""
Test script for DuckDB integration
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

import pandas as pd
from backend.database.database import AuctionDatabase


def test_duckdb_integration():
    """Test DuckDB database functionality"""
    print("🦆 Testing DuckDB Integration")
    print("=" * 50)

    try:
        # Initialize database
        db = AuctionDatabase("database/test_auction_data.duckdb")
        print("✅ Database initialized successfully")

        # Test data
        test_results = [
            {
                "Item Description": "Test Item 1",
                "Current price": "$100.00",
                "Auction end date": "2024-12-31",
                "Auction image / thumbnail URL (extra credit)": "http://example.com/image1.jpg",
            },
            {
                "Item Description": "Test Item 2",
                "Current price": "$200.00",
                "Auction end date": "2024-12-30",
                "Auction image / thumbnail URL (extra credit)": "http://example.com/image2.jpg",
            },
        ]

        # Test insertion
        print("\n📝 Testing data insertion...")
        inserted_count = db.insert_auction_results("test-keyword", test_results)
        print(f"✅ Inserted {inserted_count} records")

        # Test querying
        print("\n🔍 Testing data querying...")
        results = db.get_auction_results(keyword="test-keyword")
        print(f"✅ Retrieved {len(results)} records")

        # Test statistics
        print("\n📊 Testing statistics...")
        stats = db.get_database_stats()
        print(f"✅ Database stats: {stats['total_records']} total records")

        # Test keyword stats
        print("\n📈 Testing keyword statistics...")
        keyword_stats = db.get_keyword_stats()
        print(f"✅ Keyword stats: {len(keyword_stats)} keywords")

        # Test price analytics
        print("\n💰 Testing price analytics...")
        price_stats = db.get_price_analytics()
        print(f"✅ Price analytics: avg=${price_stats.get('avg_price', 0):.2f}")

        # Test search
        print("\n🔎 Testing search functionality...")
        search_results = db.search_items("Test Item")
        print(f"✅ Search results: {len(search_results)} items found")

        # Test export
        print("\n📤 Testing export functionality...")
        db.export_to_csv("test_export.csv")
        print("✅ Export completed")

        # Clean up
        db.close()
        import os

        if os.path.exists("database/test_auction_data.duckdb"):
            os.remove("database/test_auction_data.duckdb")
        if os.path.exists("test_export.csv"):
            os.remove("test_export.csv")

        print("\n🎉 All DuckDB tests passed!")
        return True

    except Exception as e:
        print(f"❌ DuckDB test failed: {e}")
        return False


if __name__ == "__main__":
    test_duckdb_integration()
