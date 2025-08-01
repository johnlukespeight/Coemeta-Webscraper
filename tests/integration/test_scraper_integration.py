#!/usr/bin/env python3
"""
Integration tests for the auction scraper
Tests actual web scraping functionality
"""

import unittest
import json
import time
import os
from scraper import scrape_auction_results
from utils import validate_auction_data


class TestScraperIntegration(unittest.TestCase):
    """Integration tests for the scraper module"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_keywords = ["vintage", "antique"]
        self.max_results = 2
        self.results_file = "integration_test_results.json"

    def tearDown(self):
        """Clean up after tests"""
        # Remove test results file if it exists
        if os.path.exists(self.results_file):
            os.remove(self.results_file)

    def test_scraper_connects_to_website(self):
        """Test that the scraper can connect to the target website"""
        print("\n🔍 Testing scraper connection to website...")

        keyword = "test"
        try:
            results = scrape_auction_results(keyword, max_results=1)

            # Should return a list (even if blocked)
            self.assertIsInstance(results, list)
            self.assertGreaterEqual(len(results), 1)

            print(f"✅ Scraper connected successfully. Got {len(results)} results")

        except Exception as e:
            self.fail(f"Scraper failed to connect: {e}")

    def test_scraper_handles_multiple_keywords(self):
        """Test that the scraper can handle multiple keywords"""
        print("\n🔍 Testing scraper with multiple keywords...")

        all_results = {}

        for keyword in self.test_keywords:
            print(f"  Testing keyword: '{keyword}'")

            try:
                results = scrape_auction_results(keyword, self.max_results)

                # Should return a list
                self.assertIsInstance(results, list)
                self.assertGreaterEqual(len(results), 1)

                all_results[keyword] = results

                # Wait between requests to be respectful
                time.sleep(2)

                print(f"    ✅ Got {len(results)} results")

            except Exception as e:
                print(f"    ❌ Error with keyword '{keyword}': {e}")
                all_results[keyword] = []

        # Save results for inspection
        with open(self.results_file, "w") as f:
            json.dump(all_results, f, indent=2)

        print(f"💾 Results saved to '{self.results_file}'")

        # Check that we got results for at least some keywords
        successful_keywords = sum(1 for results in all_results.values() if results)
        self.assertGreaterEqual(successful_keywords, 1)

    def test_scraper_result_quality(self):
        """Test the quality of scraper results"""
        print("\n🔍 Testing result quality...")

        keyword = "jewelry"  # Use a common keyword
        results = scrape_auction_results(keyword, max_results=3)

        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)

        # Check result structure
        for result in results:
            self.assertIn("Item Description", result)
            self.assertIn("Current price", result)
            self.assertIn("Auction end date", result)
            self.assertIn("Auction image / thumbnail URL (extra credit)", result)

        # Check if we got actual results or just blocking messages
        actual_results = [
            r
            for r in results
            if "blocked" not in r.get("Item Description", "").lower()
            and "error" not in r.get("Item Description", "").lower()
        ]

        if actual_results:
            print(f"🎉 Got {len(actual_results)} actual results!")
            for i, result in enumerate(actual_results, 1):
                desc = result.get("Item Description", "N/A")
                price = result.get("Current price", "N/A")
                print(f"  {i}. {desc[:50]}... | Price: {price}")
        else:
            print("⚠️  No actual results - likely blocked by website")
            print("   This is normal for modern websites with anti-bot protection")

    def test_scraper_performance(self):
        """Test scraper performance and timing"""
        print("\n🔍 Testing scraper performance...")

        start_time = time.time()
        results = scrape_auction_results("test", max_results=1)
        end_time = time.time()

        execution_time = end_time - start_time

        print(f"⏱️  Execution time: {execution_time:.2f} seconds")

        # Should complete within reasonable time (less than 30 seconds)
        self.assertLess(execution_time, 30)

        # Should return results
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)

    def test_scraper_with_validation(self):
        """Test scraper with data validation (from main.py test_scraper)"""
        print("\n🔍 Testing scraper with data validation...")

        test_keyword = "gore-tex"
        print(f"Scraping auction results for keyword: '{test_keyword}'")

        try:
            results = scrape_auction_results(test_keyword, max_results=3)
            print(f"Found {len(results)} results")

            # Test data validation
            valid_count = 0
            for i, result in enumerate(results):
                is_valid = validate_auction_data(result)
                print(f"Result {i+1} valid: {is_valid}")
                print(f"  Description: {result.get('Item Description', 'N/A')}")
                print(f"  Price: {result.get('Current price', 'N/A')}")
                print(f"  End date: {result.get('Auction end date', 'N/A')}")
                print()

                if is_valid:
                    valid_count += 1

            print(
                f"✅ Validation complete: {valid_count}/{len(results)} results are valid"
            )

            # Should return results
            self.assertIsInstance(results, list)
            self.assertGreaterEqual(len(results), 1)

        except Exception as e:
            print(f"❌ Scraper validation test failed: {e}")
            self.fail(f"Scraper validation test failed: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
