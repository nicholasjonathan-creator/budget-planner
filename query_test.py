#!/usr/bin/env python3
"""
Direct MongoDB Query Test
Test the exact query that should be executed by the transaction service
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8218a3b4-6b13-405a-8693-551f9e56e60c.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user
TEST_USER = {"email": "testuser@example.com", "password": "testpassword123"}

class QueryTester:
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
                print(f"   User ID: {self.user_id}")
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

    def test_different_query_approaches(self):
        """Test different ways to query the transactions"""
        print("\n🧪 Testing Different Query Approaches...")
        print("=" * 80)
        
        # Test 1: All transactions
        print("Test 1: All transactions")
        all_response = requests.get(
            f"{API_BASE}/transactions",
            headers=self.get_auth_headers(),
            timeout=15
        )
        
        if all_response.status_code == 200:
            all_transactions = all_response.json()
            july_count = sum(1 for t in all_transactions if '2025-07' in str(t.get('date', '')))
            print(f"  All transactions: {len(all_transactions)}")
            print(f"  July 2025 in all: {july_count}")
        
        # Test 2: With month/year filter
        print("\nTest 2: With month=6&year=2025 filter")
        filtered_response = requests.get(
            f"{API_BASE}/transactions?month=6&year=2025",
            headers=self.get_auth_headers(),
            timeout=15
        )
        
        if filtered_response.status_code == 200:
            filtered_transactions = filtered_response.json()
            print(f"  Filtered transactions: {len(filtered_transactions)}")
            for t in filtered_transactions:
                print(f"    - ₹{t.get('amount')} - {t.get('description')} - {t.get('date')}")
        
        # Test 3: Different month values to see if there's an off-by-one error
        print("\nTest 3: Testing different month values")
        for test_month in [5, 6, 7]:
            test_response = requests.get(
                f"{API_BASE}/transactions?month={test_month}&year=2025",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if test_response.status_code == 200:
                test_transactions = test_response.json()
                print(f"  Month {test_month}: {len(test_transactions)} transactions")
                if test_transactions:
                    for t in test_transactions[:2]:  # Show first 2
                        print(f"    - ₹{t.get('amount')} - {t.get('date')}")
            else:
                print(f"  Month {test_month}: Error {test_response.status_code}")

    def test_manual_date_filtering(self):
        """Manually filter the transactions to see what should be returned"""
        print("\n🔍 Manual Date Filtering Test...")
        print("=" * 80)
        
        # Get all transactions
        all_response = requests.get(
            f"{API_BASE}/transactions",
            headers=self.get_auth_headers(),
            timeout=15
        )
        
        if all_response.status_code == 200:
            all_transactions = all_response.json()
            
            # Manually filter for July 2025
            month = 6  # 0-indexed
            year = 2025
            actual_month = month + 1  # Convert to 1-indexed (7 for July)
            
            start_date = datetime(year, actual_month, 1)  # 2025-07-01
            end_date = datetime(year, actual_month + 1, 1)  # 2025-08-01
            
            print(f"Filtering criteria:")
            print(f"  Month (0-indexed): {month}")
            print(f"  Year: {year}")
            print(f"  Actual month (1-indexed): {actual_month}")
            print(f"  Date range: {start_date} <= date < {end_date}")
            
            manually_filtered = []
            
            for transaction in all_transactions:
                date_str = transaction.get('date', '')
                try:
                    # Parse the date
                    if isinstance(date_str, str):
                        if 'T' in date_str:
                            parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        else:
                            parsed_date = datetime.fromisoformat(date_str)
                    else:
                        parsed_date = date_str
                    
                    # Remove timezone info for comparison
                    if parsed_date.tzinfo:
                        parsed_date = parsed_date.replace(tzinfo=None)
                    
                    # Check if in range
                    if start_date <= parsed_date < end_date:
                        manually_filtered.append(transaction)
                        print(f"  ✅ MATCH: ₹{transaction.get('amount')} - {transaction.get('description')} - {date_str}")
                    else:
                        if parsed_date.year == 2025 and parsed_date.month == 7:
                            print(f"  ❓ JULY BUT NOT MATCHED: ₹{transaction.get('amount')} - {transaction.get('description')} - {date_str}")
                            print(f"     Parsed: {parsed_date}")
                            print(f"     In range check: {start_date} <= {parsed_date} < {end_date}")
                        
                except Exception as e:
                    print(f"  ❌ Date parse error for {date_str}: {e}")
            
            print(f"\nManual filtering results:")
            print(f"  Should return: {len(manually_filtered)} transactions")
            
            # Compare with API result
            api_response = requests.get(
                f"{API_BASE}/transactions?month=6&year=2025",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if api_response.status_code == 200:
                api_transactions = api_response.json()
                print(f"  API returned: {len(api_transactions)} transactions")
                
                if len(manually_filtered) != len(api_transactions):
                    print(f"  ❌ MISMATCH CONFIRMED!")
                    
                    # Find missing transactions
                    api_ids = {t.get('id') for t in api_transactions}
                    missing = [t for t in manually_filtered if t.get('id') not in api_ids]
                    
                    print(f"  Missing from API response:")
                    for t in missing:
                        print(f"    - ₹{t.get('amount')} - {t.get('description')} - {t.get('date')}")
                        print(f"      ID: {t.get('id')}")
                        print(f"      Source: {t.get('source')}")
                        print(f"      User ID: {t.get('user_id')}")
                else:
                    print(f"  ✅ Manual and API results match")

    def run_tests(self):
        """Run all tests"""
        print("🔍 Direct MongoDB Query Testing")
        print("=" * 80)
        
        if not self.authenticate_user():
            print("❌ Could not authenticate. Aborting tests.")
            return False
        
        self.test_different_query_approaches()
        self.test_manual_date_filtering()
        
        return True

if __name__ == "__main__":
    tester = QueryTester()
    tester.run_tests()