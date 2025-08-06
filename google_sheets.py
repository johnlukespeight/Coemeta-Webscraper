"""Google Sheets integration module for Coemeta WebScraper.

This module provides functionality to interact with Google Sheets,
including authentication, reading keywords, and writing scraping results.
It uses the gspread library to handle Google Sheets API operations.

The module implements three main functions:
1. Authentication with Google Sheets API using service account credentials
2. Reading keywords from a specified worksheet in a Google Sheet
3. Writing scraping results to a specified worksheet in a Google Sheet

Example:
    >>> from google_sheets import get_gspread_client, read_keywords, write_results
    >>> client = get_gspread_client("service_account.json")
    >>> keywords = read_keywords("sheet_id", client)
    >>> results = [{"Item Description": "Item 1", "Current price": "$10.00"}]
    >>> write_results("sheet_id", "keyword", results, client)
"""

from typing import List, Dict, Any, Optional
import gspread
from gspread.client import Client
from gspread.models import Worksheet


def get_gspread_client(service_account_path: str) -> Client:
    """Authenticate with Google Sheets using a service account JSON file.

    Creates and returns an authenticated gspread client instance using
    the provided service account credentials file. This client can be
    used for all subsequent Google Sheets operations.

    Args:
        service_account_path: Path to the service account JSON file.
            This file should contain valid Google service account credentials
            with appropriate permissions for Google Sheets access.

    Returns:
        Client: Authenticated gspread client instance ready for use
            with Google Sheets API operations.

    Raises:
        FileNotFoundError: If the service account file doesn't exist.
        gspread.exceptions.GSpreadException: If authentication fails.
    """
    return gspread.service_account(filename=service_account_path)


def read_keywords(sheet_id: str, client: Client) -> List[str]:
    """Read keywords from the [KEYWORDS] tab of the specified Google Sheet.

    Retrieves a list of keywords from the first column of the [KEYWORDS]
    worksheet in the specified Google Sheet. The function handles common
    formatting issues such as headers and empty strings.

    Args:
        sheet_id: The ID of the Google Sheet to read from.
            This is the unique identifier in the Google Sheets URL.
        client: Authenticated gspread client instance.
            Should be obtained from get_gspread_client().

    Returns:
        List[str]: List of keywords as strings, with empty strings and
            headers removed.

    Raises:
        gspread.exceptions.WorksheetNotFound: If the [KEYWORDS] worksheet
            doesn't exist in the specified sheet.
        gspread.exceptions.SpreadsheetNotFound: If the sheet_id is invalid.
    """
    # Open the Google Sheet by ID
    sheet = client.open_by_key(sheet_id)

    # Open the [KEYWORDS] worksheet/tab
    worksheet = sheet.worksheet("[KEYWORDS]")

    # Get all values in the first column (assume keywords are in column A)
    keywords = worksheet.col_values(1)

    # Optionally, remove header if present
    if keywords and keywords[0].strip().lower() == "keyword":
        keywords = keywords[1:]

    # Remove empty strings
    keywords = [kw for kw in keywords if kw.strip()]

    return keywords


def write_results(
    sheet_id: str, keyword: str, results: List[Dict[str, str]], client: Client
) -> None:
    """Write search results to the 'RESULTS TEMPLATE' tab of the specified Google Sheet.

    Creates or clears the 'RESULTS TEMPLATE' worksheet in the specified Google Sheet
    and writes the search results to it. The function also attempts to render
    image URLs as actual images in the spreadsheet.

    The worksheet will be structured with the following columns:
    - Keyword: The search keyword used
    - Item Description: Description of the auction item
    - Auction end date: End date of the auction
    - Current price: Current price of the item
    - Auction image / thumbnail URL: URL of the item image (rendered as image)

    Args:
        sheet_id: The ID of the Google Sheet to write to.
            This is the unique identifier in the Google Sheets URL.
        keyword: The search keyword used to find these results.
            Will be written in the first column of each row.
        results: List of dictionaries, each representing a result to write.
            Each dictionary should contain keys matching the column names.
        client: Authenticated gspread client instance.
            Should be obtained from get_gspread_client().

    Returns:
        None

    Raises:
        gspread.exceptions.SpreadsheetNotFound: If the sheet_id is invalid.
        gspread.exceptions.APIError: If there's an error with the Google Sheets API.
    """
    # Define the required columns
    columns = [
        "Keyword",
        "Item Description",
        "Auction end date",
        "Current price",
        "Auction image / thumbnail URL (extra credit)",
    ]

    # Open the Google Sheet by ID
    sheet = client.open_by_key(sheet_id)

    # Try to open the 'RESULTS TEMPLATE' worksheet, or create it if it doesn't exist
    try:
        worksheet = sheet.worksheet("RESULTS TEMPLATE")
        worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(
            title="RESULTS TEMPLATE", rows="100", cols=str(len(columns))
        )

    # Prepare the data: first row is headers, then each row is a list of values
    data = [columns]
    for row in results:
        # Ensure the 'Keyword' column is filled with the provided keyword
        row_data = [
            keyword,
            row.get("Item Description", ""),
            row.get("Auction end date", ""),
            row.get("Current price", ""),
            row.get("Auction image / thumbnail URL (extra credit)", ""),
        ]
        data.append(row_data)

    # Write the data to the worksheet starting at A1
    worksheet.update("A1", data)

    # Add images to column E (5th column) if image URLs are available
    try:
        for i, row in enumerate(results, start=2):  # Start from row 2 (after headers)
            image_url = row.get("Auction image / thumbnail URL (extra credit)", "")
            if image_url and image_url.strip():
                try:
                    # Insert image using cell update method
                    worksheet.update_cell(i, 5, f'=IMAGE("{image_url}", 3, 100, 100)')
                    print(f"✅ Added image to row {i}, column E: {image_url}")
                except Exception as e:
                    print(f"⚠️ Could not add image to row {i}, column E: {e}")
                    # Fallback: just put the URL as text
                    worksheet.update_cell(i, 5, image_url)
    except Exception as e:
        print(f"⚠️ Error adding images to sheet: {e}")
