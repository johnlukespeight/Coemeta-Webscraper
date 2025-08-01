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
from config import get_service_account_path, get_sheet_id, validate_credentials


def main():
    """Main execution function that reads keywords from sheet and processes them"""
    print("🚀 Starting Coemeta WebScraper")
    print("=" * 50)

    # Setup logging
    logger = setup_logging("INFO")
    logger.info("Starting main execution")

    try:
        # Validate credentials first
        if not validate_credentials():
            print("❌ Please configure your Google Service Account credentials")
            print(
                "Set GOOGLE_SERVICE_ACCOUNT_PATH environment variable or place 'service_account.json' in the project root"
            )
            return

        # Initialize Google Sheets client
        service_account_path = get_service_account_path()
        client = get_gspread_client(service_account_path)
        print("✓ Google Sheets client authenticated successfully")

        # Read keywords from the sheet
        sheet_id = get_sheet_id()
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
