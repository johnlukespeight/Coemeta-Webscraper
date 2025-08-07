#!/usr/bin/env python3
"""
Debug script to check database table structure
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import duckdb


def debug_database():
    """Debug the database table structure"""
    print("🔍 Debugging Database Structure")
    print("=" * 40)

    try:
        # Connect to database
        conn = duckdb.connect("auction_data.duckdb")

        # Check if tables exist
        tables = conn.execute("SHOW TABLES").fetchall()
        print(f"Tables in database: {tables}")

        # Check table structure
        if tables:
            for table in tables:
                table_name = table[0]
                print(f"\n📋 Table: {table_name}")
                schema = conn.execute(f"DESCRIBE {table_name}").fetchall()
                for col in schema:
                    print(f"  {col[0]}: {col[1]}")

        # Try to create a simple test table
        print("\n🧪 Creating test table...")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                keyword VARCHAR,
                description TEXT
            )
        """
        )

        # Insert test data
        conn.execute(
            """
            INSERT INTO test_table (keyword, description)
            VALUES ('test', 'test description')
        """
        )

        # Query test data
        result = conn.execute("SELECT * FROM test_table").fetchall()
        print(f"Test data: {result}")

        conn.close()
        print("✅ Database debug completed")

    except Exception as e:
        print(f"❌ Database debug failed: {e}")


if __name__ == "__main__":
    debug_database()
