#!/usr/bin/env python3
"""
Test runner for the Coemeta WebScraper project
Runs both unit and integration tests
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running Unit Tests...")
    print("=" * 50)

    # Discover and run unit tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), "unit")
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_integration_tests():
    """Run integration tests"""
    print("\n🔍 Running Integration Tests...")
    print("=" * 50)

    # Discover and run integration tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), "integration")
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Test Suite for Coemeta WebScraper")
    print("=" * 60)

    # Run unit tests
    unit_success = run_unit_tests()

    # Run integration tests
    integration_success = run_integration_tests()

    # Summary
    print("\n📊 Test Summary")
    print("=" * 30)
    print(f"Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")

    overall_success = unit_success and integration_success
    print(
        f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}"
    )

    return overall_success


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
