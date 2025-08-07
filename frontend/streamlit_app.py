"""Streamlit web application for the Coemeta WebScraper.

This module provides a modern, interactive web interface for the auction data scraper.
It allows users to perform single keyword searches or batch processing, view and analyze
results, interact with the database, and use various utility functions.

The UI is designed with a modern, responsive layout featuring glassmorphism effects,
gradient backgrounds, and animated components.

Features:
    - Single keyword search with real-time feedback
    - Batch processing from Google Sheets or manual input
    - Results viewer with filtering capabilities
    - Database analytics dashboard
    - Utility tools for testing data processing functions
    - Real-time statistics and logging

Typical usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os
from typing import Dict, List, Optional, Any, Union, Tuple

from backend.google_sheets import get_gspread_client, write_results, read_keywords
from backend.scraper import scrape_auction_results
from backend.database.database import get_database, close_database
from backend.utils import (
    setup_logging,
    sanitize_keyword,
    clean_text,
    log_scraping_stats,
    validate_auction_data,
    extract_price,
    format_date,
)
from backend.config import get_config
from backend.error_handling import (
    handle_error,
    GoogleSheetsError,
    ScrapingError,
    DataError,
)

# Page configuration
st.set_page_config(
    page_title="Coemeta WebScraper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enhanced Custom CSS for modern styling
st.markdown(
    """
