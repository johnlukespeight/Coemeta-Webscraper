import streamlit as st
import pandas as pd
import time
from datetime import datetime
import os
from google_sheets import get_gspread_client, write_results, read_keywords
from scraper import scrape_auction_results
from utils import (
    setup_logging,
    sanitize_keyword,
    clean_text,
    log_scraping_stats,
    validate_auction_data,
    extract_price,
    format_date,
)

# Page configuration
st.set_page_config(
    page_title="Coemeta WebScraper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialize session state variables"""
    if "results_data" not in st.session_state:
        st.session_state.results_data = []
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = "idle"
    if "logs" not in st.session_state:
        st.session_state.logs = []


def log_message(message, level="INFO"):
    """Add a message to the logs"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {level}: {message}")


def display_logs():
    """Display logs in a scrollable container"""
    if st.session_state.logs:
        with st.expander("📋 Activity Logs", expanded=False):
            for log in st.session_state.logs[-20:]:  # Show last 20 logs
                st.text(log)


def main():
    st.markdown(
        '<h1 class="main-header">🔍 Coemeta WebScraper</h1>', unsafe_allow_html=True
    )

    initialize_session_state()

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Google Sheets configuration
        st.subheader("Google Sheets")
        sheet_id = st.text_input(
            "Sheet ID",
            value="1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo",
            help="The Google Sheet ID where keywords are stored and results will be written",
        )

        # Service account path
        service_account_path = st.text_input(
            "Service Account JSON Path",
            value="service_account.json",
            help="Path to your Google Service Account JSON file",
        )

        # Scraping configuration
        st.subheader("Scraping Settings")
        max_results = st.slider(
            "Max Results per Keyword",
            min_value=1,
            max_value=50,
            value=10,
            help="Maximum number of results to scrape per keyword",
        )

        # Test connection button
        if st.button("🔗 Test Google Sheets Connection"):
            with st.spinner("Testing connection..."):
                try:
                    client = get_gspread_client(service_account_path)
                    keywords = read_keywords(sheet_id, client)
                    st.success(f"✅ Connected! Found {len(keywords)} keywords")
                    log_message(
                        f"Successfully connected to Google Sheets. Found {len(keywords)} keywords"
                    )
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
                    log_message(f"Google Sheets connection failed: {str(e)}", "ERROR")

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🔍 Single Search", "📋 Batch Processing", "📊 Results Viewer", "🛠️ Utilities"]
    )

    with tab1:
        st.header("Single Keyword Search")

        col1, col2 = st.columns([2, 1])

        with col1:
            keyword = st.text_input(
                "Enter keyword to search",
                placeholder="e.g., gore-tex, vintage watch, etc.",
                help="Enter a keyword to search for auction items",
            )

            if st.button("🔍 Search", type="primary", disabled=not keyword):
                if keyword:
                    st.session_state.processing_status = "searching"

                    with st.spinner(f"Searching for '{keyword}'..."):
                        try:
                            results = scrape_auction_results(keyword, max_results)

                            if results:
                                st.session_state.results_data = results
                                st.success(
                                    f"✅ Found {len(results)} results for '{keyword}'"
                                )
                                log_message(
                                    f"Found {len(results)} results for keyword: {keyword}"
                                )

                                # Display results in a table
                                df = pd.DataFrame(results)
                                st.dataframe(df, use_container_width=True)

                                # Download button
                                csv = df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Results as CSV",
                                    data=csv,
                                    file_name=f"auction_results_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                )
                            else:
                                st.warning(f"⚠️ No results found for '{keyword}'")
                                log_message(
                                    f"No results found for keyword: {keyword}",
                                    "WARNING",
                                )

                        except Exception as e:
                            st.error(f"❌ Search failed: {str(e)}")
                            log_message(
                                f"Search failed for keyword {keyword}: {str(e)}",
                                "ERROR",
                            )

                    st.session_state.processing_status = "idle"

        with col2:
            st.subheader("Quick Stats")
            if st.session_state.results_data:
                st.metric("Total Results", len(st.session_state.results_data))

                # Calculate average price if available
                prices = []
                for result in st.session_state.results_data:
                    price = result.get("Current price", "")
                    if price and price != "N/A":
                        try:
                            # Extract numeric value from price
                            numeric_price = extract_price(price)
                            if numeric_price:
                                prices.append(numeric_price)
                        except:
                            pass

                if prices:
                    avg_price = sum(prices) / len(prices)
                    st.metric("Average Price", f"${avg_price:.2f}")

    with tab2:
        st.header("Batch Processing")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("From Google Sheets")

            if st.button("📋 Process All Keywords", type="primary"):
                st.session_state.processing_status = "batch_processing"

                try:
                    client = get_gspread_client(service_account_path)
                    keywords = read_keywords(sheet_id, client)

                    if not keywords:
                        st.warning("⚠️ No keywords found in the sheet!")
                        return

                    st.info(f"📋 Processing {len(keywords)} keywords...")

                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    total_results = 0
                    successful_keywords = 0

                    for i, keyword in enumerate(keywords):
                        status_text.text(f"Processing: {keyword}")

                        try:
                            results = scrape_auction_results(keyword, max_results)

                            if results:
                                write_results(sheet_id, keyword, results, client)
                                total_results += len(results)
                                successful_keywords += 1
                                log_message(
                                    f"Processed keyword '{keyword}': {len(results)} results"
                                )
                            else:
                                log_message(
                                    f"No results for keyword '{keyword}'", "WARNING"
                                )

                        except Exception as e:
                            log_message(
                                f"Error processing keyword '{keyword}': {str(e)}",
                                "ERROR",
                            )

                        # Update progress
                        progress = (i + 1) / len(keywords)
                        progress_bar.progress(progress)
                        time.sleep(0.1)  # Small delay for UI responsiveness

                    progress_bar.empty()
                    status_text.empty()

                    st.success(f"✅ Batch processing complete!")
                    st.metric("Keywords Processed", successful_keywords)
                    st.metric("Total Results", total_results)

                except Exception as e:
                    st.error(f"❌ Batch processing failed: {str(e)}")
                    log_message(f"Batch processing failed: {str(e)}", "ERROR")

                st.session_state.processing_status = "idle"

        with col2:
            st.subheader("Manual Keywords")

            manual_keywords = st.text_area(
                "Enter keywords (one per line)",
                height=150,
                help="Enter multiple keywords, one per line",
            )

            if st.button("🔍 Process Manual Keywords", disabled=not manual_keywords):
                if manual_keywords:
                    keywords_list = [
                        kw.strip() for kw in manual_keywords.split("\n") if kw.strip()
                    ]

                    if keywords_list:
                        st.info(
                            f"📋 Processing {len(keywords_list)} manual keywords..."
                        )

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        all_results = []

                        for i, keyword in enumerate(keywords_list):
                            status_text.text(f"Processing: {keyword}")

                            try:
                                results = scrape_auction_results(keyword, max_results)
                                if results:
                                    all_results.extend(results)
                                    log_message(
                                        f"Processed keyword '{keyword}': {len(results)} results"
                                    )
                                else:
                                    log_message(
                                        f"No results for keyword '{keyword}'", "WARNING"
                                    )
                            except Exception as e:
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
                            st.success(f"✅ Found {len(all_results)} total results")

                            # Download all results
                            df = pd.DataFrame(all_results)
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download All Results",
                                data=csv,
                                file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                            )
                        else:
                            st.warning("⚠️ No results found for any keywords")

    with tab3:
        st.header("Results Viewer")

        if st.session_state.results_data:
            st.subheader(
                f"📊 Current Results ({len(st.session_state.results_data)} items)"
            )

            # Filter options
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
                st.dataframe(df, use_container_width=True)

                # Summary statistics
                col1, col2, col3 = st.columns(3)
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
                    avg_price = "N/A"
                    # Calculate average price if possible
                    st.metric("Average Price", avg_price)
            else:
                st.info("No results match the current filters")
        else:
            st.info("No results available. Run a search first!")

    with tab4:
        st.header("Utility Functions")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Text Processing")

            test_text = st.text_input(
                "Test text cleaning", "  This   is   dirty   text  "
            )
            if st.button("Clean Text"):
                cleaned = clean_text(test_text)
                st.write(f"**Original:** `{test_text}`")
                st.write(f"**Cleaned:** `{cleaned}`")

            test_keyword = st.text_input(
                "Test keyword sanitization", "  Gore-Tex  Jacket  "
            )
            if st.button("Sanitize Keyword"):
                sanitized = sanitize_keyword(test_keyword)
                st.write(f"**Original:** `{test_keyword}`")
                st.write(f"**Sanitized:** `{sanitized}`")

        with col2:
            st.subheader("Data Validation")

            test_price = st.text_input("Test price extraction", "$123.45")
            if st.button("Extract Price"):
                extracted = extract_price(test_price)
                st.write(f"**Input:** `{test_price}`")
                st.write(f"**Extracted:** `{extracted}`")

            test_date = st.text_input("Test date formatting", "  Dec 15, 2024  ")
            if st.button("Format Date"):
                formatted = format_date(test_date)
                st.write(f"**Input:** `{test_date}`")
                st.write(f"**Formatted:** `{formatted}`")

    # Display logs at the bottom
    display_logs()


if __name__ == "__main__":
    main()
