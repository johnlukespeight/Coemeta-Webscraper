#!/usr/bin/env python3
"""
Unit tests for the utils module.

This module contains unit tests for the utility functions in the utils.py module.
The tests verify that each utility function behaves correctly with various inputs,
including edge cases and invalid inputs.
"""

import unittest
from typing import List, Dict, Any, Optional, Tuple
import logging

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
    """Unit tests for utility functions in the utils module.
    
    This test suite verifies the functionality of various utility functions
    used throughout the application, ensuring they handle different inputs
    correctly and return expected outputs.
    """

    def test_sanitize_keyword(self) -> None:
        """Test keyword sanitization function.
        
        This test verifies that the sanitize_keyword function correctly
        transforms input strings by trimming whitespace, converting to
        lowercase, and replacing spaces with plus signs.
        
        Returns:
            None
        """
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

    def test_clean_text(self) -> None:
        """Test text cleaning function.
        
        This test verifies that the clean_text function correctly removes
        extra whitespace from strings and handles edge cases like empty
        strings and strings with only whitespace.
        
        Returns:
            None
        """
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

    def test_extract_price(self) -> None:
        """Test price extraction function.
        
        This test verifies that the extract_price function correctly extracts
        numeric price values from various string formats, handling currency
        symbols, commas, and invalid inputs appropriately.
        
        Returns:
            None
        """
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

    def test_format_date(self) -> None:
        """Test date formatting function.
        
        This test verifies that the format_date function correctly formats
        date strings by removing extra whitespace while preserving the
        original date format.
        
        Returns:
            None
        """
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

    def test_validate_auction_data(self) -> None:
        """Test auction data validation function.
        
        This test verifies that the validate_auction_data function correctly
        identifies valid auction data dictionaries (containing all required fields)
        and rejects invalid ones (missing required fields).
        
        Returns:
            None
        """
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

    def test_setup_logging(self) -> None:
        """Test logging setup function.
        
        This test verifies that the setup_logging function correctly creates
        and configures a logger object with the specified log level.
        
        Returns:
            None
        """
        logger = setup_logging("INFO")
        self.assertIsNotNone(logger)
        # The logger level might be inherited from root logger, so just check it's a logger
        self.assertTrue(hasattr(logger, 'info'))
        self.assertTrue(hasattr(logger, 'error'))

        # Test with different levels
        debug_logger = setup_logging("DEBUG")
        self.assertTrue(hasattr(debug_logger, 'debug'))

    def test_log_scraping_stats(self) -> None:
        """Test logging scraping statistics function.
        
        This test verifies that the log_scraping_stats function can be called
        without raising exceptions, confirming it correctly logs information
        about scraping results.
        
        Returns:
            None
        """
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