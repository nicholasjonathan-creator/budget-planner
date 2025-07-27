#!/usr/bin/env python3
"""
Transaction Filtering Investigation for Available Users
Focus: Check if the SMS transaction filtering bug exists with current users
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fe5a1b17-dacb-468f-a395-f044dbe77291.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Available test users
TEST_USERS = [
    {"email": "testuser@example.com", "password": "testpassword123"},
    {"email": "admin@example.com", "password": "admin123"},
]

class TransactionInvestigator:
    def __init__(self):
        self.results = []
        
    def authenticate_user(self, email, password):
        """Authenticate a user"""
        try:
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                return {
                    "token": login_data.get("access_token"),
                    "user_id": login_data.get("user", {}).get("id"),
                    "email": email
                }
            return None
        except Exception as e:
            print(f"❌ Error authenticating {email}: {e}")
            return None

    def get_auth_headers(self, token):
        """Get authentication headers"""
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def investigate_user_transactions(self, user_info):
        """Investigate transactions for a specific user"""
        print(f"\n🔍 Investigating transactions for: {user_info['email']}")
        print(f"   User ID: {user_info['user_id']}")
        print("-" * 60)
        
        try:
            # Get all transactions
            response = requests.get(
                f"{API_BASE}/transactions",
                headers=self.get_auth_headers(user_info['token']),
                timeout=15
            )
            
            if response.status_code == 200:
                all_transactions = response.json()
                print(f"✅ Total transactions: {len(all_transactions)}")
                
                if len(all_transactions) == 0:
                    print("   No transactions found for this user")
                    return
                
                # Analyze by source
                sources = {}
                dates = {}
                
                for txn in all_transactions:
                    source = txn.get('source', 'unknown')
                    date = txn.get('date', '')[:7]  # YYYY-MM format
                    amount = txn.get('amount', 0)
                    
                    if source not in sources:
                        sources[source] = []
                    sources[source].append(amount)
                    
                    if date not in dates:
                        dates[date] = []
                    dates[date].append({'source': source, 'amount': amount})
                
                print(f"   Sources found: {list(sources.keys())}")
                
                # Check for SMS transactions
                sms_sources = [s for s in sources.keys() if 'sms' in s.lower()]
                if sms_sources:
                    print(f"   🚨 SMS transactions found: {sms_sources}")
                    for source in sms_sources:
                        amounts = sources[source]
                        print(f"     {source}: {len(amounts)} transactions, amounts: {[f'₹{amt:.2f}' for amt in amounts[:5]]}")
                else:
                    print("   ℹ️  No SMS transactions found")
                
                # Test specific month filtering (July 2025 = month 6 in 0-indexed)
                print(f"\n   Testing month filtering for July 2025...")
                
                # Test different month parameters
                for month_param in [6, 7]:  # Test both 6 and 7 to see which is correct
                    filter_response = requests.get(
                        f"{API_BASE}/transactions?month={month_param}&year=2025",
                        headers=self.get_auth_headers(user_info['token']),
                        timeout=15
                    )
                    
                    if filter_response.status_code == 200:
                        filtered_transactions = filter_response.json()
                        print(f"     month={month_param}: {len(filtered_transactions)} transactions")
                        
                        if filtered_transactions:
                            filtered_sources = {}
                            for txn in filtered_transactions:
                                source = txn.get('source', 'unknown')
                                filtered_sources[source] = filtered_sources.get(source, 0) + 1
                            print(f"       Sources: {filtered_sources}")
                    else:
                        print(f"     month={month_param}: API error {filter_response.status_code}")
                
                # Check if there are any 2025 transactions
                transactions_2025 = [txn for txn in all_transactions if '2025' in txn.get('date', '')]
                if transactions_2025:
                    print(f"\n   2025 transactions: {len(transactions_2025)}")
                    for txn in transactions_2025[:5]:  # Show first 5
                        print(f"     ₹{txn.get('amount', 0):.2f} | {txn.get('source', 'unknown')} | {txn.get('date', 'N/A')}")
                
            else:
                print(f"❌ Failed to get transactions: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error investigating transactions: {e}")

    def create_test_sms_transaction(self, user_info):
        """Create a test SMS transaction to verify filtering"""
        print(f"\n🧪 Creating test SMS transaction for: {user_info['email']}")
        
        try:
            # Create a test transaction with SMS source
            test_transaction = {
                "type": "expense",
                "category_id": 1,
                "amount": 999.99,
                "description": "Test SMS Transaction for Filtering Bug Investigation",
                "date": "2025-07-15T10:00:00Z",
                "source": "sms",
                "merchant": "Test Bank SMS",
                "account_number": "TEST1234",
                "currency": "INR"
            }
            
            response = requests.post(
                f"{API_BASE}/transactions",
                json=test_transaction,
                headers=self.get_auth_headers(user_info['token']),
                timeout=15
            )
            
            if response.status_code == 200:
                created_txn = response.json()
                print(f"✅ Test SMS transaction created: {created_txn.get('id')}")
                
                # Now test if it appears in filtered results
                filter_response = requests.get(
                    f"{API_BASE}/transactions?month=6&year=2025",
                    headers=self.get_auth_headers(user_info['token']),
                    timeout=15
                )
                
                if filter_response.status_code == 200:
                    filtered_transactions = filter_response.json()
                    test_txn_found = any(txn.get('id') == created_txn.get('id') for txn in filtered_transactions)
                    
                    if test_txn_found:
                        print("✅ Test SMS transaction appears in filtered results - No filtering bug")
                    else:
                        print("❌ Test SMS transaction MISSING from filtered results - BUG CONFIRMED!")
                        print("   This confirms the SMS transaction filtering bug exists")
                        
                        # Check if it appears in all transactions
                        all_response = requests.get(
                            f"{API_BASE}/transactions",
                            headers=self.get_auth_headers(user_info['token']),
                            timeout=15
                        )
                        
                        if all_response.status_code == 200:
                            all_transactions = all_response.json()
                            test_txn_in_all = any(txn.get('id') == created_txn.get('id') for txn in all_transactions)
                            
                            if test_txn_in_all:
                                print("   ✅ Test transaction exists in database (appears in /transactions)")
                                print("   ❌ But missing from filtered results (/transactions?month=6&year=2025)")
                                print("   🚨 CRITICAL BUG: SMS transactions are filtered out incorrectly")
                                return "BUG_CONFIRMED"
                            else:
                                print("   ❌ Test transaction not found anywhere - creation may have failed")
                                return "CREATION_FAILED"
                        else:
                            print("   ❌ Could not verify transaction in database")
                            return "VERIFICATION_FAILED"
                    
                    return "NO_BUG" if test_txn_found else "BUG_CONFIRMED"
                else:
                    print(f"❌ Could not test filtering: {filter_response.status_code}")
                    return "FILTER_TEST_FAILED"
            else:
                print(f"❌ Failed to create test transaction: {response.status_code}")
                print(f"   Response: {response.text}")
                return "CREATION_FAILED"
                
        except Exception as e:
            print(f"❌ Error creating test SMS transaction: {e}")
            return "ERROR"

    def run_investigation(self):
        """Run complete investigation"""
        print("🔍 TRANSACTION FILTERING BUG INVESTIGATION")
        print("=" * 80)
        print("Investigating SMS transaction filtering issue with available users")
        print("=" * 80)
        
        bug_found = False
        
        for user_creds in TEST_USERS:
            user_info = self.authenticate_user(user_creds["email"], user_creds["password"])
            
            if user_info:
                print(f"\n✅ Authenticated: {user_info['email']}")
                
                # Investigate existing transactions
                self.investigate_user_transactions(user_info)
                
                # Create test SMS transaction to verify filtering
                test_result = self.create_test_sms_transaction(user_info)
                
                if test_result == "BUG_CONFIRMED":
                    bug_found = True
                    print(f"\n🚨 BUG CONFIRMED for user: {user_info['email']}")
                elif test_result == "NO_BUG":
                    print(f"\n✅ No filtering bug found for user: {user_info['email']}")
                else:
                    print(f"\n⚠️  Test inconclusive for user: {user_info['email']} - {test_result}")
                    
            else:
                print(f"\n❌ Could not authenticate: {user_creds['email']}")
        
        # Final assessment
        print("\n" + "=" * 80)
        print("🏁 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        if bug_found:
            print("🚨 CRITICAL BUG CONFIRMED: SMS transaction filtering issue exists")
            print("   Issue: SMS source transactions are missing from month-filtered API responses")
            print("   Impact: Users cannot see all their transactions for specific months")
            print("   Action Required: Fix TransactionService.get_transactions method")
            return False
        else:
            print("✅ No SMS transaction filtering bug found with current test setup")
            print("   Either the bug has been fixed or doesn't affect the test users")
            return True

if __name__ == "__main__":
    print("🔍 Transaction Filtering Bug Investigation")
    print("=" * 80)
    
    investigator = TransactionInvestigator()
    success = investigator.run_investigation()
    
    if success:
        print("\n✅ Investigation completed - No critical bugs found")
        sys.exit(0)
    else:
        print("\n❌ Investigation found critical bugs")
        sys.exit(1)