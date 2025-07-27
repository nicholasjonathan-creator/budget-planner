#!/usr/bin/env python3
"""
Transaction API Testing for nicholasjonathan@gmail.com
Testing the specific issue where frontend calls /api/transactions?month=6&year=2025 
but only sees one transaction when database contains 2 transactions (₹1394.82 and ₹150.00)
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://4e36ad4f-0605-4e84-966c-86dfbb141256.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user as specified in review request
TEST_USER = {
    "email": "nicholasjonathan@gmail.com",
    "password": "password123"  # Assuming standard test password
}

class TransactionAPITester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.auth_token = None
        self.user_id = None
        
    def test_health_check(self):
        """Test if the backend is running"""
        print("🔍 Testing Backend Health...")
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is healthy")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False

    def authenticate_user(self):
        """Authenticate the specific test user nicholasjonathan@gmail.com"""
        print(f"\n🔐 Authenticating User: {TEST_USER['email']}...")
        
        try:
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": TEST_USER["email"],
                    "password": TEST_USER["password"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.auth_token = login_data.get("access_token")
                self.user_id = login_data.get("user", {}).get("id")
                print(f"✅ User authenticated successfully: {TEST_USER['email']}")
                print(f"   User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Failed to authenticate user: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return False
                    
        except Exception as e:
            print(f"❌ Error authenticating user: {e}")
            return False

    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    def test_transactions_with_month_year_filter(self):
        """Test GET /api/transactions?month=6&year=2025 - the specific issue"""
        print("\n🧪 Testing Transactions API with Month/Year Filter (month=6, year=2025)...")
        print("=" * 70)
        
        self.total_tests += 1
        
        try:
            # Test the specific API call mentioned in the review
            response = requests.get(
                f"{API_BASE}/transactions?month=6&year=2025",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                transactions = response.json()
                print(f"✅ Transactions API responded successfully")
                print(f"   Total transactions returned: {len(transactions)}")
                
                # Check for the specific transactions mentioned in the review
                expected_amounts = [1394.82, 150.00]
                found_amounts = []
                
                for transaction in transactions:
                    amount = transaction.get('amount', 0)
                    transaction_type = transaction.get('type', 'unknown')
                    date = transaction.get('date', 'unknown')
                    description = transaction.get('description', 'unknown')
                    
                    print(f"   Transaction: ₹{amount} ({transaction_type}) - {description} - {date}")
                    
                    # Check if this matches our expected amounts
                    if abs(amount - 1394.82) < 0.01:
                        found_amounts.append(1394.82)
                    elif abs(amount - 150.00) < 0.01:
                        found_amounts.append(150.00)
                
                print(f"\n   Expected transactions: ₹{expected_amounts[0]} and ₹{expected_amounts[1]}")
                print(f"   Found matching transactions: {found_amounts}")
                
                if len(found_amounts) == 2:
                    print("✅ Both expected transactions found!")
                    self.passed_tests += 1
                elif len(found_amounts) == 1:
                    print("⚠️  Only 1 of 2 expected transactions found - this matches the reported issue!")
                    print("   This confirms the frontend issue where only one transaction is visible")
                    self.failed_tests += 1
                else:
                    print("❌ Neither expected transaction found")
                    self.failed_tests += 1
                    
            elif response.status_code == 401:
                print("❌ Authentication failed - check JWT token")
                self.failed_tests += 1
            else:
                print(f"❌ Transactions API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing transactions API with filters: {e}")
            self.failed_tests += 1

    def test_transactions_without_filters(self):
        """Test GET /api/transactions without month/year parameters"""
        print("\n🧪 Testing Transactions API without Filters (all transactions)...")
        print("=" * 70)
        
        self.total_tests += 1
        
        try:
            response = requests.get(
                f"{API_BASE}/transactions",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                transactions = response.json()
                print(f"✅ Transactions API responded successfully")
                print(f"   Total transactions returned: {len(transactions)}")
                
                # Look for our specific transactions in all data
                expected_amounts = [1394.82, 150.00]
                found_amounts = []
                july_2025_transactions = []
                
                for transaction in transactions:
                    amount = transaction.get('amount', 0)
                    transaction_type = transaction.get('type', 'unknown')
                    date = transaction.get('date', 'unknown')
                    description = transaction.get('description', 'unknown')
                    
                    # Check if this is a July 2025 transaction
                    if '2025-07' in str(date) or '2025-08' in str(date):  # July is month 7, but 0-indexed would be 6
                        july_2025_transactions.append(transaction)
                        print(f"   July 2025 Transaction: ₹{amount} ({transaction_type}) - {description} - {date}")
                    
                    # Check if this matches our expected amounts
                    if abs(amount - 1394.82) < 0.01:
                        found_amounts.append(1394.82)
                    elif abs(amount - 150.00) < 0.01:
                        found_amounts.append(150.00)
                
                print(f"\n   July 2025 transactions found: {len(july_2025_transactions)}")
                print(f"   Expected amounts found in all data: {found_amounts}")
                
                if len(found_amounts) == 2:
                    print("✅ Both expected transactions exist in database!")
                    if len(july_2025_transactions) >= 2:
                        print("✅ Both transactions appear to be in July 2025 timeframe")
                    self.passed_tests += 1
                else:
                    print(f"❌ Only {len(found_amounts)} of 2 expected transactions found in database")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Transactions API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing transactions API without filters: {e}")
            self.failed_tests += 1

    def test_monthly_summary_api(self):
        """Test GET /api/analytics/monthly-summary for July 2025 (month=6, year=2025)"""
        print("\n🧪 Testing Monthly Summary API for July 2025...")
        print("=" * 70)
        
        self.total_tests += 1
        
        try:
            response = requests.get(
                f"{API_BASE}/analytics/monthly-summary?month=6&year=2025",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                summary = response.json()
                print(f"✅ Monthly Summary API responded successfully")
                
                income = summary.get('income', 0)
                expense = summary.get('expense', 0)
                balance = summary.get('balance', 0)
                
                print(f"   Income: ₹{income:,.2f}")
                print(f"   Expense: ₹{expense:,.2f}")
                print(f"   Balance: ₹{balance:,.2f}")
                
                # Check if the summary reflects our expected transactions
                expected_total = 1394.82 + 150.00  # ₹1544.82
                
                # The transactions could be income or expense, so check both
                if abs(income - expected_total) < 0.01 or abs(expense - expected_total) < 0.01:
                    print(f"✅ Monthly summary reflects expected transaction total: ₹{expected_total}")
                    self.passed_tests += 1
                elif abs(income - 1394.82) < 0.01 or abs(expense - 1394.82) < 0.01:
                    print(f"⚠️  Monthly summary only reflects ₹1394.82 - missing ₹150.00 transaction")
                    print("   This suggests the filtering issue affects the summary as well")
                    self.failed_tests += 1
                else:
                    print(f"⚠️  Monthly summary doesn't match expected amounts")
                    print(f"   Expected total: ₹{expected_total}, but got Income: ₹{income}, Expense: ₹{expense}")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Monthly Summary API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing monthly summary API: {e}")
            self.failed_tests += 1

    def test_different_month_year_combinations(self):
        """Test different month/year combinations to isolate the filtering issue"""
        print("\n🧪 Testing Different Month/Year Combinations...")
        print("=" * 70)
        
        self.total_tests += 1
        
        test_combinations = [
            (5, 2025),   # June 2025 (0-indexed)
            (6, 2025),   # July 2025 (0-indexed) - the problematic one
            (7, 2025),   # August 2025 (0-indexed)
            (6, 2024),   # July 2024 (0-indexed)
        ]
        
        results = {}
        
        for month, year in test_combinations:
            try:
                response = requests.get(
                    f"{API_BASE}/transactions?month={month}&year={year}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    transactions = response.json()
                    results[f"{month}/{year}"] = len(transactions)
                    print(f"   Month {month}, Year {year}: {len(transactions)} transactions")
                else:
                    results[f"{month}/{year}"] = f"Error {response.status_code}"
                    print(f"   Month {month}, Year {year}: Error {response.status_code}")
                    
            except Exception as e:
                results[f"{month}/{year}"] = f"Exception: {e}"
                print(f"   Month {month}, Year {year}: Exception: {e}")
        
        # Analyze results
        july_2025_count = results.get("6/2025", 0)
        if isinstance(july_2025_count, int):
            if july_2025_count == 1:
                print(f"\n⚠️  Confirmed: July 2025 (month=6) returns only 1 transaction")
                print("   This matches the reported frontend issue")
                self.failed_tests += 1
            elif july_2025_count == 2:
                print(f"\n✅ July 2025 (month=6) correctly returns 2 transactions")
                self.passed_tests += 1
            else:
                print(f"\n❓ July 2025 (month=6) returns {july_2025_count} transactions (unexpected)")
                self.failed_tests += 1
        else:
            print(f"\n❌ July 2025 (month=6) API call failed: {july_2025_count}")
            self.failed_tests += 1

    def test_transaction_service_directly(self):
        """Test if we can identify any patterns in the transaction data"""
        print("\n🧪 Analyzing Transaction Data Patterns...")
        print("=" * 70)
        
        self.total_tests += 1
        
        try:
            # Get all transactions to analyze patterns
            response = requests.get(
                f"{API_BASE}/transactions",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                transactions = response.json()
                print(f"✅ Retrieved {len(transactions)} total transactions for analysis")
                
                # Analyze transaction patterns
                date_patterns = {}
                amount_patterns = {}
                source_patterns = {}
                
                for transaction in transactions:
                    # Date analysis
                    date = transaction.get('date', 'unknown')
                    if date != 'unknown':
                        date_key = date[:7] if len(str(date)) >= 7 else str(date)  # YYYY-MM format
                        date_patterns[date_key] = date_patterns.get(date_key, 0) + 1
                    
                    # Amount analysis
                    amount = transaction.get('amount', 0)
                    if amount in [1394.82, 150.00]:
                        amount_patterns[amount] = amount_patterns.get(amount, 0) + 1
                    
                    # Source analysis
                    source = transaction.get('source', 'unknown')
                    source_patterns[source] = source_patterns.get(source, 0) + 1
                
                print(f"\n   Date Distribution:")
                for date, count in sorted(date_patterns.items()):
                    print(f"     {date}: {count} transactions")
                
                print(f"\n   Expected Amount Analysis:")
                for amount, count in amount_patterns.items():
                    print(f"     ₹{amount}: {count} occurrences")
                
                print(f"\n   Source Distribution:")
                for source, count in source_patterns.items():
                    print(f"     {source}: {count} transactions")
                
                # Check if both expected amounts exist
                if 1394.82 in amount_patterns and 150.00 in amount_patterns:
                    print(f"\n✅ Both expected transactions (₹1394.82 and ₹150.00) exist in database")
                    self.passed_tests += 1
                else:
                    print(f"\n❌ Missing expected transactions in database")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Could not retrieve transactions for analysis: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error analyzing transaction patterns: {e}")
            self.failed_tests += 1

    def run_all_tests(self):
        """Run all transaction API tests"""
        print("🚀 Starting Transaction API Testing for nicholasjonathan@gmail.com")
        print("Focus: /api/transactions filtering issue with month=6&year=2025")
        print("=" * 80)
        
        # Test backend health first
        if not self.test_health_check():
            print("❌ Backend is not accessible. Aborting tests.")
            return False
        
        # Authenticate user
        if not self.authenticate_user():
            print("❌ Could not authenticate test user. Aborting tests.")
            return False
        
        # Run all transaction API tests
        self.test_transactions_with_month_year_filter()
        self.test_transactions_without_filters()
        self.test_monthly_summary_api()
        self.test_different_month_year_combinations()
        self.test_transaction_service_directly()
        
        # Print final results
        self.print_final_results()
        
        return self.failed_tests == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 TRANSACTION API TEST RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: Transaction API is working correctly!")
            elif success_rate >= 75:
                print("👍 GOOD: Transaction API is mostly working with minor issues")
            elif success_rate >= 50:
                print("⚠️  MODERATE: Transaction API has some issues that need attention")
            else:
                print("❌ POOR: Transaction API has significant issues")
        
        print("\n📋 Test Summary:")
        print("  🎯 Primary Issue: /api/transactions?month=6&year=2025 filtering")
        print("  📊 Expected: 2 transactions (₹1394.82 and ₹150.00) for nicholasjonathan@gmail.com")
        print("  🔍 Tested: Month/year filtering, unfiltered queries, monthly summaries")
        print("  📈 Analysis: Transaction patterns, date distributions, source analysis")
        
        print("=" * 80)

if __name__ == "__main__":
    print("🧪 Transaction API Testing for nicholasjonathan@gmail.com")
    print("=" * 80)
    
    tester = TransactionAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Transaction API is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the results above.")
        sys.exit(1)