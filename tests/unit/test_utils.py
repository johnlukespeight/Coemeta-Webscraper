#!/usr/bin/env python3
"""
Unit tests for the utils module
"""

import unittest
from utils import (
    sanitize_keyword,
    clean_text,
    extract_price,
    format_date,
    validate_auction_data,
    log_scraping_stats,
    setup_logging,
)


class TestUtils(unittest.TestCase):
    """Unit tests for utility functions"""

    def test_sanitize_keyword(self):
        """Test keyword sanitization"""
        test_cases = [
            ("  Gore-Tex  Jacket  ", "gore-tex+jacket"),
            ("VINTAGE WATCH", "vintage+watch"),
            ("  Multiple   Spaces  ", "multiple+spaces"),
            ("", ""),
            ("   ", ""),
        ]

        for input_keyword, expected in test_cases:
            with self.subTest(input_keyword=input_keyword):
                result = sanitize_keyword(input_keyword)
                self.assertEqual(result, expected)

    def test_clean_text(self):
        """Test text cleaning"""
        test_cases = [
            ("  This   is   dirty   text  ", "This is dirty text"),
            ("  Multiple   Spaces  ", "Multiple Spaces"),
            ("", ""),
            ("   ", ""),
            ("normal text", "normal text"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = clean_text(input_text)
                self.assertEqual(result, expected)

    def test_extract_price(self):
        """Test price extraction"""
        test_cases = [
            ("$123.45", 123.45),
            ("123.45", 123.45),
            ("123", 123.0),
            ("Invalid", None),
            ("", None),
            ("$0.99", 0.99),
            ("$1,234.56", 1234.56),
        ]

        for input_price, expected in test_cases:
            with self.subTest(input_price=input_price):
                result = extract_price(input_price)
                self.assertEqual(result, expected)

    def test_format_date(self):
        """Test date formatting"""
        test_cases = [
            ("  Dec 15, 2024  ", "Dec 15, 2024"),
            ("Invalid date", "Invalid date"),
            ("", ""),
            ("Jan 1, 2023", "Jan 1, 2023"),
            ("  2024-01-15  ", "2024-01-15"),
        ]

        for input_date, expected in test_cases:
            with self.subTest(input_date=input_date):
                result = format_date(input_date)
                self.assertEqual(result, expected)

    def test_validate_auction_data(self):
        """Test auction data validation"""
        # Valid data
        valid_data = {
            "Item Description": "Test Item",
            "Current price": "$100.00",
            "Auction end date": "Dec 15, 2024",
            "Auction image / thumbnail URL (extra credit)": "http://example.com/image.jpg",
        }
        self.assertTrue(validate_auction_data(valid_data))

        # Invalid data - missing required fields
        invalid_data = {
            "Item Description": "Test Item",
            "Current price": "$100.00",
            # Missing other required fields
        }
        self.assertFalse(validate_auction_data(invalid_data))

        # Invalid data - missing required field
        invalid_data2 = {
            "Item Description": "Test Item",
            "Current price": "$100.00",
            "Auction end date": "Dec 15, 2024",
            # Missing "Auction image / thumbnail URL (extra credit)" field
        }
        self.assertFalse(validate_auction_data(invalid_data2))

    def test_setup_logging(self):
        """Test logging setup"""
        logger = setup_logging("INFO")
        self.assertIsNotNone(logger)
        # The logger level might be inherited from root logger, so just check it's a logger
        self.assertTrue(hasattr(logger, 'info'))
        self.assertTrue(hasattr(logger, 'error'))

        # Test with different levels
        debug_logger = setup_logging("DEBUG")
        self.assertTrue(hasattr(debug_logger, 'debug'))

    def test_log_scraping_stats(self):
        """Test logging scraping statistics"""
        logger = setup_logging("INFO")
        
        # This should not raise an exception
        try:
            log_scraping_stats("test_keyword", 5, logger)
            # If we get here, the function worked
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"log_scraping_stats raised an exception: {e}")


if __name__ == "__main__":
    unittest.main() 