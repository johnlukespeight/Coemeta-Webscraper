"""Error handling module for Coemeta WebScraper.

This module provides standardized error handling functionality for the
application, including custom exceptions, error logging, and error
formatting utilities.

Example:
    >>> from error_handling import handle_error, ScraperError
    >>> try:
    ...     # Some code that might raise an exception
    ...     result = some_function()
    ... except Exception as e:
    ...     handle_error(e, "Failed to execute some_function", logger)
"""

import logging
import traceback
import sys
from typing import Optional, Type, Any, Dict, List, Union, Callable
import requests


class ScraperError(Exception):
    """Base exception class for scraper-related errors.

    This is the base class for all custom exceptions in the application.
    It provides additional context about the error and standardized
    formatting.

    Attributes:
        message: Human-readable error message
        details: Additional error details
        original_exception: The original exception that caused this error
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ) -> None:
        """Initialize a ScraperError.

        Args:
            message: Human-readable error message
            details: Additional error details as a dictionary
            original_exception: The original exception that caused this error
        """
        self.message = message
        self.details = details or {}
        self.original_exception = original_exception

        # Format the error message
        formatted_message = self.message
        if self.details:
            formatted_message += f" - Details: {self.details}"
        if self.original_exception:
            formatted_message += f" - Original error: {str(self.original_exception)}"

        super().__init__(formatted_message)


class ConfigurationError(ScraperError):
    """Exception raised for configuration-related errors."""

    pass


class NetworkError(ScraperError):
    """Exception raised for network-related errors."""

    pass


class ScrapingError(ScraperError):
    """Exception raised for scraping-related errors."""

    pass


class DataError(ScraperError):
    """Exception raised for data-related errors."""

    pass


class GoogleSheetsError(ScraperError):
    """Exception raised for Google Sheets-related errors."""

    pass


def handle_error(
    error: Exception,
    context: str,
    logger: Optional[logging.Logger] = None,
    reraise: bool = True,
    error_type: Type[Exception] = ScraperError,
) -> None:
    """Handle an exception with standardized logging and formatting.

    This function provides a consistent way to handle exceptions throughout
    the application. It logs the error with appropriate context and
    optionally reraises it as a custom exception type.

    Args:
        error: The exception to handle
        context: A description of what was happening when the error occurred
        logger: Logger to use for logging the error
        reraise: Whether to reraise the exception after handling
        error_type: The type of exception to raise if reraise is True

    Raises:
        The specified error_type if reraise is True
    """
    # Get error details
    error_message = str(error)
    error_traceback = traceback.format_exc()

    # Create error details
    details = {
        "context": context,
        "error_type": error.__class__.__name__,
        "traceback": error_traceback,
    }

    # Log the error
    if logger:
        logger.error(f"{context}: {error_message}")
        logger.debug(f"Error details: {details}")
    else:
        print(f"ERROR: {context}: {error_message}", file=sys.stderr)

    # Reraise as custom exception if requested
    if reraise:
        if isinstance(error, error_type):
            raise error
        else:
            raise error_type(context, details=details, original_exception=error)


def handle_request_error(
    response: requests.Response,
    context: str,
    logger: Optional[logging.Logger] = None,
    reraise: bool = True,
) -> None:
    """Handle HTTP response errors with standardized logging and formatting.

    This function provides a consistent way to handle HTTP response errors
    throughout the application. It logs the error with appropriate context
    and optionally raises a NetworkError.

    Args:
        response: The HTTP response to check for errors
        context: A description of what was happening when the error occurred
        logger: Logger to use for logging the error
        reraise: Whether to raise a NetworkError if the response indicates an error

    Raises:
        NetworkError: If the response status code indicates an error and reraise is True
    """
    if response.status_code >= 400:
        # Create error details
        details = {
            "context": context,
            "status_code": response.status_code,
            "url": response.url,
            "response_text": response.text[:500],  # First 500 characters of response
        }

        # Create error message
        error_message = f"HTTP error {response.status_code} for {response.url}"

        # Log the error
        if logger:
            logger.error(error_message)
            logger.debug(f"Error details: {details}")
        else:
            print(f"ERROR: {error_message}", file=sys.stderr)

        # Raise a NetworkError if requested
        if reraise:
            raise NetworkError(error_message, details=details)


def safe_execute(
    func: Callable,
    *args: Any,
    error_message: str = "Function execution failed",
    logger: Optional[logging.Logger] = None,
    default_return: Any = None,
    **kwargs: Any,
) -> Any:
    """Execute a function safely with error handling.

    This function provides a convenient way to execute a function with
    standardized error handling. If the function raises an exception,
    it is handled according to the specified parameters.

    Args:
        func: The function to execute
        *args: Positional arguments to pass to the function
        error_message: A description of what was happening when the error occurred
        logger: Logger to use for logging any error
        default_return: Value to return if the function raises an exception
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The return value of the function, or default_return if an exception occurs
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, error_message, logger, reraise=False)
        return default_return
