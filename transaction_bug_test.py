#!/usr/bin/env python3
"""
Critical Transaction Filtering Bug Investigation
Focus: Testing the specific issue reported for nicholasjonathan@gmail.com
where SMS source transactions are missing from API responses
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://fe5a1b17-dacb-468f-a395-f044dbe77291.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test user with the reported issue
TEST_USER = {
    "email": "nicholasjonathan@gmail.com",
    "password": "testpassword123"
}

class TransactionFilteringBugTester:
    def __init__(self):
        self.auth_token = None
        self.user_id = None
        
    def authenticate_user(self):
        """Authenticate the specific user with the reported issue"""
        print("🔐 Authenticating user with reported transaction filtering issue...")
        
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
                print(f"✅ User authenticated: {TEST_USER['email']}")
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

    def test_transaction_filtering_bug(self):
        """Test the specific transaction filtering bug for July 2025"""
        print("\n🚨 CRITICAL BUG INVESTIGATION: Transaction API Filtering Issue")
        print("=" * 70)
        print("Issue: SMS source transactions missing from /api/transactions?month=6&year=2025")
        print("Expected: 5 transactions (₹150.00, ₹1394.82, ₹1408.00, ₹500.00, ₹500.00)")
        print("Reported: Only 2 transactions returned (₹150.00, ₹1394.82)")
        print("Missing: 3 SMS transactions (₹1408.00, ₹500.00, ₹500.00)")
        print("-" * 70)
        
        try:
            # Test the specific API call that has the issue
            response = requests.get(
                f"{API_BASE}/transactions?month=6&year=2025",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                transactions = response.json()
                print(f"✅ API Response received: {len(transactions)} transactions")
                
                if len(transactions) == 0:
                    print("⚠️  No transactions found - user may not have data for July 2025")
                    return
                
                # Analyze the transactions
                print("\n📊 Transaction Analysis:")
                print("-" * 40)
                
                total_amount = 0
                sources = {}
                amounts = []
                
                for i, txn in enumerate(transactions, 1):
                    amount = txn.get('amount', 0)
                    source = txn.get('source', 'unknown')
                    description = txn.get('description', 'N/A')
                    date = txn.get('date', 'N/A')
                    
                    print(f"{i}. Amount: ₹{amount:.2f} | Source: {source} | Date: {date}")
                    print(f"   Description: {description}")
                    
                    total_amount += amount
                    sources[source] = sources.get(source, 0) + 1
                    amounts.append(amount)
                
                print("-" * 40)
                print(f"Total Amount: ₹{total_amount:.2f}")
                print(f"Sources: {sources}")
                print(f"Amounts: {[f'₹{amt:.2f}' for amt in amounts]}")
                
                # Check for the specific bug pattern
                sms_count = sources.get('sms', 0) + sources.get('sms_manual', 0)
                manual_count = sources.get('manual', 0)
                
                print(f"\n🔍 Bug Analysis:")
                print(f"SMS transactions: {sms_count}")
                print(f"Manual transactions: {manual_count}")
                print(f"Total returned: {len(transactions)}")
                
                # Expected amounts from the bug report
                expected_amounts = [150.00, 1394.82, 1408.00, 500.00, 500.00]
                returned_amounts = sorted(amounts)
                expected_amounts_sorted = sorted(expected_amounts)
                
                print(f"\nExpected amounts: {[f'₹{amt:.2f}' for amt in expected_amounts_sorted]}")
                print(f"Returned amounts: {[f'₹{amt:.2f}' for amt in returned_amounts]}")
                
                # Check if this matches the reported bug
                if len(transactions) == 2 and 150.00 in amounts and 1394.82 in amounts:
                    print("\n❌ CRITICAL BUG CONFIRMED!")
                    print("   This matches the exact pattern reported in the bug:")
                    print("   - Only 2 transactions returned instead of 5")
                    print("   - Contains ₹150.00 and ₹1394.82 (the manual transactions)")
                    print("   - Missing ₹1408.00, ₹500.00, ₹500.00 (the SMS transactions)")
                    print("   - SMS source transactions are being filtered out incorrectly")
                    return "BUG_CONFIRMED"
                elif len(transactions) == 5:
                    print("\n✅ BUG APPEARS TO BE FIXED!")
                    print("   All 5 expected transactions are now being returned")
                    return "BUG_FIXED"
                else:
                    print(f"\n⚠️  UNCLEAR RESULT:")
                    print(f"   Expected 5 transactions, got {len(transactions)}")
                    print("   This may indicate a different issue or data change")
                    return "UNCLEAR"
                    
            elif response.status_code == 401:
                print("❌ Authentication failed for transaction API")
                return "AUTH_FAILED"
            else:
                print(f"❌ Transaction API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return "API_FAILED"
                
        except Exception as e:
            print(f"❌ Error testing transaction filtering: {e}")
            return "ERROR"

    def test_all_transactions(self):
        """Get all transactions to understand the full dataset"""
        print("\n📋 Full Transaction Dataset Analysis")
        print("=" * 50)
        
        try:
            response = requests.get(
                f"{API_BASE}/transactions",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                all_transactions = response.json()
                print(f"✅ Total transactions in database: {len(all_transactions)}")
                
                if len(all_transactions) == 0:
                    print("⚠️  No transactions found for this user")
                    return
                
                # Analyze by date and source
                july_2025_transactions = []
                sources_analysis = {}
                
                for txn in all_transactions:
                    txn_date = txn.get('date', '')
                    source = txn.get('source', 'unknown')
                    amount = txn.get('amount', 0)
                    
                    # Check if it's July 2025 (month 7) or June 2025 (month 6)
                    if '2025-07' in txn_date or '2025-06' in txn_date:
                        july_2025_transactions.append(txn)
                    
                    if source not in sources_analysis:
                        sources_analysis[source] = []
                    sources_analysis[source].append(amount)
                
                print(f"\nJuly 2025 transactions found: {len(july_2025_transactions)}")
                
                if july_2025_transactions:
                    print("\nJuly 2025 Transaction Details:")
                    for i, txn in enumerate(july_2025_transactions, 1):
                        print(f"{i}. ₹{txn.get('amount', 0):.2f} | {txn.get('source', 'unknown')} | {txn.get('date', 'N/A')}")
                        print(f"   Description: {txn.get('description', 'N/A')}")
                
                print(f"\nAll Sources Analysis:")
                for source, amounts in sources_analysis.items():
                    print(f"  {source}: {len(amounts)} transactions, amounts: {[f'₹{amt:.2f}' for amt in amounts[:5]]}")
                    if len(amounts) > 5:
                        print(f"    ... and {len(amounts) - 5} more")
                
            else:
                print(f"❌ Failed to retrieve all transactions: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error analyzing all transactions: {e}")

    def run_investigation(self):
        """Run the complete investigation"""
        print("🔍 CRITICAL TRANSACTION FILTERING BUG INVESTIGATION")
        print("=" * 80)
        print("User: nicholasjonathan@gmail.com")
        print("Issue: SMS source transactions missing from API responses")
        print("API: /api/transactions?month=6&year=2025")
        print("=" * 80)
        
        # Authenticate user
        if not self.authenticate_user():
            print("❌ Cannot proceed without authentication")
            return False
        
        # Test the specific filtering bug
        bug_result = self.test_transaction_filtering_bug()
        
        # Analyze full dataset
        self.test_all_transactions()
        
        # Final assessment
        print("\n" + "=" * 80)
        print("🏁 INVESTIGATION RESULTS")
        print("=" * 80)
        
        if bug_result == "BUG_CONFIRMED":
            print("🚨 CRITICAL BUG CONFIRMED: SMS transactions are being filtered out")
            print("   Action Required: Fix TransactionService.get_transactions method")
            print("   Impact: Users cannot see all their transactions for specific months")
            return False
        elif bug_result == "BUG_FIXED":
            print("✅ BUG APPEARS TO BE FIXED: All expected transactions are returned")
            print("   Status: Transaction filtering is working correctly")
            return True
        elif bug_result == "UNCLEAR":
            print("⚠️  UNCLEAR RESULTS: Transaction count doesn't match expected pattern")
            print("   Action Required: Further investigation needed")
            return False
        else:
            print("❌ INVESTIGATION FAILED: Could not complete bug analysis")
            print(f"   Reason: {bug_result}")
            return False

if __name__ == "__main__":
    print("🔍 Critical Transaction Filtering Bug Investigation")
    print("=" * 80)
    
    tester = TransactionFilteringBugTester()
    success = tester.run_investigation()
    
    if success:
        print("\n✅ Investigation completed successfully - Bug appears to be fixed")
        sys.exit(0)
    else:
        print("\n❌ Investigation found issues - Bug confirmed or investigation failed")
        sys.exit(1)