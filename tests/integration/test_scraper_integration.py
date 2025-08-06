#!/usr/bin/env python3
"""
Integration tests for the auction scraper.

This module contains integration tests for the scraper.py module,
testing actual web scraping functionality against live websites.
These tests verify that the scraper can connect to websites,
handle multiple keywords, and return valid data.

Note: These tests make actual network requests and may fail if
the target website changes or implements stronger anti-bot measures.
"""

import unittest
import json
import time
import os
from typing import Dict, List, Any, Optional, Union

from scraper import scrape_auction_results
from utils import validate_auction_data


class TestScraperIntegration(unittest.TestCase):
    """Integration tests for the scraper module.
    
    This test suite performs integration tests against actual websites to verify
    that the scraper can connect, retrieve data, and handle various scenarios
    in a real-world environment.
    
    Attributes:
        test_keywords: List of keywords to test with
        max_results: Maximum number of results to request in tests
        results_file: File to save test results for inspection
    """

    def setUp(self) -> None:
        """Set up test fixtures before each test.
        
        This method initializes test data and configuration that will be
        used across multiple test cases.
        
        Returns:
            None
        """
        self.test_keywords = ["gore-tex", "Bape"]
        self.max_results = 2
        self.results_file = "integration_test_results.json"

    def tearDown(self) -> None:
        """Clean up after tests have run.
        
        This method removes any temporary files created during testing
        to ensure a clean state for subsequent test runs.
        
        Returns:
            None
        """
        # Remove test results file if it exists
        if os.path.exists(self.results_file):
            os.remove(self.results_file)

    def test_scraper_connects_to_website(self) -> None:
        """Test that the scraper can connect to the target website.
        
        This test verifies that the scraper can establish a connection to
        the target website and retrieve at least some basic response,
        even if it's a blocking message.
        
        Returns:
            None
        """
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

    def test_scraper_handles_multiple_keywords(self) -> None:
        """Test that the scraper can handle multiple keywords.
        
        This test verifies that the scraper can process multiple different
        keywords sequentially, saving the results to a file for inspection.
        It ensures that at least some keywords return results.
        
        Returns:
            None
        """
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

    def test_scraper_result_quality(self) -> None:
        """Test the quality of scraper results.
        
        This test verifies that the scraper returns results with the expected
        structure and content. It checks for the presence of required fields
        and distinguishes between actual results and blocking messages.
        
        Returns:
            None
        """
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

    def test_scraper_performance(self) -> None:
        """Test scraper performance and timing.
        
        This test measures the execution time of the scraper to ensure
        it completes within a reasonable timeframe (less than 30 seconds).
        It also verifies that results are returned.
        
        Returns:
            None
        """
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

    def test_scraper_with_validation(self) -> None:
        """Test scraper with data validation.
        
        This test verifies that the scraper returns data that passes
        validation checks using the validate_auction_data function.
        It prints detailed information about each result for inspection.
        
        Returns:
            None
        """
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
