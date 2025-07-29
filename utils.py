import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Union
from urllib.parse import quote_plus, urljoin, urlparse


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the application.

    Args:
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


def sanitize_keyword(keyword: str) -> str:
    """
    Sanitize a keyword for use in URLs and search queries.

    Args:
        keyword (str): Raw keyword string

    Returns:
        str: Sanitized keyword
    """
    # Remove extra whitespace and convert to lowercase
    sanitized = re.sub(r"\s+", " ", keyword.strip().lower())
    # Replace spaces with + for URL encoding
    return sanitized.replace(" ", "+")


def validate_url(url: str) -> bool:
    """
    Validate if a string is a proper URL.

    Args:
        url (str): URL string to validate

    Returns:
        bool: True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_price(price_text: str) -> Optional[float]:
    """
    Extract numeric price from price text.

    Args:
        price_text (str): Price text (e.g., "$123.45", "123.45", "123")

    Returns:
        Optional[float]: Extracted price as float, or None if invalid
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
    """
    Format date text to a consistent format.

    Args:
        date_text (str): Raw date text from scraping

    Returns:
        str: Formatted date string
    """
    if not date_text:
        return ""

    # Remove extra whitespace
    cleaned = re.sub(r"\s+", " ", date_text.strip())
    return cleaned


def validate_auction_data(data: Dict) -> bool:
    """
    Validate auction data dictionary has required fields.

    Args:
        data (Dict): Auction data dictionary

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = [
        "Item Description",
        "Auction end date",
        "Current price",
        "Auction image / thumbnail URL (extra credit)",
    ]

    return all(field in data for field in required_fields)


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.

    Args:
        text (str): Raw text to clean

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace and normalize
    cleaned = re.sub(r"\s+", " ", text.strip())
    return cleaned


def build_search_url(base_url: str, keyword: str) -> str:
    """
    Build search URL with proper encoding.

    Args:
        base_url (str): Base URL for the search
        keyword (str): Search keyword

    Returns:
        str: Complete search URL
    """
    encoded_keyword = quote_plus(keyword)
    return f"{base_url}/search?keywords={encoded_keyword}&sort=Closing"


def get_user_agent() -> str:
    """
    Get a realistic user agent string for web scraping.

    Returns:
        str: User agent string
    """
    return (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )


def add_delay(seconds: float = 1.0) -> None:
    """
    Add a delay between requests to be respectful to the server.

    Args:
        seconds (float): Delay time in seconds
    """
    time.sleep(seconds)


def format_results_for_sheets(results: List[Dict], keyword: str) -> List[List]:
    """
    Format results for Google Sheets writing.

    Args:
        results (List[Dict]): List of auction result dictionaries
        keyword (str): Search keyword

    Returns:
        List[List]: Formatted data ready for Google Sheets
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
    """
    Log scraping statistics.

    Args:
        keyword (str): Search keyword
        results_count (int): Number of results found
        logger (logging.Logger): Logger instance
    """
    logger.info(f"Scraped {results_count} results for keyword: '{keyword}'")


def handle_request_error(response, logger: logging.Logger) -> None:
    """
    Handle and log request errors.

    Args:
        response: Response object from requests
        logger (logging.Logger): Logger instance
    """
    if response.status_code != 200:
        logger.error(f"Request failed with status code: {response.status_code}")
        logger.error(f"Response text: {response.text[:500]}...")
        response.raise_for_status()
