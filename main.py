"""Main entry point for the Coemeta WebScraper application.

This module provides the command-line interface and main execution logic
for the web scraping application, including environment setup, process
management, and the core scraping workflow.

The application can be run in various modes:
- Default mode: Run the web scraper to process keywords from Google Sheets
- Setup mode: Configure the virtual environment and install dependencies
- Streamlit mode: Run the Streamlit web interface
- Test mode: Execute the test suite to verify functionality

Example:
    $ python main.py           # Run the web scraper
    $ python main.py setup     # Setup environment
    $ python main.py streamlit # Run Streamlit app
    $ python main.py test      # Run tests
"""

from typing import List, Optional, Dict, Any, Union, Callable
import sys
import subprocess
import psutil
from pathlib import Path
import logging
import traceback

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
from config import (
    get_config,
    get_service_account_path,
    get_sheet_id,
    validate_credentials,
    get_log_level,
)


def check_venv() -> bool:
    """Check if virtual environment is activated.

    Determines whether the current Python environment is a virtual environment
    by checking for the presence of virtual environment indicators.

    Returns:
        bool: True if running in a virtual environment, False otherwise.
    """
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def setup_environment() -> bool:
    """Setup virtual environment and install dependencies.

    Creates a virtual environment if it doesn't exist and installs
    all required dependencies from requirements.txt. This function
    checks if a virtual environment already exists before creating
    a new one and provides appropriate feedback to the user.

    Returns:
        bool: True if setup was successful, False otherwise.

    Note:
        This function requires the venv module to be available in the
        Python standard library. It will create a 'venv' directory in
        the current working directory if it doesn't exist.
    """
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


def kill_streamlit_processes() -> bool:
    """Kill any running Streamlit processes.

    Searches for and terminates any running Streamlit processes
    to ensure clean startup of new instances. This function uses
    the psutil library to find and terminate processes with 'streamlit'
    in their name.

    Returns:
        bool: True if processes were killed, False if none found.

    Note:
        This function requires the psutil module to be installed.
        It will catch and handle exceptions that may occur during
        process termination, such as access denied or process no longer
        existing.
    """
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


def clean_database() -> None:
    """Clean up database connections.

    Safely closes any open database connections to prevent
    resource leaks and ensure clean application shutdown.
    This function attempts to import the database module and
    call its close_database function. If the module is not available
    or an error occurs, appropriate error messages are displayed.

    Returns:
        None
    """
    try:
        from database.database import close_database

        close_database()
        print("Database connections closed.")
    except ImportError:
        print("Database module not available.")
    except Exception as e:
        print(f"Error closing database: {e}")


def run_streamlit() -> bool:
    """Run Streamlit app with proper cleanup.

    Ensures clean environment by killing existing processes and
    cleaning database connections before starting Streamlit.
    This function checks if the virtual environment is activated
    before running Streamlit and performs necessary cleanup operations.

    Returns:
        bool: True if Streamlit started successfully, False otherwise.

    Note:
        This function requires the streamlit module to be installed
        in the virtual environment. It will terminate any existing
        Streamlit processes before starting a new instance.
    """
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
    return True


