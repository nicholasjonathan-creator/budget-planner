#!/usr/bin/env python3
"""
Database Transaction Analysis
Direct database inspection to understand the filtering issue
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fe5a1b17-dacb-468f-a395-f044dbe77291.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user
TEST_USER = {"email": "testuser@example.com", "password": "testpassword123"}

class DatabaseAnalyzer:
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        
    def authenticate_user(self):
        """Authenticate the test user"""
        try:
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json=TEST_USER,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.auth_token = login_data.get("access_token")
                self.user_id = login_data.get("user", {}).get("id")
                print(f"✅ Authenticated: {TEST_USER['email']}")
                return True
            else:
                print(f"❌ Authentication failed: {login_response.status_code}")
                return False
                    
        except Exception as e:
            print(f"❌ Error authenticating: {e}")
            return False

    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    def analyze_transaction_dates(self):
        """Analyze all transaction dates to understand the filtering issue"""
        print("\n🔍 Analyzing Transaction Dates...")
        print("=" * 80)
        
        try:
            # Get all transactions
            response = requests.get(
                f"{API_BASE}/transactions",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                transactions = response.json()
                print(f"Total transactions: {len(transactions)}")
                
                # Analyze each transaction's date
                july_2025_transactions = []
                date_formats = {}
                
                for i, transaction in enumerate(transactions):
                    amount = transaction.get('amount', 0)
                    date_str = transaction.get('date', 'unknown')
                    description = transaction.get('description', 'N/A')
                    source = transaction.get('source', 'unknown')
                    
                    print(f"\nTransaction {i+1}:")
                    print(f"  Amount: ₹{amount}")
                    print(f"  Description: {description}")
                    print(f"  Date (raw): {date_str}")
                    print(f"  Source: {source}")
                    
                    # Try to parse the date
                    try:
                        if isinstance(date_str, str):
                            if 'T' in date_str:
                                # ISO format
                                parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                date_format = "ISO"
                            else:
                                # Try other formats
                                parsed_date = datetime.fromisoformat(date_str)
                                date_format = "ISO_simple"
                        else:
                            # Might be already a datetime object
                            parsed_date = date_str
                            date_format = "datetime_object"
                        
                        print(f"  Parsed Date: {parsed_date}")
                        print(f"  Year: {parsed_date.year}, Month: {parsed_date.month}")
                        
                        # Check if it's July 2025
                        if parsed_date.year == 2025 and parsed_date.month == 7:
                            july_2025_transactions.append(transaction)
                            print(f"  *** JULY 2025 TRANSACTION ***")
                        
                        date_formats[date_format] = date_formats.get(date_format, 0) + 1
                        
                    except Exception as e:
                        print(f"  ❌ Date parsing error: {e}")
                        date_formats["parse_error"] = date_formats.get("parse_error", 0) + 1
                
                print(f"\n📊 Summary:")
                print(f"  Total transactions: {len(transactions)}")
                print(f"  July 2025 transactions found: {len(july_2025_transactions)}")
                print(f"  Date formats: {date_formats}")
                
                # Now test the filtering
                print(f"\n🧪 Testing API filtering...")
                filtered_response = requests.get(
                    f"{API_BASE}/transactions?month=6&year=2025",
                    headers=self.get_auth_headers(),
                    timeout=15
                )
                
                if filtered_response.status_code == 200:
                    filtered_transactions = filtered_response.json()
                    print(f"  API returned: {len(filtered_transactions)} transactions")
                    
                    if len(filtered_transactions) != len(july_2025_transactions):
                        print(f"  ❌ MISMATCH: Expected {len(july_2025_transactions)}, got {len(filtered_transactions)}")
                        
                        # Show what the API returned
                        print(f"\n  API returned transactions:")
                        for t in filtered_transactions:
                            print(f"    - ₹{t.get('amount')} - {t.get('description')} - {t.get('date')}")
                        
                        # Show what we expected
                        print(f"\n  Expected transactions:")
                        for t in july_2025_transactions:
                            print(f"    - ₹{t.get('amount')} - {t.get('description')} - {t.get('date')}")
                    else:
                        print(f"  ✅ Filtering working correctly")
                else:
                    print(f"  ❌ Filtered API failed: {filtered_response.status_code}")
                    
            else:
                print(f"❌ Could not get transactions: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error analyzing dates: {e}")

    def test_date_filtering_logic(self):
        """Test the date filtering logic manually"""
        print("\n🧪 Testing Date Filtering Logic...")
        print("=" * 80)
        
        # Test the date range calculation
        month = 6  # July (0-indexed)
        year = 2025
        
        # This is what the backend should be doing
        actual_month = month + 1  # Convert to 1-indexed (7 for July)
        start_date = datetime(year, actual_month, 1)  # 2025-07-01
        end_date = datetime(year, actual_month + 1, 1)  # 2025-08-01
        
        print(f"Frontend sends: month={month}, year={year}")
        print(f"Backend converts to: actual_month={actual_month}")
        print(f"Date range: {start_date} <= date < {end_date}")
        
        # Test some sample dates
        test_dates = [
            "2025-07-01T00:00:00",
            "2025-07-15T10:30:00",
            "2025-07-20T14:45:00",
            "2025-07-27T00:00:00",
            "2025-07-31T23:59:59",
            "2025-08-01T00:00:00",  # Should be excluded
        ]
        
        print(f"\nTesting sample dates:")
        for date_str in test_dates:
            try:
                test_date = datetime.fromisoformat(date_str)
                in_range = start_date <= test_date < end_date
                print(f"  {date_str}: {'✅ IN RANGE' if in_range else '❌ OUT OF RANGE'}")
            except Exception as e:
                print(f"  {date_str}: ❌ PARSE ERROR: {e}")

    def run_analysis(self):
        """Run the complete analysis"""
        print("🔍 Database Transaction Analysis")
        print("=" * 80)
        
        if not self.authenticate_user():
            print("❌ Could not authenticate. Aborting analysis.")
            return False
        
        self.analyze_transaction_dates()
        self.test_date_filtering_logic()
        
        return True

if __name__ == "__main__":
    analyzer = DatabaseAnalyzer()
    analyzer.run_analysis()