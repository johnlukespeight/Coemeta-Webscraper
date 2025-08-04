#!/usr/bin/env python3
"""
Simple test script to debug Google Sheets connection issues
"""

import os
import json
from google_sheets import get_gspread_client, read_keywords


def test_connection():
    """Test the Google Sheets connection step by step"""
    print("🔍 Testing Google Sheets Connection")
    print("=" * 50)

    # Step 1: Check if service account file exists
    service_account_path = "service_account.json"
    print(f"1. Checking service account file: {service_account_path}")

    if not os.path.exists(service_account_path):
        print(f"❌ Service account file not found: {service_account_path}")
        return False

    print(f"✅ Service account file found: {service_account_path}")

    # Step 2: Validate JSON structure
    print("\n2. Validating JSON structure...")
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
            print(f"❌ Invalid JSON structure. Missing fields: {missing_fields}")
            return False

        print("✅ JSON structure is valid")
        print(f"   Project ID: {data.get('project_id', 'N/A')}")
        print(f"   Client Email: {data.get('client_email', 'N/A')}")

    except json.JSONDecodeError:
        print("❌ Invalid JSON file")
        return False
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        return False

    # Step 3: Test gspread authentication
    print("\n3. Testing gspread authentication...")
    try:
        client = get_gspread_client(service_account_path)
        print("✅ gspread authentication successful")
    except Exception as e:
        print(f"❌ gspread authentication failed: {e}")
        return False

    # Step 4: Test sheet access
    print("\n4. Testing sheet access...")
    sheet_id = "1RaEyw9cb7i7gvm3wPr1OMVsJKElxlvdKBp8GgXMmMKo"
    print(f"   Sheet ID: {sheet_id}")

    try:
        # Try to open the sheet
        sheet = client.open_by_key(sheet_id)
        print("✅ Sheet access successful")
        print(f"   Sheet title: {sheet.title}")

        # List available worksheets
        worksheets = sheet.worksheets()
        worksheet_names = [ws.title for ws in worksheets]
        print(f"   Available worksheets: {worksheet_names}")

        # Test different worksheet name variations
        print("\n5. Testing worksheet access...")
        possible_names = ["KEYWORDS", "[KEYWORDS]", "Keywords", "keywords"]

        for name in possible_names:
            try:
                worksheet = sheet.worksheet(name)
                print(f"✅ Found worksheet: '{name}'")
                # Try to read some data
                values = worksheet.col_values(1)
                print(f"   Found {len(values)} values in column A")
                if values:
                    print(f"   Sample values: {values[:3]}")
                break
            except Exception as e:
                print(f"❌ Worksheet '{name}' not found or accessible")
                continue
        else:
            print("❌ Could not find any keywords worksheet")
            print("Available worksheets:", worksheet_names)
            return False

    except Exception as e:
        print(f"❌ Sheet access failed: {e}")
        print("\n💡 Possible solutions:")
        print("1. Check if the sheet ID is correct")
        print("2. Make sure your service account has access to the sheet")
        print("3. Share the sheet with your service account email")
        return False

    print("\n🎉 All tests passed! Your Google Sheets connection is working.")
    return True


if __name__ == "__main__":
    test_connection()
