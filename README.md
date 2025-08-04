# Coemeta WebScraper

## Overview

**Coemeta WebScraper** is a Python project designed to automate the process of scraping auction results from [shopgoodwill.com](https://shopgoodwill.com) based on a list of keywords, and then write the results to a Google Sheet. The project uses Selenium for robust web scraping, BeautifulSoup for HTML parsing, and the `gspread` library for Google Sheets integration. It is modular, testable, and includes utility functions for data cleaning, logging, and formatting.

The project now includes a **Streamlit web interface** for easy interaction and a **consolidated setup script** for seamless configuration.

---

## Project Structure

- `main.py`  
  The main entry point. Orchestrates the workflow: authenticates with Google Sheets, reads keywords, scrapes auction results, and writes results back to the sheet. Also includes test functions for each module and a full pipeline test.

- `streamlit_app.py`  
  **NEW**: Web interface built with Streamlit. Provides a user-friendly way to interact with all scraper functionality through a modern web UI.

- `setup.py`  
  **NEW**: Consolidated setup script that combines credential management, dependency checking, and comprehensive setup guidance.

- `scraper.py`  
  Contains the core scraping logic using Selenium and BeautifulSoup. Handles dynamic content, anti-bot measures, and flexible product extraction.

- `google_sheets.py`  
  Handles authentication with Google Sheets, reading keywords from a sheet, and writing results to a results tab.

- `utils.py`  
  Provides utility functions for logging, data cleaning, keyword sanitization, price extraction, date formatting, and more.

- `config.py`  
  Configuration management for service account paths and other settings.

---

## Quick Start

### 1. Initial Setup

Run the consolidated setup script to configure everything:

```bash
python setup.py
```

This script will:

- ✅ Check if all dependencies are installed
- 🔐 Guide you through Google Cloud credentials setup
- 🧪 Test your credentials
- 📋 Provide comprehensive setup instructions

### 2. Install Dependencies

If any dependencies are missing:

```bash
pip install -r requirements.txt
```

### 3. Run the Web Interface

```bash
streamlit run streamlit_app.py
```

Open your browser to the URL shown (usually `http://localhost:8501`)

---

## Usage

### Web Interface (Recommended)

The Streamlit interface provides:

- **🔍 Single Search**: Search for individual keywords and view results
- **📋 Batch Processing**: Process multiple keywords from Google Sheets or manual input
- **📊 Results Viewer**: View, filter, and analyze scraped results
- **🛠️ Utilities**: Test utility functions like text cleaning and data validation

### Command Line Interface

For automated processing:

```bash
python main.py
```

---

## Features

### 🔍 **Web Scraping**

- Robust scraping using Selenium with anti-bot measures
- Dynamic content handling
- Flexible product extraction
- Error handling and retry logic

### 📊 **Data Management**

- Google Sheets integration
- CSV export functionality
- Data validation and cleaning
- Comprehensive logging

### 🎨 **User Interface**

- Modern Streamlit web interface
- Real-time progress tracking
- Interactive data tables
- Download capabilities

### 🔐 **Security**

- Secure credential management
- Environment variable support
- .gitignore protection for sensitive files

---

## Configuration

### Google Cloud Setup

1. **Create a Google Cloud Project**
2. **Enable Google Sheets API**
3. **Create a Service Account**
4. **Download JSON credentials**
5. **Run `python setup.py`** to configure

The setup script will guide you through each step with detailed instructions.

### Environment Variables

You can set credentials via environment variable:

```bash
export GOOGLE_SERVICE_ACCOUNT_PATH="/path/to/your/service_account.json"
```

Or use the local file method (easier for development).

---

## File & Method Descriptions

### `setup.py`

- **main()**  
  Main setup function that orchestrates the entire setup process.

- **check_dependencies()**  
  Verifies all required packages are installed.

- **setup_credentials()**  
  Handles Google Cloud credentials setup with multiple options.

- **test_credentials()**  
  Tests authentication with Google Sheets.

- **auto_detect_credentials()**  
  Automatically finds and configures downloaded credential files.

### `streamlit_app.py`

- **main()**  
  Main Streamlit application with tabbed interface.

- **initialize_session_state()**  
  Sets up session state for data persistence.

- **log_message()**  
  Adds messages to the activity log.

### `main.py`

- **main()**  
  Main execution function for command-line operation.

- **test\_\*()**  
  Various test functions for each module.

### `scraper.py`

- **scrape_auction_results(keyword: str, max_results: int = 10) -> list**  
  Scrapes auction results from shopgoodwill.com for a given keyword.

### `google_sheets.py`

- **get_gspread_client(service_account_path: str)**  
  Authenticates with Google Sheets using a service account JSON file.

- **read_keywords(sheet_id: str, client)**  
  Reads keywords from the `[KEYWORDS]` tab of the specified Google Sheet.

- **write_results(sheet_id: str, keyword: str, results: list, client)**  
  Writes search results to the `RESULTS TEMPLATE` tab of the specified Google Sheet.

### `utils.py`

- **setup_logging(level: str = "INFO")**  
  Sets up and returns a logger with the specified log level.

- **sanitize_keyword(keyword: str) -> str**  
  Cleans and normalizes a keyword for searching.

- **clean_text(text: str) -> str**  
  Cleans and normalizes arbitrary text content.

- **extract_price(price_text: str) -> float**  
  Extracts a numeric price from a string.

- **format_date(date_text: str) -> str**  
  Formats a date string to a consistent format.

---

## What the Project Does

1. **Authenticates** with Google Sheets using a service account.
2. **Reads** a list of keywords from a Google Sheet.
3. **Scrapes** auction results for each keyword from shopgoodwill.com, handling dynamic content and anti-bot measures.
4. **Cleans and validates** the scraped data.
5. **Writes** the results back to a designated tab in the Google Sheet.
6. **Logs** progress and errors for transparency and debugging.
7. **Provides** a web interface for easy interaction and data visualization.

---

## Troubleshooting

### Common Issues

1. **"No credentials found"**

   - Run `python setup.py` to configure credentials

2. **"Authentication failed"**

   - Check your Google Cloud project settings
   - Ensure Google Sheets API is enabled
   - Verify service account has proper permissions

3. **"Missing dependencies"**

   - Run `pip install -r requirements.txt`

4. **"Web scraping blocked"**
   - The scraper includes anti-bot measures
   - Try again later or adjust scraping parameters

### Getting Help

- Check the activity logs in the Streamlit interface
- Review the console output for detailed error messages
- Ensure all setup steps were completed correctly

---

## Security Notes

- ✅ Service account JSON files are protected by .gitignore
- ✅ Environment variables are supported for production use
- ✅ No hardcoded credentials in the codebase
- ⚠️ Keep your service account credentials secure
- ⚠️ Never commit credentials to version control

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
