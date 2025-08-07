"""Configuration module for Coemeta WebScraper.

This module provides centralized configuration management for the application,
including secure credential handling, environment variable loading, and
default settings. It supports configuration through environment variables
with sensible defaults.

Environment Variables:
    GOOGLE_SERVICE_ACCOUNT_PATH: Path to Google service account JSON file
    GOOGLE_SHEET_ID: ID of the Google Sheet for keywords and results
    MAX_RESULTS: Maximum number of results to scrape per keyword
    LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    DATA_DIR: Directory for storing data files
    SCRAPER_DELAY: Delay between scraping requests in seconds
    SCRAPER_USER_AGENT: Custom user agent string for scraping
    SCRAPER_MAX_RETRIES: Maximum number of retry attempts for scraping

Example:
    >>> from config import get_config
    >>> config = get_config()
    >>> sheet_id = config.SHEET_ID
    >>> max_results = config.MAX_RESULTS
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration container.

    This dataclass holds all configuration settings for the application,
    providing type hints and default values.

    Attributes:
        SERVICE_ACCOUNT_PATH: Path to Google service account JSON file
        SHEET_ID: ID of the Google Sheet for keywords and results
        MAX_RESULTS: Maximum number of results to scrape per keyword
        LOG_LEVEL: Logging level
        DATA_DIR: Directory for storing data files
        SCRAPER_DELAY: Delay between scraping requests in seconds
        SCRAPER_USER_AGENT: Custom user agent string for scraping
        SCRAPER_MAX_RETRIES: Maximum number of retry attempts for scraping
    """

    SERVICE_ACCOUNT_PATH: Optional[str] = None
    SHEET_ID: str = "1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo"
    MAX_RESULTS: int = 10
    LOG_LEVEL: str = "INFO"
    DATA_DIR: Path = Path("data")
    SCRAPER_DELAY: float = 1.0
    SCRAPER_USER_AGENT: Optional[str] = None
    SCRAPER_MAX_RETRIES: int = 3


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the application configuration.

    Loads configuration from environment variables with fallbacks to
    default values. Uses a singleton pattern to ensure configuration
    is only loaded once.

    Returns:
        AppConfig: Application configuration object with all settings.
    """
    global _config

    if _config is None:
        # Create new configuration with environment variable overrides
        _config = AppConfig(
            SERVICE_ACCOUNT_PATH=get_service_account_path(),
            SHEET_ID=os.getenv("GOOGLE_SHEET_ID", AppConfig.SHEET_ID),
            MAX_RESULTS=int(os.getenv("MAX_RESULTS", str(AppConfig.MAX_RESULTS))),
            LOG_LEVEL=os.getenv("LOG_LEVEL", AppConfig.LOG_LEVEL),
            DATA_DIR=Path(os.getenv("DATA_DIR", str(AppConfig.DATA_DIR))),
            SCRAPER_DELAY=float(
                os.getenv("SCRAPER_DELAY", str(AppConfig.SCRAPER_DELAY))
            ),
            SCRAPER_USER_AGENT=os.getenv("SCRAPER_USER_AGENT"),
            SCRAPER_MAX_RETRIES=int(
                os.getenv("SCRAPER_MAX_RETRIES", str(AppConfig.SCRAPER_MAX_RETRIES))
            ),
        )

        # Create data directory if it doesn't exist
        if not _config.DATA_DIR.exists():
            _config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    return _config


def get_service_account_path() -> Optional[str]:
    """Get the service account JSON file path.

    Attempts to find the service account credentials file from:
    1. GOOGLE_SERVICE_ACCOUNT_PATH environment variable
    2. Default location in the project root (service_account.json)

    Returns:
        Optional[str]: Path to the service account credentials file,
            or None if not found.
    """
    # First try environment variable
    env_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # Fallback to default location
    default_path = "service_account.json"
    if os.path.exists(default_path):
        return default_path

    # If neither exists, return None
    return None


def get_sheet_id() -> str:
    """Get the Google Sheet ID.

    Retrieves the Google Sheet ID from the environment variable
    or returns the default value.

    Returns:
        str: The Google Sheet ID for keywords and results.
    """
    return get_config().SHEET_ID


def validate_credentials() -> bool:
    """Validate service account credentials.

    Checks if the service account credentials file exists and is accessible.
    Provides informative error messages if validation fails.

    Returns:
        bool: True if credentials are valid, False otherwise.
    """
    service_account_path = get_service_account_path()
    if not service_account_path:
        print("❌ No service account credentials found!")
        print("Please set GOOGLE_SERVICE_ACCOUNT_PATH environment variable")
        print("or place your service account JSON file as 'service_account.json'")
        return False

    if not os.path.exists(service_account_path):
        print(f"❌ Service account file not found: {service_account_path}")
        return False

    print(f"✅ Service account credentials found: {service_account_path}")
    return True


def get_log_level() -> int:
    """Get the logging level.

    Converts the string log level from configuration to the
    corresponding logging module constant.

    Returns:
        int: Logging level constant from the logging module.
    """
    level_name = get_config().LOG_LEVEL.upper()
    return getattr(logging, level_name, logging.INFO)


# Configuration constants for backward compatibility
DEFAULT_MAX_RESULTS = AppConfig.MAX_RESULTS
DEFAULT_SHEET_ID = AppConfig.SHEET_ID
