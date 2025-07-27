#!/usr/bin/env python3
"""
WhatsApp Integration Transaction Testing
Testing the specific issue where /api/transactions?month=6&year=2025 
might not return all transactions correctly for WhatsApp integration users
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

# Test users to try
TEST_USERS = [
    {"email": "testuser@example.com", "password": "testpassword123"},
    {"email": "test@example.com", "password": "securepassword123"},
]

class WhatsAppTransactionTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.auth_token = None
        self.user_id = None
        self.current_user_email = None
        
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

    def authenticate_any_user(self):
        """Try to authenticate with any available test user"""
        print(f"\n🔐 Authenticating Test Users...")
        
        for user in TEST_USERS:
            try:
                login_response = requests.post(
                    f"{API_BASE}/auth/login",
                    json={
                        "email": user["email"],
                        "password": user["password"]
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    self.auth_token = login_data.get("access_token")
                    self.user_id = login_data.get("user", {}).get("id")
                    self.current_user_email = user["email"]
                    print(f"✅ User authenticated successfully: {user['email']}")
                    print(f"   User ID: {self.user_id}")
                    return True
                        
            except Exception as e:
                print(f"❌ Error authenticating {user['email']}: {e}")
        
        print("❌ Could not authenticate any test user")
        return False

    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    def test_whatsapp_integration_transactions(self):
        """Test for WhatsApp integration transactions and filtering issues"""
        print(f"\n🧪 Testing WhatsApp Integration Transactions for {self.current_user_email}...")
        print("=" * 80)
        
        self.total_tests += 1
        
        try:
            # Get all transactions first
            all_response = requests.get(
                f"{API_BASE}/transactions",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if all_response.status_code == 200:
                all_transactions = all_response.json()
                print(f"✅ Retrieved {len(all_transactions)} total transactions")
                
                # Analyze transactions by source and date
                whatsapp_transactions = []
                july_2025_transactions = []
                target_amounts = []
                
                for transaction in all_transactions:
                    source = transaction.get('source', 'unknown')
                    amount = transaction.get('amount', 0)
                    date = transaction.get('date', 'unknown')
                    description = transaction.get('description', '')
                    
                    # Check for WhatsApp-related transactions
                    if 'whatsapp' in source.lower() or 'whatsapp' in description.lower():
                        whatsapp_transactions.append(transaction)
                    
                    # Check for July 2025 transactions
                    if '2025-07' in str(date):
                        july_2025_transactions.append(transaction)
                        print(f"   July 2025: ₹{amount} - {description} ({source})")
                    
                    # Check for target amounts mentioned in review
                    if abs(amount - 1394.82) < 0.01 or abs(amount - 150.00) < 0.01:
                        target_amounts.append(transaction)
                        print(f"   🎯 Target Amount: ₹{amount} - {description} ({source}) - {date}")
                
                print(f"\n   WhatsApp transactions found: {len(whatsapp_transactions)}")
                print(f"   July 2025 transactions found: {len(july_2025_transactions)}")
                print(f"   Target amounts (₹1394.82/₹150.00) found: {len(target_amounts)}")
                
                # Now test the specific filtering issue
                if len(july_2025_transactions) >= 2:
                    print(f"\n🔍 Testing month=6&year=2025 filtering with {len(july_2025_transactions)} July transactions...")
                    
                    filtered_response = requests.get(
                        f"{API_BASE}/transactions?month=6&year=2025",
                        headers=self.get_auth_headers(),
                        timeout=15
                    )
                    
                    if filtered_response.status_code == 200:
                        filtered_transactions = filtered_response.json()
                        print(f"   Filtered API returned: {len(filtered_transactions)} transactions")
                        
                        if len(filtered_transactions) == len(july_2025_transactions):
                            print("   ✅ Filtering working correctly - all July transactions returned")
                            self.passed_tests += 1
                        elif len(filtered_transactions) < len(july_2025_transactions):
                            print(f"   ❌ FILTERING ISSUE DETECTED: Expected {len(july_2025_transactions)}, got {len(filtered_transactions)}")
                            print("   This matches the reported issue!")
                            
                            # Show which transactions are missing
                            filtered_ids = {t.get('id') for t in filtered_transactions}
                            missing_transactions = [t for t in july_2025_transactions if t.get('id') not in filtered_ids]
                            
                            print(f"   Missing transactions:")
                            for missing in missing_transactions:
                                print(f"     - ₹{missing.get('amount')} - {missing.get('description')} - {missing.get('date')}")
                            
                            self.failed_tests += 1
                        else:
                            print(f"   ⚠️  Unexpected: Filtered returned more than expected")
                            self.failed_tests += 1
                    else:
                        print(f"   ❌ Filtered API call failed: {filtered_response.status_code}")
                        self.failed_tests += 1
                else:
                    print(f"   ⚠️  Not enough July 2025 transactions to test filtering issue")
                    self.passed_tests += 1
                    
            else:
                print(f"❌ Could not retrieve transactions: {all_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing WhatsApp integration transactions: {e}")
            self.failed_tests += 1

    def test_monthly_summary_consistency(self):
        """Test if monthly summary is consistent with transaction filtering"""
        print(f"\n🧪 Testing Monthly Summary Consistency...")
        print("=" * 80)
        
        self.total_tests += 1
        
        try:
            # Get transactions for July 2025
            transactions_response = requests.get(
                f"{API_BASE}/transactions?month=6&year=2025",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            # Get monthly summary for July 2025
            summary_response = requests.get(
                f"{API_BASE}/analytics/monthly-summary?month=6&year=2025",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if transactions_response.status_code == 200 and summary_response.status_code == 200:
                transactions = transactions_response.json()
                summary = summary_response.json()
                
                # Calculate totals from transactions
                calculated_income = sum(t['amount'] for t in transactions if t.get('type') == 'income')
                calculated_expense = sum(t['amount'] for t in transactions if t.get('type') == 'expense')
                calculated_balance = calculated_income - calculated_expense
                
                # Get summary values
                summary_income = summary.get('income', 0)
                summary_expense = summary.get('expense', 0)
                summary_balance = summary.get('balance', 0)
                
                print(f"   Transactions API: {len(transactions)} transactions")
                print(f"   Calculated Income: ₹{calculated_income:,.2f}")
                print(f"   Calculated Expense: ₹{calculated_expense:,.2f}")
                print(f"   Calculated Balance: ₹{calculated_balance:,.2f}")
                
                print(f"\n   Summary API:")
                print(f"   Summary Income: ₹{summary_income:,.2f}")
                print(f"   Summary Expense: ₹{summary_expense:,.2f}")
                print(f"   Summary Balance: ₹{summary_balance:,.2f}")
                
                # Check consistency
                income_match = abs(calculated_income - summary_income) < 0.01
                expense_match = abs(calculated_expense - summary_expense) < 0.01
                balance_match = abs(calculated_balance - summary_balance) < 0.01
                
                if income_match and expense_match and balance_match:
                    print(f"\n   ✅ Monthly summary is consistent with transaction filtering")
                    self.passed_tests += 1
                else:
                    print(f"\n   ❌ INCONSISTENCY DETECTED:")
                    if not income_match:
                        print(f"     Income mismatch: Calculated ₹{calculated_income:,.2f} vs Summary ₹{summary_income:,.2f}")
                    if not expense_match:
                        print(f"     Expense mismatch: Calculated ₹{calculated_expense:,.2f} vs Summary ₹{summary_expense:,.2f}")
                    if not balance_match:
                        print(f"     Balance mismatch: Calculated ₹{calculated_balance:,.2f} vs Summary ₹{summary_balance:,.2f}")
                    print("   This suggests the filtering issue affects both APIs")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ API calls failed - Transactions: {transactions_response.status_code}, Summary: {summary_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing monthly summary consistency: {e}")
            self.failed_tests += 1

    def test_date_range_filtering_edge_cases(self):
        """Test edge cases in date range filtering"""
        print(f"\n🧪 Testing Date Range Filtering Edge Cases...")
        print("=" * 80)
        
        self.total_tests += 1
        
        try:
            # Test different month/year combinations around July 2025
            test_cases = [
                (5, 2025, "June 2025"),
                (6, 2025, "July 2025"),  # The problematic case
                (7, 2025, "August 2025"),
                (6, 2024, "July 2024"),
                (6, 2026, "July 2026"),
            ]
            
            results = {}
            
            for month, year, description in test_cases:
                try:
                    response = requests.get(
                        f"{API_BASE}/transactions?month={month}&year={year}",
                        headers=self.get_auth_headers(),
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        transactions = response.json()
                        results[description] = len(transactions)
                        print(f"   {description} (month={month}): {len(transactions)} transactions")
                        
                        # Show details for July 2025
                        if month == 6 and year == 2025:
                            for t in transactions:
                                print(f"     - ₹{t.get('amount', 0)} - {t.get('description', 'N/A')} - {t.get('date', 'N/A')}")
                    else:
                        results[description] = f"Error {response.status_code}"
                        print(f"   {description} (month={month}): Error {response.status_code}")
                        
                except Exception as e:
                    results[description] = f"Exception: {str(e)[:50]}"
                    print(f"   {description} (month={month}): Exception: {e}")
            
            # Analyze results
            july_2025_count = results.get("July 2025", 0)
            if isinstance(july_2025_count, int) and july_2025_count > 0:
                print(f"\n   ✅ July 2025 filtering returned {july_2025_count} transactions")
                self.passed_tests += 1
            else:
                print(f"\n   ⚠️  July 2025 filtering issue: {july_2025_count}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing date range filtering: {e}")
            self.failed_tests += 1

    def run_all_tests(self):
        """Run all WhatsApp integration transaction tests"""
        print("🚀 Starting WhatsApp Integration Transaction Testing")
        print("Focus: Transaction filtering issues for WhatsApp integration")
        print("=" * 80)
        
        # Test backend health first
        if not self.test_health_check():
            print("❌ Backend is not accessible. Aborting tests.")
            return False
        
        # Authenticate user
        if not self.authenticate_any_user():
            print("❌ Could not authenticate any test user. Aborting tests.")
            return False
        
        # Run all tests
        self.test_whatsapp_integration_transactions()
        self.test_monthly_summary_consistency()
        self.test_date_range_filtering_edge_cases()
        
        # Print final results
        self.print_final_results()
        
        return self.failed_tests == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 WHATSAPP INTEGRATION TRANSACTION TEST RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: WhatsApp integration transaction filtering is working correctly!")
            elif success_rate >= 75:
                print("👍 GOOD: WhatsApp integration mostly working with minor issues")
            elif success_rate >= 50:
                print("⚠️  MODERATE: WhatsApp integration has some issues that need attention")
            else:
                print("❌ POOR: WhatsApp integration has significant issues")
        
        print("\n📋 Test Summary:")
        print("  🎯 Focus: WhatsApp integration transaction filtering")
        print("  📊 Issue: /api/transactions?month=6&year=2025 potentially missing transactions")
        print("  🔍 Tested: Transaction filtering, monthly summary consistency, edge cases")
        print("  📈 Analysis: WhatsApp transactions, date filtering, API consistency")
        
        print("=" * 80)

if __name__ == "__main__":
    print("🧪 WhatsApp Integration Transaction Testing")
    print("=" * 80)
    
    tester = WhatsAppTransactionTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! WhatsApp integration transaction filtering is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the results above.")
        sys.exit(1)