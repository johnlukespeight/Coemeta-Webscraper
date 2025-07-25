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
    pass


def write_results(sheet_id: str, keyword: str, results: list, client):
    """
    Write search results to a tab named after the keyword in the specified Google Sheet.
    If the tab does not exist, it will be created. If it exists, it will be cleared and overwritten.
    Args:
        sheet_id (str): The ID of the Google Sheet.
        keyword (str): The keyword (used as the tab name).
        results (list): List of dictionaries, each representing a row to write (matching TEMPLATE columns).
        client (gspread.Client): Authenticated gspread client.
    Returns:
        None
    """
    pass
