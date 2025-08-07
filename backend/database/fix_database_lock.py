#!/usr/bin/env python3
"""
Script to fix DuckDB database locking issues
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
import time


def fix_database_lock():
    """Fix database locking issues by cleaning up and recreating the database"""
    print("🔧 Fixing Database Lock Issues")
    print("=" * 40)

    db_path = "auction_data.duckdb"

    # Check if database file exists
    if os.path.exists(db_path):
        print(f"Found database file: {db_path}")

        # Create backup
        backup_path = f"{db_path}.backup_{int(time.time())}"
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✅ Created backup: {backup_path}")
        except Exception as e:
            print(f"⚠️ Could not create backup: {e}")

        # Try to remove the locked file
        try:
            os.remove(db_path)
            print("✅ Removed locked database file")
        except Exception as e:
            print(f"⚠️ Could not remove file: {e}")
            print("You may need to restart your system or manually delete the file")
            return False

    # Create a new database file
    try:
        import duckdb

        conn = duckdb.connect(db_path)
        conn.close()
        print("✅ Created new database file")
        return True
    except Exception as e:
        print(f"❌ Could not create new database: {e}")
        return False


if __name__ == "__main__":
    fix_database_lock()
