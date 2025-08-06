"""Utility functions for the Coemeta WebScraper application.

This module provides a collection of utility functions used throughout
the application for tasks such as:
- Logging configuration and management
- Text processing and sanitization
- URL handling and validation
- Data extraction and formatting
- Validation of scraped data

These utilities are designed to be reusable across different parts
of the application and provide consistent behavior for common operations.

Example:
    >>> from utils import setup_logging, sanitize_keyword, clean_text
    >>> logger = setup_logging("INFO")
    >>> sanitized = sanitize_keyword("  Gore-Tex  Jacket  ")
    >>> cleaned = clean_text("  This   is   dirty   text  ")
"""

import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any, Callable
from urllib.parse import quote_plus, urljoin, urlparse


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up logging configuration for the application.

    Configures the logging system with appropriate handlers and formatting
    for both console output and file logging. This function creates a
    consistent logging setup across the application.

    The function configures:
    - A file handler that writes logs to 'scraper.log'
    - A console handler that outputs logs to the terminal
    - A consistent format for log messages with timestamp, level, and source

    Args:
        level: Logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            Default is "INFO".

    Returns:
        logging.Logger: Configured logger instance ready for use.

    Example:
        >>> logger = setup_logging("DEBUG")
        >>> logger.debug("Debug message")
        >>> logger.info("Info message")
        >>> logger.error("Error message")
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def sanitize_keyword(keyword: str) -> str:
    """Sanitize a keyword for use in URLs and search queries.

    Processes a raw keyword string to make it suitable for use in URLs
    and search queries. This function:
    1. Removes leading and trailing whitespace
    2. Converts the keyword to lowercase
    3. Normalizes internal whitespace (replaces multiple spaces with a single space)
    4. Replaces spaces with '+' characters for URL encoding

    Args:
        keyword: Raw keyword string to sanitize.
            Can contain any text, including extra whitespace.

    Returns:
        str: Sanitized keyword ready for use in URLs and search queries.

    Example:
        >>> sanitize_keyword("  Gore-Tex  Jacket  ")
        'gore-tex+jacket'
    """
    # Remove extra whitespace and convert to lowercase
    sanitized = re.sub(r"\s+", " ", keyword.strip().lower())
    # Replace spaces with + for URL encoding
    return sanitized.replace(" ", "+")