<style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Card Styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }
    
    /* Status Messages */
    .success-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
        margin: 1rem 0;
    }
    
    .warning-message {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        margin: 1rem 0;
    }
    
    .info-message {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
        margin: 1rem 0;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Input Styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Slider Styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Custom Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .main-header p {
            font-size: 1rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state() -> None:
    """Initialize session state variables for the application.

    This function sets up the initial state for the Streamlit application,
    creating the necessary session state variables if they don't already exist.

    Session state variables:
        - results_data: List of dictionaries containing scraped auction results
        - processing_status: Current processing status (idle, searching, batch_processing)
        - logs: List of log messages with timestamps
        - stats: Dictionary containing statistics about searches and results

    Returns:
        None
    """
    if "results_data" not in st.session_state:
        st.session_state.results_data = []
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = "idle"
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "total_searches": 0,
            "total_results": 0,
            "successful_searches": 0,
            "failed_searches": 0,
        }


def log_message(message: str, level: str = "INFO") -> None:
    """Add a message to the application logs with timestamp.

    This function appends a formatted log message to the session state logs
    with a timestamp and specified log level.

    Args:
        message: The message text to log
        level: Log level (INFO, WARNING, ERROR, SUCCESS)

    Returns:
        None

    Example:
        log_message("Search completed successfully", "SUCCESS")
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {level}: {message}")


def display_logs() -> None:
    """Display application logs in a scrollable container with appropriate styling.

    This function renders the most recent logs (up to 20) in an expandable container,
    styling each log entry according to its level (ERROR, WARNING, SUCCESS, INFO).

    Returns:
        None
    """
    if st.session_state.logs:
        with st.expander("📋 Activity Logs", expanded=False):
            log_container = st.container()
            with log_container:
                for log in st.session_state.logs[-20:]:  # Show last 20 logs
                    if "ERROR" in log:
                        st.error(log)
                    elif "WARNING" in log:
                        st.warning(log)
                    elif "SUCCESS" in log:
                        st.success(log)
                    else:
                        st.info(log)


def display_stats() -> None:
    """Display application statistics in a beautiful card layout.

    This function renders key statistics from the session state in a row of
    metric cards with custom styling. Each card shows a different statistic
    with an appropriate icon and color scheme.

    Statistics displayed:
        - Total searches performed
        - Total results found across all searches
        - Number of successful searches
        - Number of failed searches

    Returns:
        None
    """
    stats = st.session_state.stats

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #667eea;">🔍</h3>
                <h2 style="margin: 0.5rem 0; color: #333;">{stats['total_searches']}</h2>
                <p style="margin: 0; color: #666;">Total Searches</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #4CAF50;">📊</h3>
                <h2 style="margin: 0.5rem 0; color: #333;">{stats['total_results']}</h2>
                <p style="margin: 0; color: #666;">Total Results</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #2196F3;">✅</h3>
                <h2 style="margin: 0.5rem 0; color: #333;">{stats['successful_searches']}</h2>
                <p style="margin: 0; color: #666;">Successful</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #f44336;">❌</h3>
                <h2 style="margin: 0.5rem 0; color: #333;">{stats['failed_searches']}</h2>
                <p style="margin: 0; color: #666;">Failed</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def create_search_card(
    keyword: str, results_count: int, avg_price: Optional[float] = None
) -> str:
    """Create a beautiful HTML card for displaying search result summaries.

    This function generates HTML for a styled card that displays information
    about a search result, including the keyword, number of results found,
    and optionally the average price.

    Args:
        keyword: The search keyword
        results_count: Number of results found for this keyword
        avg_price: Optional average price of results, if available

    Returns:
        str: HTML string for the search result card

    Example:
        card_html = create_search_card("vintage watch", 15, 125.50)
        st.markdown(card_html, unsafe_allow_html=True)
    """
    card_html = f"""
    <div class="metric-card" style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; color: #333;">🔍 {keyword}</h3>
                <p style="margin: 0.5rem 0; color: #666;">Found {results_count} results</p>
            </div>
            <div style="text-align: right;">
                <h4 style="margin: 0; color: #4CAF50;">{results_count}</h4>
                <p style="margin: 0; color: #666;">items</p>
            </div>
        </div>
    """

    if avg_price:
        card_html += f"""
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee;">
            <p style="margin: 0; color: #666;">Average Price: <strong style="color: #4CAF50;">${avg_price:.2f}</strong></p>
        </div>
        """

    card_html += "</div>"
    return card_html


def main() -> None:
    """Main function for the Streamlit application.

    This function sets up the application layout, initializes the session state,
    and renders all UI components including the header, sidebar, tabs, and
    interactive elements.

    The application is organized into tabs:
        - Single Search: For searching individual keywords
        - Batch Processing: For processing multiple keywords
        - Results Viewer: For viewing and filtering results
        - Database Analytics: For analyzing stored data
        - Utilities: For testing data processing functions

    Returns:
        None
    """
    # Enhanced header with gradient background
    st.markdown(
        """
        <div class="main-header fade-in-up">
            <h1>🔍 Coemeta WebScraper</h1>
            <p>Advanced Auction Data Collection & Analysis Tool</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    initialize_session_state()

    # Enhanced sidebar with better styling
    with st.sidebar:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 1rem; border-radius: 15px; margin-bottom: 2rem;">
                <h3 style="margin: 0; text-align: center;">⚙️ Configuration</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Google Sheets configuration
        st.subheader("📊 Google Sheets")
        sheet_id = st.text_input(
            "Sheet ID",
            value="1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo",
            help="The Google Sheet ID where keywords are stored and results will be written",
        )

        service_account_path = st.text_input(
            "Service Account JSON Path",
            value="service_account.json",
            help="Path to your Google Service Account JSON file",
        )

        # Enhanced scraping configuration
        st.subheader("🔧 Scraping Settings")
        max_results = st.slider(
            "Max Results per Keyword",
            min_value=1,
            max_value=50,
            value=10,
            help="Maximum number of results to scrape per keyword",
        )

        # Test connection button with enhanced styling
        if st.button("🔗 Test Connection", use_container_width=True):
            with st.spinner("Testing connection..."):
                try:
                    client = get_gspread_client(service_account_path)
                    keywords = read_keywords(sheet_id, client)
                    st.markdown(
                        f"""
                        <div class="success-message">
                            <h4 style="margin: 0;">✅ Connection Successful!</h4>
                            <p style="margin: 0.5rem 0 0 0;">Found {len(keywords)} keywords in the sheet</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    log_message(
                        f"Successfully connected to Google Sheets. Found {len(keywords)} keywords"
                    )
                except Exception as e:
                    st.markdown(
                        f"""
                        <div class="error-message">
                            <h4 style="margin: 0;">❌ Connection Failed</h4>
                            <p style="margin: 0.5rem 0 0 0;">{str(e)}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    log_message(f"Google Sheets connection failed: {str(e)}", "ERROR")

    # Display statistics
    display_stats()

    # Enhanced tabs with better styling
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🔍 Single Search",
            "📋 Batch Processing",
            "📊 Results Viewer",
            "🦆 Database Analytics",
            "🛠️ Utilities",
        ]
    )

    with tab1:
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 15px; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                <h2 style="margin: 0 0 1rem 0; color: #333;">🔍 Single Keyword Search</h2>
                <p style="margin: 0; color: #666;">Search for auction items using a single keyword</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            keyword = st.text_input(
                "Enter keyword to search",
                placeholder="e.g., gore-tex, vintage watch, etc.",
                help="Enter a keyword to search for auction items",
            )

            if st.button(
                "🔍 Search",
                type="primary",
                disabled=not keyword,
                use_container_width=True,
            ):
                if keyword:
                    st.session_state.processing_status = "searching"
                    st.session_state.stats["total_searches"] += 1

                    with st.spinner(f"🔍 Searching for '{keyword}'..."):
                        try:
                            results = scrape_auction_results(keyword, max_results)

                            if results:
                                st.session_state.results_data = results
                                st.session_state.stats["total_results"] += len(results)
                                st.session_state.stats["successful_searches"] += 1

                                st.markdown(
                                    f"""
                                    <div class="success-message">
                                        <h4 style="margin: 0;">✅ Search Complete!</h4>
                                        <p style="margin: 0.5rem 0 0 0;">Found {len(results)} results for '{keyword}'</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                log_message(
                                    f"Found {len(results)} results for keyword: {keyword}"
                                )

                                # Write results to Google Sheets
                                try:
                                    client = get_gspread_client(service_account_path)
                                    write_results(sheet_id, keyword, results, client)
                                    st.success(
                                        f"📊 Written {len(results)} results to Google Sheets"
                                    )
                                    log_message(
                                        f"Written {len(results)} results to Google Sheets for keyword: {keyword}"
                                    )
                                except Exception as e:
                                    st.warning(
                                        f"⚠️ Could not write to Google Sheets: {str(e)}"
                                    )
                                    log_message(
                                        f"Google Sheets write failed for keyword {keyword}: {str(e)}",
                                        "WARNING",
                                    )

                                # Save to database
                                try:
                                    db = get_database()
                                    inserted_count = db.insert_auction_results(
                                        keyword, results
                                    )
                                    st.info(
                                        f"💾 Saved {inserted_count} results to database"
                                    )
                                    log_message(
                                        f"Saved {inserted_count} results to database for keyword: {keyword}"
                                    )
                                except Exception as e:
                                    st.warning(
                                        f"⚠️ Could not save to database: {str(e)}"
                                    )
                                    log_message(
                                        f"Database save failed for keyword {keyword}: {str(e)}",
                                        "WARNING",
                                    )

                                # Display results in a beautiful table
                                df = pd.DataFrame(results)
                                st.markdown("### 📊 Search Results")
                                st.dataframe(df, use_container_width=True)

                                # Action buttons
                                col1, col2 = st.columns(2)

                                with col1:
                                    # Enhanced download button
                                    csv = df.to_csv(index=False)
                                    st.download_button(
                                        label="📥 Download Results as CSV",
                                        data=csv,
                                        file_name=f"auction_results_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv",
                                        use_container_width=True,
                                    )

                                with col2:
                                    # Manual write to sheets button
                                    if st.button(
                                        "📊 Write to Google Sheets",
                                        use_container_width=True,
                                    ):
                                        try:
                                            client = get_gspread_client(
                                                service_account_path
                                            )
                                            write_results(
                                                sheet_id, keyword, results, client
                                            )
                                            st.success(
                                                f"✅ Written {len(results)} results to Google Sheets"
                                            )
                                            log_message(
                                                f"Manually written {len(results)} results to Google Sheets for keyword: {keyword}"
                                            )
                                        except Exception as e:
                                            st.error(
                                                f"❌ Failed to write to Google Sheets: {str(e)}"
                                            )
                                            log_message(
                                                f"Manual Google Sheets write failed for keyword {keyword}: {str(e)}",
                                                "ERROR",
                                            )
                            else:
                                st.session_state.stats["failed_searches"] += 1
                                st.markdown(
                                    f"""
                                    <div class="warning-message">
                                        <h4 style="margin: 0;">⚠️ No Results Found</h4>
                                        <p style="margin: 0.5rem 0 0 0;">No results found for '{keyword}'</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                log_message(
                                    f"No results found for keyword: {keyword}",
                                    "WARNING",
                                )

                        except Exception as e:
                            st.session_state.stats["failed_searches"] += 1
                            st.markdown(
                                f"""
                                <div class="error-message">
                                    <h4 style="margin: 0;">❌ Search Failed</h4>
                                    <p style="margin: 0.5rem 0 0 0;">{str(e)}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            log_message(
                                f"Search failed for keyword {keyword}: {str(e)}",
                                "ERROR",
                            )

                    st.session_state.processing_status = "idle"

        with col2:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; 
                            box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                    <h3 style="margin: 0 0 1rem 0; color: #333;">📈 Quick Stats</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.session_state.results_data:
                st.metric("Total Results", len(st.session_state.results_data))

                # Calculate average price if available
                prices = []
                for result in st.session_state.results_data:
                    price = result.get("Current price", "")
                    if price and price != "N/A":
                        try:
                            numeric_price = extract_price(price)
                            if numeric_price:
                                prices.append(numeric_price)
                        except:
                            pass

                if prices:
                    avg_price = sum(prices) / len(prices)
                    st.metric("Average Price", f"${avg_price:.2f}")
                    st.metric("Price Range", f"${min(prices):.2f} - ${max(prices):.2f}")

    with tab2:
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 15px; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                <h2 style="margin: 0 0 1rem 0; color: #333;">📋 Batch Processing</h2>
                <p style="margin: 0; color: #666;">Process multiple keywords from Google Sheets or manual input</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; 
                            box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                    <h3 style="margin: 0 0 1rem 0; color: #333;">📊 From Google Sheets</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "📋 Process All Keywords", type="primary", use_container_width=True
            ):
                st.session_state.processing_status = "batch_processing"

                try:
                    client = get_gspread_client(service_account_path)
                    keywords = read_keywords(sheet_id, client)

                    if not keywords:
                        st.markdown(
                            """
                            <div class="warning-message">
                                <h4 style="margin: 0;">⚠️ No Keywords Found</h4>
                                <p style="margin: 0.5rem 0 0 0;">No keywords found in the sheet!</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        return

                    st.markdown(
                        f"""
                        <div class="info-message">
                            <h4 style="margin: 0;">📋 Processing Started</h4>
                            <p style="margin: 0.5rem 0 0 0;">Processing {len(keywords)} keywords...</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Enhanced progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    results_container = st.container()

                    total_results = 0
                    successful_keywords = 0
                    search_cards = []

                    for i, keyword in enumerate(keywords):
                        status_text.text(f"🔍 Processing: {keyword}")

                        try:
                            results = scrape_auction_results(keyword, max_results)

                            if results:
                                write_results(sheet_id, keyword, results, client)
                                total_results += len(results)
                                successful_keywords += 1
                                st.session_state.stats["total_results"] += len(results)
                                st.session_state.stats["successful_searches"] += 1

                                # Calculate average price for this keyword
                                prices = []
                                for result in results:
                                    price = result.get("Current price", "")
                                    if price and price != "N/A":
                                        try:
                                            numeric_price = extract_price(price)
                                            if numeric_price:
                                                prices.append(numeric_price)
                                        except:
                                            pass

                                avg_price = (
                                    sum(prices) / len(prices) if prices else None
                                )
                                search_cards.append(
                                    create_search_card(keyword, len(results), avg_price)
                                )

                                # Save to database
                                try:
                                    db = get_database()
                                    inserted_count = db.insert_auction_results(
                                        keyword, results
                                    )
                                    log_message(
                                        f"Saved {inserted_count} results to database for keyword: {keyword}"
                                    )
                                except Exception as e:
                                    log_message(
                                        f"Database save failed for keyword {keyword}: {str(e)}",
                                        "WARNING",
                                    )

                                log_message(
                                    f"Processed keyword '{keyword}': {len(results)} results"
                                )
                            else:
                                st.session_state.stats["failed_searches"] += 1
                                log_message(
                                    f"No results for keyword '{keyword}'", "WARNING"
                                )

                        except Exception as e:
                            st.session_state.stats["failed_searches"] += 1
                            log_message(
                                f"Error processing keyword '{keyword}': {str(e)}",
                                "ERROR",
                            )

                        # Update progress
                        progress = (i + 1) / len(keywords)
                        progress_bar.progress(progress)
                        time.sleep(0.1)

                    progress_bar.empty()
                    status_text.empty()

                    # Display results summary
                    with results_container:
                        st.markdown(
                            f"""
                            <div class="success-message">
                                <h4 style="margin: 0;">✅ Batch Processing Complete!</h4>
                                <p style="margin: 0.5rem 0 0 0;">Successfully processed {successful_keywords} keywords with {total_results} total results</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Display search cards
                        if search_cards:
                            st.markdown("### 📊 Processing Summary")
                            for card in search_cards:
                                st.markdown(card, unsafe_allow_html=True)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Keywords Processed", successful_keywords)
                        with col2:
                            st.metric("Total Results", total_results)
                        with col3:
                            st.metric(
                                "Success Rate",
                                f"{(successful_keywords/len(keywords)*100):.1f}%",
                            )

                except Exception as e:
                    st.markdown(
                        f"""
                        <div class="error-message">
                            <h4 style="margin: 0;">❌ Batch Processing Failed</h4>
                            <p style="margin: 0.5rem 0 0 0;">{str(e)}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    log_message(f"Batch processing failed: {str(e)}", "ERROR")

                st.session_state.processing_status = "idle"

        with col2:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; 
                            box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                    <h3 style="margin: 0 0 1rem 0; color: #333;">✏️ Manual Keywords</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            manual_keywords = st.text_area(
                "Enter keywords (one per line)",
                height=150,
                help="Enter multiple keywords, one per line",
            )

            if st.button(
                "🔍 Process Manual Keywords",
                disabled=not manual_keywords,
                use_container_width=True,
            ):
                if manual_keywords:
                    keywords_list = [
                        kw.strip() for kw in manual_keywords.split("\n") if kw.strip()
                    ]

                    if keywords_list:
                        st.markdown(
                            f"""
                            <div class="info-message">
                                <h4 style="margin: 0;">📋 Manual Processing</h4>
                                <p style="margin: 0.5rem 0 0 0;">Processing {len(keywords_list)} manual keywords...</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        all_results = []
                        search_cards = []

                        for i, keyword in enumerate(keywords_list):
                            status_text.text(f"🔍 Processing: {keyword}")

                            try:
                                results = scrape_auction_results(keyword, max_results)
                                if results:
                                    all_results.extend(results)
                                    st.session_state.stats["total_results"] += len(
                                        results
                                    )
                                    st.session_state.stats["successful_searches"] += 1

                                    # Calculate average price for this keyword
                                    prices = []
                                    for result in results:
                                        price = result.get("Current price", "")
                                        if price and price != "N/A":
                                            try:
                                                numeric_price = extract_price(price)
                                                if numeric_price:
                                                    prices.append(numeric_price)
                                            except:
                                                pass

                                    avg_price = (
                                        sum(prices) / len(prices) if prices else None
                                    )
                                    search_cards.append(
                                        create_search_card(
                                            keyword, len(results), avg_price
                                        )
                                    )

                                    log_message(
                                        f"Processed keyword '{keyword}': {len(results)} results"
                                    )
                                else:
                                    st.session_state.stats["failed_searches"] += 1
                                    log_message(
                                        f"No results for keyword '{keyword}'", "WARNING"
                                    )
                            except Exception as e:
                                st.session_state.stats["failed_searches"] += 1
                                log_message(
                                    f"Error processing keyword '{keyword}': {str(e)}",
                                    "ERROR",
                                )

                            progress = (i + 1) / len(keywords_list)
                            progress_bar.progress(progress)
                            time.sleep(0.1)

                        progress_bar.empty()
                        status_text.empty()

                        if all_results:
                            st.session_state.results_data = all_results
                            st.markdown(
                                f"""
                                <div class="success-message">
                                    <h4 style="margin: 0;">✅ Manual Processing Complete!</h4>
                                    <p style="margin: 0.5rem 0 0 0;">Found {len(all_results)} total results</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            # Display search cards
                            if search_cards:
                                st.markdown("### 📊 Processing Summary")
                                for card in search_cards:
                                    st.markdown(card, unsafe_allow_html=True)

                            # Enhanced download button
                            df = pd.DataFrame(all_results)
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download All Results",
                                data=csv,
                                file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                use_container_width=True,
                            )
                        else:
                            st.markdown(
                                """
                                <div class="warning-message">
                                    <h4 style="margin: 0;">⚠️ No Results Found</h4>
                                    <p style="margin: 0.5rem 0 0 0;">No results found for any keywords</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

    with tab3:
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 15px; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                <h2 style="margin: 0 0 1rem 0; color: #333;">📊 Results Viewer</h2>
                <p style="margin: 0; color: #666;">View and analyze your scraped auction data</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.results_data:
            st.markdown(
                f"""
                <div class="info-message">
                    <h4 style="margin: 0;">📊 Current Results</h4>
                    <p style="margin: 0.5rem 0 0 0;">{len(st.session_state.results_data)} items available for analysis</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Enhanced filter options
            col1, col2 = st.columns([1, 1])

            with col1:
                price_filter = st.selectbox(
                    "Filter by Price",
                    ["All", "Under $50", "$50-$100", "$100-$500", "Over $500"],
                )

            with col2:
                search_filter = st.text_input("Search in descriptions", "")

            # Apply filters
            filtered_results = st.session_state.results_data.copy()

            if price_filter != "All":
                # Apply price filtering logic here
                pass

            if search_filter:
                filtered_results = [
                    result
                    for result in filtered_results
                    if search_filter.lower()
                    in result.get("Item Description", "").lower()
                ]

            # Display filtered results
            if filtered_results:
                df = pd.DataFrame(filtered_results)
                st.markdown("### 📋 Filtered Results")
                st.dataframe(df, use_container_width=True)

                # Enhanced summary statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Items", len(filtered_results))
                with col2:
                    st.metric(
                        "Unique Keywords",
                        len(
                            set(
                                result.get("Keyword", "") for result in filtered_results
                            )
                        ),
                    )
                with col3:
                    # Calculate average price
                    prices = []
                    for result in filtered_results:
                        price = result.get("Current price", "")
                        if price and price != "N/A":
                            try:
                                numeric_price = extract_price(price)
                                if numeric_price:
                                    prices.append(numeric_price)
                            except:
                                pass

                    avg_price = f"${sum(prices) / len(prices):.2f}" if prices else "N/A"
                    st.metric("Average Price", avg_price)
                with col4:
                    st.metric("Filtered Items", len(filtered_results))
            else:
                st.markdown(
                    """
                    <div class="warning-message">
                        <h4 style="margin: 0;">⚠️ No Matching Results</h4>
                        <p style="margin: 0.5rem 0 0 0;">No results match the current filters</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="info-message">
                    <h4 style="margin: 0;">📊 No Results Available</h4>
                    <p style="margin: 0.5rem 0 0 0;">Run a search first to see results here!</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab4:
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 15px; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                <h2 style="margin: 0 0 1rem 0; color: #333;">🦆 Database Analytics</h2>
                <p style="margin: 0; color: #666;">Analyze stored auction data and generate insights</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            db = get_database()

            # Database Overview
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                stats = db.get_database_stats()
                st.metric("Total Records", stats.get("total_records", 0))

            with col2:
                st.metric("Unique Keywords", stats.get("unique_keywords", 0))

            with col3:
                avg_price = stats.get("avg_price", 0)
                st.metric("Avg Price", f"${avg_price:.2f}" if avg_price else "N/A")

            with col4:
                median_price = stats.get("median_price", 0)
                st.metric(
                    "Median Price", f"${median_price:.2f}" if median_price else "N/A"
                )

            # Analytics Sections
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader("📊 Keyword Statistics")
                keyword_stats = db.get_keyword_stats()
                if not keyword_stats.empty:
                    st.dataframe(keyword_stats, use_container_width=True)
                else:
                    st.info(
                        "No keyword data available yet. Run some searches to populate the database."
                    )

            with col2:
                st.subheader("🔍 Quick Search")
                search_term = st.text_input("Search items by description")
                if search_term:
                    results = db.search_items(search_term, limit=10)
                    if not results.empty:
                        st.dataframe(
                            results[["keyword", "item_description", "current_price"]],
                            use_container_width=True,
                        )
                    else:
                        st.info("No items found matching your search.")

            # Price Analytics
            st.subheader("💰 Price Analytics")
            price_stats = db.get_price_analytics()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Min Price", f"${price_stats.get('min_price', 0):.2f}")
            with col2:
                st.metric("Max Price", f"${price_stats.get('max_price', 0):.2f}")
            with col3:
                st.metric("Total Items", price_stats.get("total_items", 0))

            # Recent Activity
            st.subheader("⏰ Recent Activity")
            hours = st.slider("Hours to look back", 1, 168, 24)
            recent_results = db.get_recent_results(hours)

            if not recent_results.empty:
                st.dataframe(
                    recent_results[
                        ["keyword", "item_description", "current_price", "scraped_at"]
                    ],
                    use_container_width=True,
                )
            else:
                st.info(f"No activity in the last {hours} hours.")

            # Export Options
            st.subheader("📤 Export Data")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Export All Data to CSV"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"auction_data_export_{timestamp}.csv"
                    db.export_to_csv(filename)
                    st.success(f"Data exported to {filename}")

            with col2:
                keyword_filter = st.text_input("Filter by keyword for export")
                if keyword_filter and st.button("Export Filtered Data"):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"auction_data_{keyword_filter}_{timestamp}.csv"
                    db.export_to_csv(filename, keyword=keyword_filter)
                    st.success(f"Filtered data exported to {filename}")

        except Exception as e:
            st.error(f"Database error: {str(e)}")
            st.info("Make sure DuckDB is installed: pip install duckdb")

    with tab5:
        st.markdown(
            """
            <div style="background: rgba(255, 255, 255, 0.95); padding: 2rem; border-radius: 15px; 
                        box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 2rem;">
                <h2 style="margin: 0 0 1rem 0; color: #333;">🛠️ Utilities</h2>
                <p style="margin: 0; color: #666;">Test and validate data processing functions</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; 
                            box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                    <h3 style="margin: 0 0 1rem 0; color: #333;">🧹 Text Processing</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            test_text = st.text_input(
                "Test text cleaning", "  This   is   dirty   text  "
            )
            if st.button("Clean Text", use_container_width=True):
                cleaned = clean_text(test_text)
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #333;">Text Cleaning Results</h4>
                        <p style="margin: 0; color: #666;"><strong>Original:</strong> <code>{test_text}</code></p>
                        <p style="margin: 0.5rem 0 0 0; color: #666;"><strong>Cleaned:</strong> <code>{cleaned}</code></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            test_keyword = st.text_input(
                "Test keyword sanitization", "  Gore-Tex  Jacket  "
            )
            if st.button("Sanitize Keyword", use_container_width=True):
                sanitized = sanitize_keyword(test_keyword)
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #333;">Keyword Sanitization Results</h4>
                        <p style="margin: 0; color: #666;"><strong>Original:</strong> <code>{test_keyword}</code></p>
                        <p style="margin: 0.5rem 0 0 0; color: #666;"><strong>Sanitized:</strong> <code>{sanitized}</code></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown(
                """
                <div style="background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; 
                            box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                    <h3 style="margin: 0 0 1rem 0; color: #333;">✅ Data Validation</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            test_price = st.text_input("Test price extraction", "$123.45")
            if st.button("Extract Price", use_container_width=True):
                extracted = extract_price(test_price)
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #333;">Price Extraction Results</h4>
                        <p style="margin: 0; color: #666;"><strong>Input:</strong> <code>{test_price}</code></p>
                        <p style="margin: 0.5rem 0 0 0; color: #666;"><strong>Extracted:</strong> <code>{extracted}</code></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            test_date = st.text_input("Test date formatting", "  Dec 15, 2024  ")
            if st.button("Format Date", use_container_width=True):
                formatted = format_date(test_date)
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <h4 style="margin: 0 0 0.5rem 0; color: #333;">Date Formatting Results</h4>
                        <p style="margin: 0; color: #666;"><strong>Input:</strong> <code>{test_date}</code></p>
                        <p style="margin: 0.5rem 0 0 0; color: #666;"><strong>Formatted:</strong> <code>{formatted}</code></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Display logs at the bottom with enhanced styling
    display_logs()


def main_app():
    """Main entry point for the Streamlit app."""
    main()


if __name__ == "__main__":
    # Add project root to path to ensure imports work
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Run the main app
    main()
