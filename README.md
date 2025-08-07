# Coemeta WebScraper

A robust web scraping solution with advanced anti-detection capabilities for auction websites.

## Project Structure

The project is now organized into backend and frontend modules:

### Backend

The `backend` folder contains all the core scraping functionality:

- `main.py`: Core orchestration and command-line interface
- `scraper.py`: Advanced web scraping with anti-detection capabilities
- `google_sheets.py`: Integration with Google Sheets for keywords and results
- `utils.py`: Utility functions for data processing
- `config.py`: Configuration management
- `error_handling.py`: Centralized error handling
- `database/`: Database operations and management

### Frontend

The `frontend` folder contains the web interface:

- `streamlit_app.py`: Streamlit web application for user interaction

## Setup & Running the Application

### One-time Setup

To set up the virtual environment and install dependencies:

```
python backend/setup.py
```

### Running the Application

You can run the application directly with:

- **Command Line Interface**: `python main.py`
- **Web Interface**: `python streamlit_app.py`

These scripts will automatically ensure the virtual environment is set up and activated.

### Advanced Usage

You can also run components directly (requires manual venv activation):

```
# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows

# Then run the components directly
python backend/main.py    # Backend CLI
python -m streamlit run frontend/streamlit_app.py  # Frontend
```

## Commands

- `python main.py`: Run the web scraper
- `python main.py setup`: Set up the environment
- `python main.py streamlit`: Launch the web interface
- `python main.py test`: Run tests
- `python main.py help`: Show available commands
