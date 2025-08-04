import gspread


def get_gspread_client(service_account_path: str):
    """
    Authenticate with Google Sheets using the provided service account JSON file.
    Returns a gspread client instance.
    Args:
        service_account_path (str): Path to the service account JSON file.
    Returns:
        gspread.Client: Authenticated gspread client.
    """

    # Use the provided service_account_path parameter instead of hardcoded path
    # service_account_path = "/Users/nezamsp8/Developer/Coemeta WebScraper/spartan-rhino-434020-h1-a244eeb7b709.json"

    return gspread.service_account(filename=service_account_path)


def read_keywords(sheet_id: str, client):
    """
    Read keywords from the [KEYWORDS] tab of the specified Google Sheet.
    Args:
        sheet_id (str): The ID of the Google Sheet.
        client (gspread.Client): Authenticated gspread client.
    Returns:
        list: List of keywords as strings.
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


def write_results(sheet_id: str, keyword: str, results: list, client):
    """
    Write search results to the 'RESULTS TEMPLATE' tab of the specified Google Sheet.
    The worksheet will be cleared and overwritten with the new results.
    Args:
        sheet_id (str): The ID of the Google Sheet.
        keyword (str): The keyword (will be written in the first column of each row).
        results (list): List of dictionaries, each representing a row to write.
        client (gspread.Client): Authenticated gspread client.
    Returns:
        None
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
