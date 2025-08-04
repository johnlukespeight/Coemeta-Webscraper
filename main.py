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
import sys
import subprocess
import psutil
from pathlib import Path


def check_venv():
    """Check if virtual environment is activated"""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def setup_environment():
    """Setup virtual environment and install dependencies"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("Virtual environment created.")

    if not check_venv():
        print("Please activate virtual environment:")
        print("source venv/bin/activate")
        return False

    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully!")
    return True


def kill_streamlit_processes():
    """Kill any running Streamlit processes"""
    killed = False
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            if proc.info["name"] and "streamlit" in proc.info["name"].lower():
                print(f"Killing Streamlit process: {proc.info['pid']}")
                proc.terminate()
                killed = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not killed:
        print("No Streamlit processes found.")
    else:
        print("Streamlit processes terminated.")
    return killed


def clean_database():
    """Clean up database connections"""
    try:
        from database.database import close_database

        close_database()
        print("Database connections closed.")
    except ImportError:
        print("Database module not available.")
    except Exception as e:
        print(f"Error closing database: {e}")


def run_streamlit():
    """Run Streamlit app with proper cleanup"""
    if not check_venv():
        print("Please activate virtual environment first:")
        print("source venv/bin/activate")
        return False

    # Kill any existing Streamlit processes
    kill_streamlit_processes()

    # Clean database connections
    clean_database()

    print("Starting Streamlit app...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])


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
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "setup":
            setup_environment()
        elif command == "streamlit":
            run_streamlit()
        elif command == "kill":
            kill_streamlit_processes()
        elif command == "clean":
            clean_database()
        elif command == "help":
            print("Usage:")
            print("  python main.py              - Run the web scraper")
            print(
                "  python main.py setup        - Setup virtual environment and install dependencies"
            )
            print("  python main.py streamlit    - Run Streamlit app with cleanup")
            print("  python main.py kill         - Kill running Streamlit processes")
            print("  python main.py clean        - Clean database connections")
            print("  python main.py help         - Show this help message")
        else:
            print(f"Unknown command: {command}")
            print("Use 'python main.py help' for usage information")
    else:
        # Run the main execution function
        main()
