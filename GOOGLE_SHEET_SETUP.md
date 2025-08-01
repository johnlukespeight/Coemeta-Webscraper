# Google Sheet Setup Guide

## 📊 Setting up your Google Sheet

The Coemeta WebScraper uses Google Sheets to store keywords and results. Here's how to set it up:

### Step 1: Create a Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it something like "Coemeta WebScraper"

### Step 2: Set up the Keywords Tab

1. **Rename the first sheet** to `[KEYWORDS]`
2. **Add keywords** in column A, one per row:

```
A1: Keywords
A2: vintage watch
A3: antique jewelry
A4: gore-tex jacket
A5: collectible coins
```

### Step 3: Set up the Results Template Tab

1. **Create a new sheet** and name it `RESULTS TEMPLATE`
2. **Add these headers** in row 1:

```
A1: Keyword
B1: Item Description
C1: Auction end date
D1: Current price
E1: Auction image / thumbnail URL (extra credit)
```

### Step 4: Share the Sheet with your Service Account

1. **Get your service account email** from the JSON file:

   - Open your `service_account.json` file
   - Look for the `client_email` field
   - It will look like: `coemeta-scraper@your-project.iam.gserviceaccount.com`

2. **Share the Google Sheet**:
   - Click the "Share" button in the top right
   - Add your service account email as an Editor
   - Make sure to give it "Editor" permissions

### Step 5: Get the Sheet ID

1. **Copy the Sheet ID** from the URL:

   - Your URL will look like: `https://docs.google.com/spreadsheets/d/1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo/edit`
   - The Sheet ID is: `1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo`

2. **Update the configuration**:
   - The default Sheet ID in the code is already set to the example above
   - You can change it by setting the `GOOGLE_SHEET_ID` environment variable
   - Or update the default in `config.py`

### Step 6: Test the Setup

Run the setup script to test your configuration:

```bash
python setup_google_credentials.py
```

Or run the comprehensive verification script:

```bash
python tests/verify_setup.py
```

## 🔧 Configuration Options

### Environment Variables

You can set these environment variables instead of using the default files:

```bash
export GOOGLE_SERVICE_ACCOUNT_PATH="/path/to/your/service_account.json"
export GOOGLE_SHEET_ID="your-sheet-id-here"
```

### Default Configuration

- **Service Account**: `service_account.json` (in project root)
- **Sheet ID**: `1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo`

## 📋 Example Sheet Structure

### Keywords Tab (`[KEYWORDS]`)

```
| Keywords        |
|-----------------|
| vintage watch   |
| antique jewelry |
| gore-tex jacket |
| collectible coins|
```

### Results Template Tab (`RESULTS TEMPLATE`)

```
| Keyword | Item Description | Auction end date | Current price | Auction image / thumbnail URL (extra credit) |
|---------|------------------|------------------|---------------|-----------------------------------------------|
| vintage watch | Vintage Rolex Watch | Dec 15, 2024 | $1,250.00 | https://example.com/image1.jpg |
| antique jewelry | Antique Diamond Ring | Dec 16, 2024 | $2,500.00 | https://example.com/image2.jpg |
```

## 🚨 Important Notes

1. **Service Account Permissions**: Make sure your service account has Editor access to the Google Sheet
2. **API Quotas**: Google Sheets API has rate limits, so the scraper includes delays between requests
3. **Sheet Names**: The tab names must be exactly `[KEYWORDS]` and `RESULTS TEMPLATE`
4. **Data Format**: Results will overwrite existing data in the RESULTS TEMPLATE tab

## 🧪 Testing

After setup, you can test the Google Sheets integration:

```bash
# Test Google Sheets functionality
python -m unittest tests.integration.test_google_sheets_integration

# Test the full pipeline
python -m unittest tests.integration.test_full_pipeline_integration
```
