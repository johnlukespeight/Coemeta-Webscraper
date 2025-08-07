#!/usr/bin/env python3
"""
Integration tests for the full pipeline
Tests the complete workflow from keywords to results
"""

import unittest
import os
from backend.google_sheets import get_gspread_client, read_keywords, write_results
from backend.scraper import scrape_auction_results
from backend.utils import setup_logging, log_scraping_stats, validate_auction_data
from backend.config import get_service_account_path, get_sheet_id, validate_credentials


class TestFullPipelineIntegration(unittest.TestCase):
    """Integration tests for the full pipeline"""

    def setUp(self):
        """Set up test fixtures"""
        self.service_account_path = get_service_account_path()
        self.sheet_id = get_sheet_id()
        self.logger = setup_logging("INFO")

    def test_full_pipeline_with_test_keyword(self):
        """Test the complete pipeline with a test keyword"""
        print("\n🔍 Testing full pipeline with test keyword...")

        test_keyword = "vintage"

        try:
            # Step 1: Validate credentials
            if not validate_credentials():
                print("⚠️  Credentials not configured - skipping pipeline test")
                self.skipTest("Google Sheets credentials not configured")
                return

            # Step 2: Authenticate with Google Sheets
            client = get_gspread_client(self.service_account_path)
            print("✅ Step 1: Google Sheets authentication successful")

            # Step 3: Scrape results
            print(f"🔍 Step 2: Scraping results for keyword '{test_keyword}'")
            results = scrape_auction_results(test_keyword, max_results=3)

            self.assertIsInstance(results, list)
            self.assertGreaterEqual(len(results), 1)
            print(f"✅ Step 2: Found {len(results)} results")

            # Step 4: Validate results
            valid_results = 0
            for result in results:
                if validate_auction_data(result):
                    valid_results += 1

            print(f"✅ Step 3: {valid_results}/{len(results)} results are valid")

            # Step 5: Log statistics
            log_scraping_stats(test_keyword, len(results), self.logger)
            print("✅ Step 4: Logged scraping statistics")

            # Step 6: Write to Google Sheets (if we have valid results)
            if valid_results > 0:
                write_results(self.sheet_id, test_keyword, results, client)
                print("✅ Step 5: Results written to Google Sheets")
            else:
                print("⚠️  Step 5: No valid results to write to Google Sheets")

            print("✅ Full pipeline test completed successfully")

        except Exception as e:
            print(f"❌ Full pipeline test failed: {e}")
            # Don't fail the test if credentials aren't configured
            if "credentials" in str(e).lower():
                self.skipTest(f"Google Sheets credentials not configured: {e}")
            else:
                self.fail(f"Full pipeline test failed: {e}")

    def test_pipeline_with_multiple_keywords(self):
        """Test the pipeline with multiple keywords"""
        print("\n🔍 Testing pipeline with multiple keywords...")

        test_keywords = ["vintage", "antique"]
        total_results = 0

        try:
            # Validate credentials
            if not validate_credentials():
                print("⚠️  Credentials not configured - skipping multi-keyword test")
                self.skipTest("Google Sheets credentials not configured")
                return

            # Authenticate
            client = get_gspread_client(self.service_account_path)
            print("✅ Authentication successful")

            # Process each keyword
            for keyword in test_keywords:
                print(f"🔍 Processing keyword: '{keyword}'")

                # Scrape results
                results = scrape_auction_results(keyword, max_results=2)

                self.assertIsInstance(results, list)
                self.assertGreaterEqual(len(results), 1)

                print(f"  Found {len(results)} results for '{keyword}'")

                # Validate and count valid results
                valid_results = [r for r in results if validate_auction_data(r)]
                print(f"  {len(valid_results)} valid results")

                # Log statistics
                log_scraping_stats(keyword, len(results), self.logger)

                # Write to Google Sheets if we have valid results
                if valid_results:
                    write_results(self.sheet_id, keyword, results, client)
                    print(f"  ✅ Results written to Google Sheets")
                    total_results += len(results)
                else:
                    print(f"  ⚠️  No valid results to write")

            print(
                f"✅ Multi-keyword pipeline completed. Total results: {total_results}"
            )

        except Exception as e:
            print(f"❌ Multi-keyword pipeline failed: {e}")
            # Don't fail the test if credentials aren't configured
            if "credentials" in str(e).lower():
                self.skipTest(f"Google Sheets credentials not configured: {e}")
            else:
                self.fail(f"Multi-keyword pipeline failed: {e}")

    def test_pipeline_error_handling(self):
        """Test pipeline error handling"""
        print("\n🔍 Testing pipeline error handling...")

        # Test with an invalid keyword that might cause issues
        test_keyword = "invalid_keyword_that_should_not_exist"

        try:
            # Validate credentials
            if not validate_credentials():
                print("⚠️  Credentials not configured - skipping error handling test")
                self.skipTest("Google Sheets credentials not configured")
                return

            # Authenticate
            client = get_gspread_client(self.service_account_path)
            print("✅ Authentication successful")

            # Try to scrape with invalid keyword
            results = scrape_auction_results(test_keyword, max_results=1)

            # Should still return a list (even if empty or with error message)
            self.assertIsInstance(results, list)
            print(f"✅ Error handling test completed. Got {len(results)} results")

            # The scraper should handle errors gracefully
            if results:
                print("  Note: Scraper returned results despite invalid keyword")
            else:
                print("  Note: Scraper returned no results for invalid keyword")

        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            # Don't fail the test if credentials aren't configured
            if "credentials" in str(e).lower():
                self.skipTest(f"Google Sheets credentials not configured: {e}")
            else:
                self.fail(f"Error handling test failed: {e}")

    def test_pipeline_performance(self):
        """Test pipeline performance"""
        print("\n🔍 Testing pipeline performance...")

        import time

        start_time = time.time()

        try:
            # Validate credentials
            if not validate_credentials():
                print("⚠️  Credentials not configured - skipping performance test")
                self.skipTest("Google Sheets credentials not configured")
                return

            # Authenticate
            client = get_gspread_client(self.service_account_path)

            # Scrape a single keyword
            results = scrape_auction_results("test", max_results=1)

            end_time = time.time()
            execution_time = end_time - start_time

            print(f"⏱️  Pipeline execution time: {execution_time:.2f} seconds")

            # Should complete within reasonable time (less than 60 seconds)
            self.assertLess(execution_time, 60)

            # Should return results
            self.assertIsInstance(results, list)
            self.assertGreaterEqual(len(results), 1)

            print("✅ Performance test passed")

        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            # Don't fail the test if credentials aren't configured
            if "credentials" in str(e).lower():
                self.skipTest(f"Google Sheets credentials not configured: {e}")
            else:
                self.fail(f"Performance test failed: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