def validate_url(url: str) -> bool:
    """Validate if a string is a proper URL.

    Checks if a given string is a valid URL by parsing it and verifying
    that it has both a scheme (e.g., http, https) and a network location
    (domain). This function uses Python's built-in urlparse from urllib.parse.

    Args:
        url: URL string to validate.
            Should be a complete URL including scheme (e.g., "https://example.com").

    Returns:
        bool: True if the URL is valid (has both scheme and network location),
            False otherwise.

    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("example.com")
        False
        >>> validate_url("not a url")
        False
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_price(price_text: str) -> Optional[float]:
    """Extract numeric price from price text.

    Parses a string containing a price and extracts the numeric value,
    removing currency symbols and other non-numeric characters. This
    function handles various price formats including those with currency
    symbols, commas, and other decorations.

    Args:
        price_text: Price text to parse.
            Can be in various formats (e.g., "$123.45", "123.45", "123", "£100").

    Returns:
        Optional[float]: Extracted price as a float if successful,
            or None if the input is empty or cannot be parsed as a number.

    Example:
        >>> extract_price("$123.45")
        123.45
        >>> extract_price("€99,99")
        99.99
        >>> extract_price("")
        None
        >>> extract_price("Price not available")
        None
    """
    if not price_text:
        return None

    # Remove currency symbols and extra characters
    cleaned = re.sub(r"[^\d.]", "", price_text.strip())

    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def format_date(date_text: str) -> str:
    """Format date text to a consistent format.

    Cleans and normalizes date text to ensure consistent formatting.
    This function currently performs basic cleaning by removing extra
    whitespace, but could be extended to parse and standardize date formats.

    Args:
        date_text: Raw date text from scraping.
            Can contain extra whitespace and various date formats.

    Returns:
        str: Cleaned and formatted date string, or an empty string if
            the input is empty.

    Example:
        >>> format_date("  Dec 15, 2024  ")
        'Dec 15, 2024'
        >>> format_date("")
        ''
    """
    if not date_text:
        return ""

    # Remove extra whitespace
    cleaned = re.sub(r"\s+", " ", date_text.strip())
    return cleaned


def validate_auction_data(data: Dict[str, Any]) -> bool:
    """Validate auction data dictionary has required fields.

    Checks if a dictionary containing auction data has all the required fields.
    This function ensures that scraped data meets the minimum requirements
    for processing and storage.

    The required fields are:
    - Item Description: Description of the auction item
    - Auction end date: End date of the auction
    - Current price: Current price of the item
    - Auction image / thumbnail URL (extra credit): Image URL

    Args:
        data: Auction data dictionary to validate.
            Should contain key-value pairs representing auction data.

    Returns:
        bool: True if the dictionary contains all required fields,
            False otherwise.

    Example:
        >>> data = {
        ...     "Item Description": "Vintage Watch",
        ...     "Auction end date": "Dec 15, 2024",
        ...     "Current price": "$123.45",
        ...     "Auction image / thumbnail URL (extra credit)": "https://example.com/img.jpg"
        ... }
        >>> validate_auction_data(data)
        True
    """
    required_fields = [
        "Item Description",
        "Auction end date",
        "Current price",
        "Auction image / thumbnail URL (extra credit)",
    ]

    return all(field in data for field in required_fields)


def clean_text(text: str) -> str:
    """Clean and normalize text content.

    Processes raw text to clean and normalize it by removing extra whitespace
    and standardizing spacing. This function is useful for preparing text
    for display, storage, or further processing.

    Args:
        text: Raw text to clean.
            Can contain any text, including extra or inconsistent whitespace.

    Returns:
        str: Cleaned and normalized text with consistent spacing,
            or an empty string if the input is empty.

    Example:
        >>> clean_text("  This   is   dirty   text  ")
        'This is dirty text'
        >>> clean_text("")
        ''
    """
    if not text:
        return ""

    # Remove extra whitespace and normalize
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned


def build_search_url(base_url: str, keyword: str) -> str:
    """Build search URL with proper encoding.

    Constructs a complete search URL by combining a base URL with an
    encoded search keyword. This function properly encodes the keyword
    to ensure it's safe for use in a URL.

    Args:
        base_url: Base URL for the search.
            Should be a valid URL without the query parameters.
        keyword: Search keyword to include in the URL.
            Will be URL-encoded to handle special characters.

    Returns:
        str: Complete search URL with the encoded keyword.

    Example:
        >>> build_search_url("https://example.com", "vintage watch")
        'https://example.com/search?keywords=vintage%20watch&sort=Closing'
    """
    encoded_keyword = quote_plus(keyword)
    return f"{base_url}/search?keywords={encoded_keyword}&sort=Closing"


def get_user_agent() -> str:
    """Get a realistic user agent string for web scraping.

    Returns a modern and realistic user agent string that can be used
    for web scraping requests. Using a realistic user agent helps avoid
    detection by websites that block automated scrapers.

    The function first checks if a custom user agent is specified in the
    application configuration (SCRAPER_USER_AGENT). If not, it returns
    a default user agent string.

    Returns:
        str: A user agent string for web requests.
            Either the configured custom user agent or a default one.

    Example:
        >>> user_agent = get_user_agent()
        >>> user_agent.startswith("Mozilla/5.0")
        True
    """
    from config import get_config

    # Check if a custom user agent is configured
    custom_agent = get_config().SCRAPER_USER_AGENT
    if custom_agent:
        return custom_agent

    # Default user agent
    return (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )


def add_delay(seconds: Optional[float] = None) -> None:
    """Add a delay between requests to be respectful to the server.

    Pauses execution for the specified number of seconds to avoid
    overwhelming the target server with too many requests in a short
    period. This function helps implement ethical scraping practices
    and reduces the risk of being blocked.

    If no delay is specified, the function uses the SCRAPER_DELAY
    value from the application configuration.

    Args:
        seconds: Delay time in seconds.
            If None, uses the configured SCRAPER_DELAY.

    Returns:
        None

    Example:
        >>> import time
        >>> start = time.time()
        >>> add_delay(0.5)
        >>> elapsed = time.time() - start
        >>> elapsed >= 0.5
        True
    """
    from config import get_config

    if seconds is None:
        seconds = get_config().SCRAPER_DELAY

    time.sleep(seconds)


def format_results_for_sheets(
    results: List[Dict[str, str]], keyword: str
) -> List[List[str]]:
    """Format results for Google Sheets writing.

    Converts a list of auction result dictionaries into a format suitable
    for writing to Google Sheets. The function creates a 2D array where
    the first row contains column headers and subsequent rows contain
    the data from each result.

    Args:
        results: List of auction result dictionaries.
            Each dictionary should contain keys matching the required columns.
        keyword: Search keyword used to find these results.
            Will be included in each row of the formatted data.

    Returns:
        List[List[str]]: 2D array of formatted data ready for Google Sheets.
            First row contains column headers, and subsequent rows contain
            the data from each result.

    Example:
        >>> results = [{"Item Description": "Item 1", "Current price": "$10.00"}]
        >>> formatted = format_results_for_sheets(results, "test")
        >>> len(formatted)
        2  # Header row + 1 data row
    """
    headers = [
        "Keyword",
        "Item Description",
        "Auction end date",
        "Current price",
        "Auction image / thumbnail URL (extra credit)",
    ]

    formatted_data = [headers]

    for result in results:
        row = [
            keyword,
            result.get("Item Description", ""),
            result.get("Auction end date", ""),
            result.get("Current price", ""),
            result.get("Auction image / thumbnail URL (extra credit)", ""),
        ]
        formatted_data.append(row)

    return formatted_data


def log_scraping_stats(
    keyword: str, results_count: int, logger: logging.Logger
) -> None:
    """Log scraping statistics.

    Records statistics about a completed scraping operation to the provided
    logger. This function is useful for monitoring the performance and
    results of scraping operations.

    Args:
        keyword: Search keyword that was used for scraping.
        results_count: Number of results found for the keyword.
        logger: Logger instance to use for logging.
            Should be obtained from setup_logging().

    Returns:
        None

    Example:
        >>> import logging
        >>> logger = logging.getLogger()
        >>> log_scraping_stats("vintage watch", 5, logger)
        # Logs: "Scraped 5 results for keyword: 'vintage watch'"
    """
    logger.info(f"Scraped {results_count} results for keyword: '{keyword}'")


def handle_request_error(response: requests.Response, logger: logging.Logger) -> None:
    """Handle and log request errors.

    Processes HTTP response errors by logging relevant information and
    raising an appropriate exception. This function helps standardize
    error handling for HTTP requests throughout the application.

    This function is a wrapper around error_handling.handle_request_error
    for backward compatibility.

    Args:
        response: Response object from requests.
            Should be a requests.Response object with status_code and text attributes.
        logger: Logger instance to use for logging.
            Should be obtained from setup_logging().

    Returns:
        None

    Raises:
        NetworkError: If the response status code indicates an error.

    Example:
        >>> import requests
        >>> import logging
        >>> logger = logging.getLogger()
        >>> response = requests.get("https://httpbin.org/status/404")
        >>> try:
        ...     handle_request_error(response, logger)
        ... except Exception:
        ...     print("Error handled")
        Error handled
    """
    from error_handling import handle_request_error as new_handle_request_error

    # Use the new error handling function with a generic context
    new_handle_request_error(
        response=response, context="HTTP request", logger=logger, reraise=True
    )
