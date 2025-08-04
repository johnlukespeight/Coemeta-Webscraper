"""
DuckDB Database Module for Coemeta WebScraper
Handles data storage, querying, and analytics for auction results.
"""

import duckdb
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import os
import threading
import atexit


class AuctionDatabase:
    """DuckDB database manager for auction data"""

    def __init__(self, db_path: str = "auction_data.duckdb"):
        """
        Initialize the database connection

        Args:
            db_path (str): Path to the DuckDB database file
        """
        self.db_path = db_path
        self._lock = threading.Lock()
        self.conn = None
        self._connect()
        self._create_tables()

        # Register cleanup on exit
        atexit.register(self.close)

    def _connect(self):
        """Create a new database connection with proper settings"""
        try:
            # Use read-write mode with better concurrency handling
            self.conn = duckdb.connect(self.db_path, read_only=False)
        except Exception as e:
            print(f"Warning: Could not connect to database: {e}")
            # Try with different settings or create new file
            try:
                # Try with read-only mode first
                self.conn = duckdb.connect(self.db_path, read_only=True)
                self.conn.close()
                # Now try read-write
                self.conn = duckdb.connect(self.db_path, read_only=False)
            except:
                # If all else fails, create a new database file
                import os

                backup_path = f"{self.db_path}.backup"
                if os.path.exists(self.db_path):
                    os.rename(self.db_path, backup_path)
                self.conn = duckdb.connect(self.db_path, read_only=False)

    def _create_tables(self):
        """Create the necessary tables if they don't exist"""
        with self._lock:
            try:
                # Create auction_results table
                self.conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS auction_results (
                        keyword VARCHAR,
                        item_description TEXT,
                        current_price DECIMAL(10,2),
                        auction_end_date DATE,
                        image_url TEXT,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        source_url TEXT
                    )
                """
                )

                # Create keywords table for tracking
                self.conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS keywords (
                        id INTEGER PRIMARY KEY,
                        keyword VARCHAR UNIQUE,
                        last_scraped TIMESTAMP,
                        total_results INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create scraping_sessions table for analytics
                self.conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scraping_sessions (
                        id INTEGER PRIMARY KEY,
                        session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        session_end TIMESTAMP,
                        keywords_processed INTEGER DEFAULT 0,
                        total_results INTEGER DEFAULT 0,
                        status VARCHAR DEFAULT 'running'
                    )
                """
                )

                self.conn.commit()
            except Exception as e:
                print(f"Warning: Could not create tables: {e}")

    def insert_auction_results(self, keyword: str, results: List[Dict]) -> int:
        """
        Insert auction results into the database

        Args:
            keyword (str): The search keyword
            results (List[Dict]): List of auction result dictionaries

        Returns:
            int: Number of results inserted
        """
        if not results:
            return 0

        with self._lock:
            try:
                # Convert results to DataFrame
                df = pd.DataFrame(results)

                # Add keyword column
                df["keyword"] = keyword
                df["scraped_at"] = datetime.now()

                # Rename columns to match database schema
                column_mapping = {
                    "Item Description": "item_description",
                    "Current price": "current_price",
                    "Auction end date": "auction_end_date",
                    "Auction image / thumbnail URL (extra credit)": "image_url",
                }
                df = df.rename(columns=column_mapping)

                # Select only the columns we need
                columns_to_insert = [
                    "keyword",
                    "item_description",
                    "current_price",
                    "auction_end_date",
                    "image_url",
                    "scraped_at",
                ]

                df_to_insert = df[columns_to_insert].copy()

                # Clean price data
                df_to_insert["current_price"] = pd.to_numeric(
                    df_to_insert["current_price"]
                    .str.replace("$", "")
                    .str.replace(",", ""),
                    errors="coerce",
                )

                # Insert into database using proper DuckDB syntax
                for _, row in df_to_insert.iterrows():
                    self.conn.execute(
                        """
                        INSERT INTO auction_results 
                        (keyword, item_description, current_price, auction_end_date, image_url, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        [
                            str(row["keyword"]),
                            str(row["item_description"]),
                            (
                                float(row["current_price"])
                                if pd.notna(row["current_price"])
                                else None
                            ),
                            (
                                str(row["auction_end_date"])
                                if pd.notna(row["auction_end_date"])
                                else None
                            ),
                            (
                                str(row["image_url"])
                                if pd.notna(row["image_url"])
                                else None
                            ),
                            str(row["scraped_at"]),
                        ],
                    )
                self.conn.commit()

                # Update keywords table
                self.conn.execute(
                    """
                    INSERT OR REPLACE INTO keywords (keyword, last_scraped, total_results)
                    VALUES (?, ?, ?)
                """,
                    [keyword, datetime.now(), len(results)],
                )
                self.conn.commit()

                return len(results)
            except Exception as e:
                print(f"Database save failed for keyword {keyword}: {e}")
                # Try to reconnect if connection is lost
                try:
                    self._connect()
                except:
                    pass
                return 0

    def get_auction_results(
        self,
        keyword: Optional[str] = None,
        limit: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> pd.DataFrame:
        """
        Query auction results from the database

        Args:
            keyword (str, optional): Filter by keyword
            limit (int, optional): Limit number of results
            min_price (float, optional): Minimum price filter
            max_price (float, optional): Maximum price filter

        Returns:
            pd.DataFrame: Query results
        """
        query = "SELECT * FROM auction_results WHERE 1=1"
        params = []

        if keyword:
            query += " AND keyword ILIKE ?"
            params.append(f"%{keyword}%")

        if min_price is not None:
            query += " AND current_price >= ?"
            params.append(min_price)

        if max_price is not None:
            query += " AND current_price <= ?"
            params.append(max_price)

        query += " ORDER BY scraped_at DESC"

        if limit:
            query += f" LIMIT {limit}"

        return self.conn.execute(query, params).df()

    def get_keyword_stats(self) -> pd.DataFrame:
        """
        Get statistics for all keywords

        Returns:
            pd.DataFrame: Keyword statistics
        """
        return self.conn.execute(
            """
            SELECT 
                ar.keyword,
                COUNT(*) as total_items,
                AVG(current_price) as avg_price,
                MIN(current_price) as min_price,
                MAX(current_price) as max_price,
                MAX(last_scraped) as last_scraped
            FROM auction_results ar
            LEFT JOIN keywords k ON ar.keyword = k.keyword
            GROUP BY ar.keyword
            ORDER BY total_items DESC
        """
        ).df()

    def get_price_analytics(self) -> Dict:
        """
        Get price analytics across all data

        Returns:
            Dict: Price analytics
        """
        result = self.conn.execute(
            """
            SELECT 
                COUNT(*) as total_items,
                AVG(current_price) as avg_price,
                MIN(current_price) as min_price,
                MAX(current_price) as max_price,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY current_price) as median_price
            FROM auction_results
            WHERE current_price IS NOT NULL
        """
        ).fetchone()

        return {
            "total_items": result[0],
            "avg_price": result[1],
            "min_price": result[2],
            "max_price": result[3],
            "median_price": result[4],
        }

    def search_items(self, search_term: str, limit: int = 50) -> pd.DataFrame:
        """
        Search items by description

        Args:
            search_term (str): Search term
            limit (int): Maximum results to return

        Returns:
            pd.DataFrame: Search results
        """
        return self.conn.execute(
            """
            SELECT * FROM auction_results
            WHERE item_description ILIKE ?
            ORDER BY scraped_at DESC
            LIMIT ?
        """,
            (f"%{search_term}%", limit),
        ).df()

    def get_recent_results(self, hours: int = 24) -> pd.DataFrame:
        """
        Get results from the last N hours

        Args:
            hours (int): Number of hours to look back

        Returns:
            pd.DataFrame: Recent results
        """
        return self.conn.execute(
            """
            SELECT * FROM auction_results
            WHERE scraped_at >= datetime('now', '-{} hours')
            ORDER BY scraped_at DESC
        """.format(
                hours
            )
        ).df()

    def export_to_csv(self, filepath: str, keyword: Optional[str] = None):
        """
        Export data to CSV

        Args:
            filepath (str): Output file path
            keyword (str, optional): Filter by keyword
        """
        df = self.get_auction_results(keyword=keyword)
        df.to_csv(filepath, index=False)

    def get_database_stats(self) -> Dict:
        """
        Get overall database statistics

        Returns:
            Dict: Database statistics
        """
        stats = {}

        # Total records
        result = self.conn.execute("SELECT COUNT(*) FROM auction_results").fetchone()
        stats["total_records"] = result[0]

        # Unique keywords
        result = self.conn.execute(
            "SELECT COUNT(DISTINCT keyword) FROM auction_results"
        ).fetchone()
        stats["unique_keywords"] = result[0]

        # Date range
        result = self.conn.execute(
            """
            SELECT MIN(scraped_at), MAX(scraped_at) FROM auction_results
        """
        ).fetchone()
        stats["date_range"] = {"earliest": result[0], "latest": result[1]}

        # Price statistics
        price_stats = self.get_price_analytics()
        stats.update(price_stats)

        return stats

    def close(self):
        """Close the database connection"""
        try:
            if self.conn:
                with self._lock:
                    self.conn.close()
                    self.conn = None
        except Exception as e:
            print(f"Warning: Error closing database connection: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global database instance
_db_instance = None
_db_lock = threading.Lock()


def get_database() -> AuctionDatabase:
    """
    Get the global database instance

    Returns:
        AuctionDatabase: Database instance
    """
    global _db_instance
    with _db_lock:
        if _db_instance is None:
            try:
                _db_instance = AuctionDatabase()
            except Exception as e:
                print(f"Warning: Could not create database instance: {e}")
                # Try with a different database path
                import os
                import tempfile

                temp_db_path = os.path.join(
                    tempfile.gettempdir(), "auction_data_temp.duckdb"
                )
                _db_instance = AuctionDatabase(temp_db_path)
        return _db_instance


def close_database():
    """Close the global database connection"""
    global _db_instance
    with _db_lock:
        if _db_instance:
            _db_instance.close()
            _db_instance = None
