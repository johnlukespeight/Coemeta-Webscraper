from google_sheets import get_gspread_client, write_results, read_keywords
from scraper import scrape_auction_results
from utils import (
    setup_logging,
    sanitize_keyword,
    clean_text,
    log_scraping_stats,
    validate_auction_data,
    extract_price,
    format_date,
)


def test_utils():
    """Test utility functions"""
    print("\n=== Testing Utility Functions ===")

    # Test keyword sanitization
    test_keyword = "  Gore-Tex  Jacket  "
    sanitized = sanitize_keyword(test_keyword)
    print(f"Original keyword: '{test_keyword}'")
    print(f"Sanitized keyword: '{sanitized}'")

    # Test text cleaning
    dirty_text = "  This   is   dirty   text  "
    cleaned = clean_text(dirty_text)
    print(f"Dirty text: '{dirty_text}'")
    print(f"Cleaned text: '{cleaned}'")

    # Test price extraction
    price_tests = ["$123.45", "123.45", "123", "Invalid", ""]
    for price in price_tests:
        extracted = extract_price(price)
        print(f"Price text: '{price}' -> Extracted: {extracted}")

    # Test date formatting
    date_tests = ["  Dec 15, 2024  ", "Invalid date", ""]
    for date in date_tests:
        formatted = format_date(date)
        print(f"Date text: '{date}' -> Formatted: '{formatted}'")


def test_scraper():
    """Test the scraper functionality"""
    print("\n=== Testing Scraper ===")

    test_keyword = "gore-tex"
    print(f"Scraping auction results for keyword: '{test_keyword}'")

    try:
        results = scrape_auction_results(test_keyword, max_results=3)
        print(f"Found {len(results)} results")

        # Test data validation
        for i, result in enumerate(results):
            is_valid = validate_auction_data(result)
            print(f"Result {i+1} valid: {is_valid}")
            print(f"  Description: {result.get('Item Description', 'N/A')}")
            print(f"  Price: {result.get('Current price', 'N/A')}")
            print(f"  End date: {result.get('Auction end date', 'N/A')}")
            print()

        return results

    except Exception as e:
        print(f"Scraper error: {e}")
        return []


def test_google_sheets():
    """Test Google Sheets integration"""
    print("\n=== Testing Google Sheets ===")

    try:
        # Test client authentication
        client = get_gspread_client(
            "/Users/nezamsp8/Developer/Coemeta WebScraper/spartan-rhino-434020-h1-a244eeb7b709.json"
        )
        print("✓ Google Sheets client authenticated successfully")

        # Test reading keywords (if sheet exists)
        sheet_id = "1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo"
        try:
            keywords = read_keywords(sheet_id, client)
            print(f"✓ Read {len(keywords)} keywords from sheet")
            print(f"Keywords: {keywords[:3]}...")  # Show first 3
        except Exception as e:
            print(f"⚠ Could not read keywords: {e}")

        return client

    except Exception as e:
        print(f"✗ Google Sheets error: {e}")
        return None


def test_full_pipeline():
    """Test the complete pipeline"""
    print("\n=== Testing Full Pipeline ===")

    # Setup logging
    logger = setup_logging("INFO")
    logger.info("Starting full pipeline test")

    # Test scraper
    results = test_scraper()
    if results:
        log_scraping_stats("gore-tex", len(results), logger)

        # Test Google Sheets integration
        client = test_google_sheets()
        if client:
            try:
                sheet_id = "1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo"
                write_results(sheet_id, "gore-tex", results, client)
                print("✓ Results written to Google Sheets successfully")
                logger.info("Full pipeline completed successfully")
            except Exception as e:
                print(f"✗ Failed to write to Google Sheets: {e}")
                logger.error(f"Failed to write to Google Sheets: {e}")
    else:
        print("✗ No results to write to Google Sheets")
        logger.warning("No results found for pipeline test")


def main():
    """Main execution function that reads keywords from sheet and processes them"""
    print("🚀 Starting Coemeta WebScraper")
    print("=" * 50)

    # Setup logging
    logger = setup_logging("INFO")
    logger.info("Starting main execution")

    try:
        # Initialize Google Sheets client
        client = get_gspread_client(
            "/Users/nezamsp8/Developer/Coemeta WebScraper/spartan-rhino-434020-h1-a244eeb7b709.json"
        )
        print("✓ Google Sheets client authenticated successfully")

        # Read keywords from the sheet
        sheet_id = "1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo"
        keywords = read_keywords(sheet_id, client)
        print(f"✓ Read {len(keywords)} keywords from sheet")
        print(f"Keywords: {keywords}")

        if not keywords:
            print("❌ No keywords found in the sheet!")
            return

        # Process each keyword
        total_results = 0
        for keyword in keywords:
            print(f"\n🔍 Processing keyword: '{keyword}'")
            logger.info(f"Processing keyword: {keyword}")

            try:
                # Scrape results for this keyword
                results = scrape_auction_results(keyword, max_results=10)
                print(f"Found {len(results)} results for '{keyword}'")

                if results:
                    # Write results to the sheet
                    write_results(sheet_id, keyword, results, client)
                    print(f"✓ Results written to sheet for keyword: '{keyword}'")
                    total_results += len(results)
                    log_scraping_stats(keyword, len(results), logger)
                else:
                    print(f"⚠ No results found for keyword: '{keyword}'")
                    logger.warning(f"No results found for keyword: {keyword}")

            except Exception as e:
                print(f"❌ Error processing keyword '{keyword}': {e}")
                logger.error(f"Error processing keyword {keyword}: {e}")

        print(f"\n✅ Processing complete! Total results: {total_results}")
        logger.info(f"Main execution completed. Total results: {total_results}")

    except Exception as e:
        print(f"❌ Main execution failed: {e}")
        logger.error(f"Main execution failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the main execution function
    main()