def main() -> None:
    """Main execution function that reads keywords from sheet and processes them.

    Orchestrates the complete web scraping workflow:
    1. Validates credentials and establishes Google Sheets connection
    2. Reads keywords from the configured Google Sheet
    3. Scrapes auction results for each keyword
    4. Writes results back to the Google Sheet
    5. Logs progress and statistics

    The function handles all exceptions and provides appropriate error messages
    both to the console and to the log file. It uses environment variables or
    default values for configuration settings.

    Returns:
        None

    Raises:
        No exceptions are raised as they are caught and logged internally.
    """
    print("🚀 Starting Coemeta WebScraper")
    print("=" * 50)

    # Setup logging with configured log level
    config = get_config()
    logger = setup_logging(config.LOG_LEVEL)
    logger.info("Starting main execution with configuration:")
    logger.info(f"- Max results: {config.MAX_RESULTS}")
    logger.info(f"- Log level: {config.LOG_LEVEL}")
    logger.info(f"- Data directory: {config.DATA_DIR}")

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

            from error_handling import handle_error, ScrapingError, GoogleSheetsError

            try:
                # Scrape results for this keyword using configured max_results
                results = scrape_auction_results(
                    keyword, max_results=config.MAX_RESULTS
                )
                print(f"Found {len(results)} results for '{keyword}'")

                if results:
                    try:
                        # Write results to the sheet
                        write_results(sheet_id, keyword, results, client)
                        print(f"✓ Results written to sheet for keyword: '{keyword}'")
                        total_results += len(results)
                        log_scraping_stats(keyword, len(results), logger)
                    except Exception as sheet_error:
                        # Handle Google Sheets errors specifically
                        handle_error(
                            error=sheet_error,
                            context=f"Failed to write results for keyword '{keyword}'",
                            logger=logger,
                            reraise=False,
                            error_type=GoogleSheetsError,
                        )
                else:
                    print(f"⚠ No results found for keyword: '{keyword}'")
                    logger.warning(f"No results found for keyword: {keyword}")

            except Exception as e:
                # Handle scraping errors with our standardized error handling
                handle_error(
                    error=e,
                    context=f"Error processing keyword '{keyword}'",
                    logger=logger,
                    reraise=False,
                    error_type=ScrapingError,
                )

        print(f"\n✅ Processing complete! Total results: {total_results}")
        logger.info(f"Main execution completed. Total results: {total_results}")

    except Exception as e:
        from error_handling import handle_error, ScraperError

        # Handle the error with our standardized error handling
        handle_error(
            error=e,
            context="Main execution failed",
            logger=logger,
            reraise=False,  # Don't reraise to allow graceful exit
        )


def run_tests() -> bool:
    """Run all tests for the application.

    Executes the complete test suite to verify all components
    are working correctly. This function checks if the virtual
    environment is activated before running tests and provides
    appropriate error messages if tests fail.

    Returns:
        bool: True if all tests pass, False otherwise.

    Note:
        This function requires the tests module to be available
        and properly configured. It imports the run_all_tests function
        from tests.run_tests module.
    """
    if not check_venv():
        print("Please activate virtual environment first:")
        print("source venv/bin/activate")
        return False

    print("🧪 Running Test Suite...")
    try:
        # Import and run the test suite
        from tests.run_tests import run_all_tests

        success = run_all_tests()
        return success
    except ImportError as e:
        print(f"❌ Could not import test suite: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def print_usage() -> None:
    """Print usage information for the command-line interface.

    Displays all available commands and their descriptions
    to help users understand how to use the application.
    This function prints a formatted list of commands and
    their descriptions to the standard output.

    Returns:
        None
    """
    print("Usage:")
    print("  python main.py              - Run the web scraper")
    print(
        "  python main.py setup        - Setup virtual environment and install dependencies"
    )
    print("  python main.py streamlit    - Run Streamlit app with cleanup")
    print("  python main.py test         - Run all tests")
    print("  python main.py kill         - Kill running Streamlit processes")
    print("  python main.py clean        - Clean database connections")
    print("  python main.py help         - Show this help message")


def handle_command(command: str) -> bool:
    """Handle command-line arguments and execute appropriate functions.

    Processes the command-line argument and calls the corresponding
    function to perform the requested operation.

    Args:
        command: The command to execute (setup, streamlit, test, etc.).
            Valid commands include:
            - 'setup': Configure virtual environment and install dependencies
            - 'streamlit': Run the Streamlit web interface
            - 'test': Execute the test suite
            - 'kill': Terminate running Streamlit processes
            - 'clean': Clean up database connections
            - 'help': Display usage information

    Returns:
        bool: True if command was executed successfully, False otherwise.
    """
    command = command.lower()

    if command == "setup":
        return setup_environment()
    elif command == "streamlit":
        return run_streamlit()
    elif command == "test":
        return run_tests()
    elif command == "kill":
        kill_streamlit_processes()
        return True
    elif command == "clean":
        clean_database()
        return True
    elif command == "help":
        print_usage()
        return True
    else:
        print(f"Unknown command: {command}")
        print("Use 'python main.py help' for usage information")
        return False


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        handle_command(command)
    else:
        # Run the main execution function
        main()
