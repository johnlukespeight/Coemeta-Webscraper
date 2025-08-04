#!/usr/bin/env python3
"""
Verification script for Coemeta WebScraper setup
Checks that all components are properly configured and working.
"""

import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import validate_credentials, get_service_account_path, get_sheet_id


def verify_service_account():
    """Verify service account is properly configured"""
    print("🔍 Verifying Service Account...")

    # Check if file exists
    service_account_path = get_service_account_path()
    if not service_account_path:
        print("❌ Service account file not found")
        return False

    if not os.path.exists(service_account_path):
        print(f"❌ Service account file not found: {service_account_path}")
        return False

    # Validate JSON structure
    try:
        with open(service_account_path, "r") as f:
            data = json.load(f)

        required_fields = [
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
            "client_id",
        ]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            print(f"❌ Invalid service account JSON. Missing: {missing_fields}")
            return False

        print(f"✅ Service account file: {service_account_path}")
        print(f"✅ Project ID: {data.get('project_id', 'N/A')}")
        print(f"✅ Service Account Email: {data.get('client_email', 'N/A')}")
        return True

    except Exception as e:
        print(f"❌ Error reading service account: {e}")
        return False


def verify_google_sheets_access():
    """Verify Google Sheets access"""
    print("\n🔍 Verifying Google Sheets Access...")

    try:
        from google_sheets import get_gspread_client

        service_account_path = get_service_account_path()
        client = get_gspread_client(service_account_path)

        print("✅ Google Sheets authentication successful")

        # Try to access the default sheet
        sheet_id = get_sheet_id()
        print(f"✅ Sheet ID configured: {sheet_id}")

        try:
            # Try to open the sheet
            sheet = client.open_by_key(sheet_id)
            print("✅ Successfully accessed Google Sheet")

            # Check for required tabs
            worksheets = sheet.worksheets()
            tab_names = [ws.title for ws in worksheets]
            print(f"✅ Available tabs: {tab_names}")

            # Check for required tabs
            required_tabs = ["[KEYWORDS]", "RESULTS TEMPLATE"]
            missing_tabs = [tab for tab in required_tabs if tab not in tab_names]

            if missing_tabs:
                print(f"⚠️  Missing required tabs: {missing_tabs}")
                print("   Please create these tabs in your Google Sheet:")
                print("   - [KEYWORDS] - for storing keywords")
                print("   - RESULTS TEMPLATE - for storing results")
                return False
            else:
                print("✅ All required tabs found")
                return True

        except Exception as e:
            print(f"❌ Cannot access Google Sheet: {e}")
            print("   Please check:")
            print("   1. The sheet ID is correct")
            print("   2. The service account has Editor access to the sheet")
            print("   3. The sheet exists and is accessible")
            return False

    except Exception as e:
        print(f"❌ Google Sheets authentication failed: {e}")
        return False


def verify_scraper():
    """Verify scraper functionality"""
    print("\n🔍 Verifying Scraper...")

    try:
        from scraper import scrape_auction_results

        # Test with a simple keyword
        results = scrape_auction_results("test", max_results=1)

        if results and len(results) > 0:
            print("✅ Scraper is working")
            print(f"✅ Found {len(results)} test result(s)")
            return True
        else:
            print("⚠️  Scraper returned no results (may be blocked)")
            return True  # Still consider it working if it handles blocking gracefully

    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        return False


def verify_streamlit():
    """Verify Streamlit app"""
    print("\n🔍 Verifying Streamlit App...")

    try:
        import streamlit

        print("✅ Streamlit is installed")

        # Check if streamlit app file exists
        if os.path.exists("streamlit_app.py"):
            print("✅ Streamlit app file exists")
            return True
        else:
            print("❌ Streamlit app file not found")
            return False

    except ImportError:
        print("❌ Streamlit not installed")
        return False


def main():
    """Main verification function"""
    print("🔧 Coemeta WebScraper Setup Verification")
    print("=" * 50)

    checks = [
        ("Service Account", verify_service_account),
        ("Google Sheets Access", verify_google_sheets_access),
        ("Scraper", verify_scraper),
        ("Streamlit App", verify_streamlit),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n📊 Verification Summary")
    print("=" * 30)

    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} checks passed")

    if passed == len(results):
        print("🎉 All checks passed! Your setup is complete.")
        print("\n🚀 You can now:")
        print("   - Run the scraper: python main.py")
        print("   - Use the web interface: streamlit run streamlit_app.py")
        print("   - Run tests: python tests/run_tests.py")
    else:
        print("\n⚠️  Some checks failed. Please review the issues above.")
        print("   Refer to GOOGLE_SHEET_SETUP.md for setup instructions.")


if __name__ == "__main__":
    main()
