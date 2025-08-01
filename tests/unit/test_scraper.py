#!/usr/bin/env python3
"""
Unit tests for the auction scraper
"""

import unittest
from unittest.mock import patch, MagicMock
from scraper import scrape_auction_results
import json
import tempfile
import os


class TestScraper(unittest.TestCase):
    """Unit tests for the scraper module"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_keyword = "test_item"
        self.max_results = 5

    def test_scraper_function_exists(self):
        """Test that the scrape_auction_results function exists and is callable"""
        self.assertTrue(callable(scrape_auction_results))

    def test_scraper_returns_list(self):
        """Test that the scraper returns a list"""
        # Mock the webdriver to avoid actual web requests
        with patch("scraper.webdriver.Chrome") as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver.return_value = mock_driver_instance

            # Mock page source to simulate blocking
            mock_driver_instance.page_source = "<html><body>blocked</body></html>"

            results = scrape_auction_results(self.test_keyword, self.max_results)
            self.assertIsInstance(results, list)

    def test_scraper_handles_blocking(self):
        """Test that the scraper properly handles website blocking"""
        with patch("scraper.webdriver.Chrome") as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver.return_value = mock_driver_instance

            # Mock page source with blocking indicators
            mock_driver_instance.page_source = (
                "<html><body>blocked captcha</body></html>"
            )

            results = scrape_auction_results(self.test_keyword, self.max_results)

            # Should return a fallback result when blocked
            self.assertEqual(len(results), 1)
            self.assertIn("blocked", results[0]["Item Description"].lower())

    def test_scraper_handles_exceptions(self):
        """Test that the scraper handles exceptions gracefully"""
        with patch("scraper.webdriver.Chrome") as mock_driver:
            mock_driver.side_effect = Exception("Test exception")

            results = scrape_auction_results(self.test_keyword, self.max_results)

            # Should return a fallback result when exception occurs
            self.assertEqual(len(results), 1)
            self.assertIn("error", results[0]["Item Description"].lower())

    def test_scraper_result_structure(self):
        """Test that scraper results have the expected structure"""
        with patch("scraper.webdriver.Chrome") as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver.return_value = mock_driver_instance

            # Mock page source with blocking
            mock_driver_instance.page_source = "<html><body>blocked</body></html>"

            results = scrape_auction_results(self.test_keyword, self.max_results)

            if results:
                result = results[0]
                expected_keys = [
                    "Item Description",
                    "Current price",
                    "Auction end date",
                    "Auction image / thumbnail URL (extra credit)",
                ]

                for key in expected_keys:
                    self.assertIn(key, result)

    def test_scraper_respects_max_results(self):
        """Test that the scraper respects the max_results parameter"""
        with patch("scraper.webdriver.Chrome") as mock_driver:
            mock_driver_instance = MagicMock()
            mock_driver.return_value = mock_driver_instance

            # Mock page source with blocking
            mock_driver_instance.page_source = "<html><body>blocked</body></html>"

            # Test with different max_results values
            for max_results in [1, 3, 5]:
                results = scrape_auction_results(self.test_keyword, max_results)
                # Should return at least one result (fallback) but not more than max_results
                self.assertGreaterEqual(len(results), 1)
                self.assertLessEqual(len(results), max_results)


if __name__ == "__main__":
    unittest.main()
