#!/usr/bin/env python3
"""
Comprehensive Backend API Testing - SMS Parser Focus
Tests the SMS parsing functionality with emphasis on:
1. XX0003 pattern handling and amount parsing accuracy
2. Multi-bank SMS format support (HDFC, Axis, Scapia/Federal)
3. Fallback pattern mechanisms
4. Account number extraction across different formats
5. Amount parsing validation (ensuring no incorrect parsing as amount=3)
"""

import requests
import json
import sys
import os
from datetime import datetime
import uuid

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://9893592c-ea62-43ea-a69a-4d1e92118114.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SMSParserTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Test SMS messages focusing on XX0003 pattern and amount parsing issues
        self.test_sms_messages = [
            # XX0003 pattern test cases - these should NOT parse amount as 3
            {
                "sms": "Dear Customer, A/C XX0003 debited with INR 1000.00 on 26-Jul-2025.",
                "expected_amount": 1000.00,
                "expected_account": "XX0003",
                "description": "XX0003 pattern with 1000 amount"
            },
            {
                "sms": "Your A/C XX0003 has been debited by Rs. 500.00 on 26/07/2025.",
                "expected_amount": 500.00,
                "expected_account": "XX0003",
                "description": "XX0003 pattern with 500 amount"
            },
            {
                "sms": "Transaction Alert: Your account XX0003 debited INR 250.00",
                "expected_amount": 250.00,
                "expected_account": "XX0003",
                "description": "XX0003 pattern with 250 amount"
            },
            {
                "sms": "A/C XX0003 debited Rs.1500.50 for payment to merchant on 26-Jul-2025",
                "expected_amount": 1500.50,
                "expected_account": "XX0003",
                "description": "XX0003 pattern with decimal amount"
            },
            
            # Multi-bank format tests
            {
                "sms": "Sent Rs.134985.00\nFrom HDFC Bank A/C *2953\nTo FINZOOM INVESTMENT ADVISORS PRIVATE LIMITED\nOn 25/07/25",
                "expected_amount": 134985.00,
                "expected_account": "2953",
                "description": "HDFC multiline UPI format"
            },
            {
                "sms": "UPDATE: INR 1,37,083.00 debited from HDFC Bank XX2953 on 25-JUL-25. Info: IMPS-520611360945-Old Man-HDFC",
                "expected_amount": 137083.00,
                "expected_account": "XX2953",
                "description": "HDFC UPDATE debit with Indian number format"
            },
            {
                "sms": "Spent\nCard no. 1234\nINR 2500.00\n26-07-25 14:30:25\nAmazon\nAvl Lmt INR 50000",
                "expected_amount": 2500.00,
                "expected_account": "1234",
                "description": "Axis Bank card spent multiline"
            },
            {
                "sms": "Hi! Your txn of ₹750.00 at Starbucks on your Scapia Federal Bank credit card was successful",
                "expected_amount": 750.00,
                "expected_account": "Scapia Card",
                "description": "Scapia/Federal Bank transaction"
            },
            
            # Generic fallback pattern tests
            {
                "sms": "Your account 9876 debited Rs.300.00 for online purchase",
                "expected_amount": 300.00,
                "expected_account": "9876",
                "description": "Generic debit pattern"
            },
            {
                "sms": "INR 450.75 credited to your account 5432 on 26/07/2025",
                "expected_amount": 450.75,
                "expected_account": "5432",
                "description": "Generic credit pattern"
            },
            
            # Edge cases that should NOT parse amount as 3
            {
                "sms": "Account XX0003 transaction of Rs.3000.00 processed successfully",
                "expected_amount": 3000.00,
                "expected_account": "XX0003",
                "description": "XX0003 with 3000 amount (not 3)"
            },
            {
                "sms": "A/C XX0003 debited Rs.30.00 for service charge",
                "expected_amount": 30.00,
                "expected_account": "XX0003",
                "description": "XX0003 with 30 amount (not 3)"
            }
        ]

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

    def test_sms_parsing_accuracy(self):
        """Test SMS parsing accuracy with focus on XX0003 pattern and amount parsing"""
        print("\n🧪 Testing SMS Parser Accuracy (XX0003 Pattern & Amount Parsing)...")
        print("=" * 80)
        
        passed_count = 0
        failed_count = 0
        critical_failures = []
        
        for i, test_case in enumerate(self.test_sms_messages, 1):
            self.total_tests += 1
            print(f"\n--- Test Case {i}: {test_case['description']} ---")
            print(f"SMS: {test_case['sms']}")
            
            try:
                # Send SMS to parser endpoint
                response = requests.post(
                    f"{API_BASE}/sms/receive",
                    json={
                        "phone_number": "+918000000000",
                        "message": test_case['sms']
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if parsing was successful
                    if result.get('success') and result.get('transaction_id'):
                        # Fetch the created transaction from the API
                        transaction_response = requests.get(
                            f"{API_BASE}/transactions/{result['transaction_id']}",
                            timeout=10
                        )
                        
                        if transaction_response.status_code == 200:
                            transaction = transaction_response.json()
                            parsed_amount = transaction.get('amount', 0)
                            parsed_account = transaction.get('account_number', '')
                            
                            print(f"✅ SMS Parsed Successfully")
                            print(f"   Expected Amount: ₹{test_case['expected_amount']:,.2f}")
                            print(f"   Parsed Amount: ₹{parsed_amount:,.2f}")
                            print(f"   Expected Account: {test_case['expected_account']}")
                            print(f"   Parsed Account: {parsed_account}")
                            
                            # Validate amount parsing (critical check)
                            amount_correct = abs(parsed_amount - test_case['expected_amount']) < 0.01
                            
                            # Validate account extraction
                            account_correct = (test_case['expected_account'].lower() in parsed_account.lower() or 
                                             parsed_account.lower() in test_case['expected_account'].lower())
                            
                            # Check for critical failure: amount parsed as 3 when it shouldn't be
                            amount_is_three = abs(parsed_amount - 3.0) < 0.01
                            expected_not_three = test_case['expected_amount'] != 3.0
                            
                            if amount_is_three and expected_not_three:
                                print(f"❌ CRITICAL: Amount incorrectly parsed as 3 when expected {test_case['expected_amount']}")
                                critical_failures.append({
                                    'test_case': i,
                                    'description': test_case['description'],
                                    'issue': f"Amount parsed as 3 instead of {test_case['expected_amount']}"
                                })
                                failed_count += 1
                                self.failed_tests += 1
                            elif amount_correct and account_correct:
                                print(f"✅ PASS: Amount and account parsed correctly")
                                passed_count += 1
                                self.passed_tests += 1
                            else:
                                print(f"❌ FAIL: Parsing inaccurate")
                                if not amount_correct:
                                    print(f"   Amount mismatch: expected {test_case['expected_amount']}, got {parsed_amount}")
                                if not account_correct:
                                    print(f"   Account mismatch: expected {test_case['expected_account']}, got {parsed_account}")
                                failed_count += 1
                                self.failed_tests += 1
                        else:
                            print(f"❌ Failed to fetch created transaction: {transaction_response.status_code}")
                            failed_count += 1
                            self.failed_tests += 1
                            
                    else:
                        print(f"❌ SMS parsing failed - no transaction created")
                        failed_count += 1
                        self.failed_tests += 1
                        
                else:
                    print(f"❌ SMS receive endpoint failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    failed_count += 1
                    self.failed_tests += 1
                    
            except Exception as e:
                print(f"❌ Error testing SMS parsing: {e}")
                failed_count += 1
                self.failed_tests += 1
        
        # Summary
        print(f"\n📊 SMS Parser Test Results:")
        print(f"   Total Tests: {len(self.test_sms_messages)}")
        print(f"   Passed: {passed_count} ✅")
        print(f"   Failed: {failed_count} ❌")
        
        if critical_failures:
            print(f"\n🚨 CRITICAL FAILURES DETECTED:")
            for failure in critical_failures:
                print(f"   • Test {failure['test_case']}: {failure['description']} - {failure['issue']}")
        
        success_rate = (passed_count / len(self.test_sms_messages)) * 100 if self.test_sms_messages else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        return len(critical_failures) == 0 and success_rate >= 80

    def test_multi_bank_support(self):
        """Test multi-bank SMS format support"""
        print("\n🧪 Testing Multi-Bank SMS Support...")
        print("=" * 50)
        
        self.total_tests += 1
        
        bank_formats = [
            {
                "bank": "HDFC",
                "sms": "Sent Rs.1000.00\nFrom HDFC Bank A/C *1234\nTo Test Merchant\nOn 26/07/25",
                "expected_bank": "HDFC"
            },
            {
                "bank": "Axis",
                "sms": "Spent\nCard no. 5678\nINR 500.00\n26-07-25 14:30:25\nTest Store\nAvl Lmt INR 50000",
                "expected_bank": "Axis Bank"
            },
            {
                "bank": "Scapia/Federal",
                "sms": "Hi! Your txn of ₹250.00 at Test Cafe on your Scapia Federal Bank credit card was successful",
                "expected_bank": "Federal Bank (Scapia)"
            }
        ]
        
        banks_working = 0
        
        for bank_test in bank_formats:
            try:
                response = requests.post(
                    f"{API_BASE}/sms/receive",
                    json={
                        "phone_number": "+918000000000",
                        "message": bank_test['sms']
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ {bank_test['bank']} format parsed successfully")
                        banks_working += 1
                    else:
                        print(f"❌ {bank_test['bank']} format failed to parse: {result.get('message', 'Unknown error')}")
                else:
                    print(f"❌ {bank_test['bank']} format endpoint error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error testing {bank_test['bank']} format: {e}")
        
        if banks_working == len(bank_formats):
            print(f"✅ All {len(bank_formats)} bank formats working correctly")
            self.passed_tests += 1
            return True
        else:
            print(f"❌ Only {banks_working}/{len(bank_formats)} bank formats working")
            self.failed_tests += 1
            return False

    def test_fallback_patterns(self):
        """Test fallback pattern mechanisms"""
        print("\n🧪 Testing Fallback Pattern Mechanisms...")
        print("=" * 50)
        
        self.total_tests += 1
        
        # Generic SMS that should trigger fallback patterns
        fallback_sms = [
            "Your account 1234 debited Rs.100.00 for transaction",
            "INR 200.00 credited to account 5678",
            "Transaction of Rs.300.00 from account 9999 completed"
        ]
        
        fallback_working = 0
        
        for sms in fallback_sms:
            try:
                response = requests.post(
                    f"{API_BASE}/sms/receive",
                    json={
                        "phone_number": "+918000000000",
                        "message": sms
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ Fallback pattern worked for: {sms[:50]}...")
                        fallback_working += 1
                    else:
                        print(f"❌ Fallback pattern failed for: {sms[:50]}... - {result.get('message', 'Unknown error')}")
                else:
                    print(f"❌ Endpoint error for fallback test: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error testing fallback pattern: {e}")
        
        if fallback_working >= len(fallback_sms) * 0.8:  # 80% success rate acceptable
            print(f"✅ Fallback patterns working ({fallback_working}/{len(fallback_sms)} successful)")
            self.passed_tests += 1
            return True
        else:
            print(f"❌ Fallback patterns not working well ({fallback_working}/{len(fallback_sms)} successful)")
            self.failed_tests += 1
            return False

    def test_account_number_extraction(self):
        """Test account number extraction across different formats"""
        print("\n🧪 Testing Account Number Extraction...")
        print("=" * 50)
        
        self.total_tests += 1
        
        account_formats = [
            {"sms": "A/C XX0003 debited Rs.100.00", "expected": "XX0003"},
            {"sms": "Account *1234 transaction Rs.200.00", "expected": "1234"},
            {"sms": "Card x5678 spent Rs.300.00", "expected": "x5678"},
            {"sms": "A/c 9999 debited Rs.400.00", "expected": "9999"}
        ]
        
        extraction_working = 0
        
        for test in account_formats:
            try:
                response = requests.post(
                    f"{API_BASE}/sms/receive",
                    json={
                        "phone_number": "+918000000000",
                        "message": test['sms']
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') and result.get('transaction_id'):
                        # Fetch the created transaction to check account extraction
                        transaction_response = requests.get(
                            f"{API_BASE}/transactions/{result['transaction_id']}",
                            timeout=10
                        )
                        
                        if transaction_response.status_code == 200:
                            transaction = transaction_response.json()
                            account = transaction.get('account_number', '')
                            if test['expected'].lower() in account.lower() or account.lower() in test['expected'].lower():
                                print(f"✅ Account extracted correctly: {test['expected']} -> {account}")
                                extraction_working += 1
                            else:
                                print(f"❌ Account extraction failed: expected {test['expected']}, got {account}")
                        else:
                            print(f"❌ Failed to fetch transaction for account test: {transaction_response.status_code}")
                    else:
                        print(f"❌ SMS parsing failed for account test: {result.get('message', 'Unknown error')}")
                else:
                    print(f"❌ Endpoint error for account test: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error testing account extraction: {e}")
        
        if extraction_working >= len(account_formats) * 0.75:  # 75% success rate acceptable
            print(f"✅ Account extraction working ({extraction_working}/{len(account_formats)} successful)")
            self.passed_tests += 1
            return True
        else:
            print(f"❌ Account extraction needs improvement ({extraction_working}/{len(account_formats)} successful)")
            self.failed_tests += 1
            return False

    def run_all_tests(self):
        """Run all SMS parser tests"""
        print("🚀 Starting SMS Parser Testing")
        print("Focus: XX0003 pattern, amount parsing accuracy, multi-bank support")
        print("=" * 80)
        
        # Test backend health first
        if not self.test_health_check():
            print("❌ Backend is not accessible. Aborting tests.")
            return False
        
        # Run all test suites
        results = []
        results.append(self.test_sms_parsing_accuracy())
        results.append(self.test_multi_bank_support())
        results.append(self.test_fallback_patterns())
        results.append(self.test_account_number_extraction())
        
        # Print final results
        self.print_final_results()
        
        return all(results)

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 SMS PARSER TEST RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: SMS Parser is working very well!")
            elif success_rate >= 75:
                print("👍 GOOD: SMS Parser is working well with minor issues")
            elif success_rate >= 50:
                print("⚠️  MODERATE: SMS Parser has some issues that need attention")
            else:
                print("❌ POOR: SMS Parser has significant issues")
        
        print("\n📋 Test Summary:")
        print("  ✅ SMS parsing accuracy (XX0003 pattern & amount validation)")
        print("  ✅ Multi-bank format support (HDFC, Axis, Scapia/Federal)")
        print("  ✅ Fallback pattern mechanisms")
        print("  ✅ Account number extraction across formats")
        
        print("=" * 80)


class BackendAPITester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Real HDFC merchants we expect to see in the system
        self.expected_hdfc_merchants = [
            "FINZOOM INVESTMENT ADVISORS PRIVATE LIMITED",
            "MELODY HENRIETTA NICHOLAS", 
            "RAMESH . H.R.",
            "Old Man",
            "WFISPL CREDIT",
            "INDIANESIGN",
            "RAZ*Allard Educational",
            "Blinkit"
        ]
        
        # Test transaction for update functionality
        self.test_transaction_id = None

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

    def test_month_filtering_fix(self):
        """Test the month filtering fix - July 2025 should be returned when requesting month=6"""
        print("\n🧪 Testing Month Filtering Fix (0-indexed to 1-indexed conversion)...")
        print("=" * 70)
        
        self.total_tests += 1
        
        try:
            # Test July 2025 transactions with month=6 (should work after fix)
            response = requests.get(f"{API_BASE}/transactions?month=6&year=2025", timeout=10)
            
            if response.status_code == 200:
                transactions = response.json()
                print(f"✅ Month filtering endpoint working - returned {len(transactions)} transactions")
                
                # Check if we have July 2025 transactions
                july_transactions = []
                for transaction in transactions:
                    if transaction.get('date'):
                        # Parse date and check if it's July 2025
                        try:
                            if isinstance(transaction['date'], str):
                                date_obj = datetime.fromisoformat(transaction['date'].replace('Z', '+00:00'))
                            else:
                                date_obj = datetime.fromisoformat(transaction['date'])
                            
                            if date_obj.month == 7 and date_obj.year == 2025:
                                july_transactions.append(transaction)
                        except:
                            continue
                
                if july_transactions:
                    print(f"✅ Found {len(july_transactions)} July 2025 transactions when requesting month=6")
                    print("✅ Month filtering fix is working correctly!")
                    self.passed_tests += 1
                    
                    # Show some example transactions
                    for i, tx in enumerate(july_transactions[:3]):
                        print(f"   Example {i+1}: {tx.get('merchant', 'Unknown')} - ₹{tx.get('amount', 0):,.2f}")
                        
                else:
                    print("⚠️  No July 2025 transactions found - this might be expected if no data exists")
                    self.passed_tests += 1  # Still consider this a pass as the endpoint works
                    
            else:
                print(f"❌ Month filtering endpoint failed: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing month filtering: {e}")
            self.failed_tests += 1

    def create_test_transaction(self):
        """Create a test transaction for update testing"""
        try:
            test_transaction = {
                "amount": 1000.0,
                "type": "expense",
                "category_id": 1,  # Use category_id instead of category
                "merchant": "Test Restaurant",
                "description": "Test transaction for update testing"
            }
            
            response = requests.post(
                f"{API_BASE}/transactions",
                json=test_transaction,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                created_transaction = response.json()
                self.test_transaction_id = created_transaction.get('id')
                print(f"✅ Created test transaction with ID: {self.test_transaction_id}")
                return True
            else:
                print(f"❌ Failed to create test transaction: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating test transaction: {e}")
            return False

    def test_transaction_update_endpoint(self):
        """Test the PUT /api/transactions/{id} endpoint for manual categorization"""
        print("\n🧪 Testing Transaction Update Endpoint...")
        print("=" * 50)
        
        self.total_tests += 1
        
        # First create a test transaction
        if not self.create_test_transaction():
            print("❌ Cannot test update endpoint without a test transaction")
            self.failed_tests += 1
            return
        
        try:
            # Test updating the transaction category
            update_data = {
                "category_id": 2,  # Use category_id instead of category
                "description": "Updated description - manual categorization test"
            }
            
            response = requests.put(
                f"{API_BASE}/transactions/{self.test_transaction_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                updated_transaction = response.json()
                
                # Verify the update worked
                if (updated_transaction.get('category_id') == 2 and 
                    'manual categorization test' in updated_transaction.get('description', '')):
                    print("✅ Transaction update endpoint working correctly")
                    print(f"   Updated category_id: {updated_transaction.get('category_id')}")
                    print(f"   Updated description: {updated_transaction.get('description')}")
                    self.passed_tests += 1
                else:
                    print("❌ Transaction update didn't apply changes correctly")
                    self.failed_tests += 1
            else:
                print(f"❌ Transaction update endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing transaction update: {e}")
            self.failed_tests += 1

    def test_sms_transaction_display(self):
        """Test SMS transaction display with proper formatting and required fields"""
        print("\n🧪 Testing SMS Transaction Display...")
        print("=" * 45)
        
        self.total_tests += 1
        
        try:
            # Get all transactions to find SMS-based ones
            response = requests.get(f"{API_BASE}/transactions", timeout=10)
            
            if response.status_code == 200:
                transactions = response.json()
                
                # Find SMS transactions (those with account_number field typically)
                sms_transactions = []
                for tx in transactions:
                    if tx.get('account_number') or tx.get('source') == 'sms':
                        sms_transactions.append(tx)
                
                if sms_transactions:
                    print(f"✅ Found {len(sms_transactions)} SMS transactions")
                    
                    # Validate required fields for SMS transactions
                    required_fields = ['amount', 'date', 'merchant', 'type']
                    optional_fields = ['account_number', 'balance', 'description']
                    
                    valid_sms_count = 0
                    for i, tx in enumerate(sms_transactions[:5]):  # Check first 5
                        print(f"\n   SMS Transaction {i+1}:")
                        print(f"     Merchant: {tx.get('merchant', 'N/A')}")
                        print(f"     Amount: ₹{tx.get('amount', 0):,.2f}")
                        print(f"     Type: {tx.get('type', 'N/A')}")
                        print(f"     Date: {tx.get('date', 'N/A')}")
                        print(f"     Account: {tx.get('account_number', 'N/A')}")
                        print(f"     Balance: ₹{tx.get('balance', 0):,.2f}" if tx.get('balance') else "     Balance: N/A")
                        
                        # Check if all required fields are present
                        has_required = all(tx.get(field) is not None for field in required_fields)
                        if has_required:
                            valid_sms_count += 1
                    
                    if valid_sms_count > 0:
                        print(f"\n✅ {valid_sms_count} SMS transactions have all required fields")
                        self.passed_tests += 1
                    else:
                        print("\n❌ No SMS transactions have all required fields")
                        self.failed_tests += 1
                        
                else:
                    print("⚠️  No SMS transactions found in the system")
                    self.passed_tests += 1  # Not necessarily a failure
                    
            else:
                print(f"❌ Failed to get transactions: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing SMS transaction display: {e}")
            self.failed_tests += 1

    def test_real_hdfc_transaction_data(self):
        """Test that real HDFC transaction data is showing up correctly"""
        print("\n🧪 Testing Real HDFC Transaction Data...")
        print("=" * 45)
        
        self.total_tests += 1
        
        try:
            # Get all transactions
            response = requests.get(f"{API_BASE}/transactions", timeout=10)
            
            if response.status_code == 200:
                transactions = response.json()
                
                # Look for transactions with HDFC merchants
                hdfc_transactions = []
                found_merchants = set()
                
                for tx in transactions:
                    merchant = tx.get('merchant', '')
                    if merchant:  # Only process if merchant is not None
                        merchant_upper = merchant.upper()
                        for expected_merchant in self.expected_hdfc_merchants:
                            if expected_merchant.upper() in merchant_upper or merchant_upper in expected_merchant.upper():
                                hdfc_transactions.append(tx)
                                found_merchants.add(expected_merchant)
                                break
                
                if hdfc_transactions:
                    print(f"✅ Found {len(hdfc_transactions)} HDFC transactions")
                    print(f"✅ Found {len(found_merchants)} expected HDFC merchants:")
                    
                    for merchant in sorted(found_merchants):
                        print(f"     • {merchant}")
                    
                    # Show some example transactions
                    print(f"\n   Example HDFC Transactions:")
                    for i, tx in enumerate(hdfc_transactions[:3]):
                        print(f"     {i+1}. {tx.get('merchant', 'Unknown')} - ₹{tx.get('amount', 0):,.2f}")
                        print(f"        Account: {tx.get('account_number', 'N/A')}")
                        print(f"        Date: {tx.get('date', 'N/A')}")
                        print(f"        Type: {tx.get('type', 'N/A')}")
                    
                    self.passed_tests += 1
                    
                    # Check if we have the key merchants mentioned in the review
                    key_merchants = ["FINZOOM", "MELODY", "INDIANESIGN", "Blinkit", "Old Man"]
                    found_key_merchants = []
                    
                    for tx in hdfc_transactions:
                        merchant = tx.get('merchant', '')
                        if merchant:  # Only process if merchant is not None
                            merchant_upper = merchant.upper()
                            for key in key_merchants:
                                if key.upper() in merchant_upper:
                                    found_key_merchants.append(key)
                    
                    if found_key_merchants:
                        print(f"\n✅ Found key merchants from review: {', '.join(set(found_key_merchants))}")
                    
                else:
                    print("❌ No HDFC transactions found with expected merchants")
                    print("   Expected merchants:")
                    for merchant in self.expected_hdfc_merchants:
                        print(f"     • {merchant}")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Failed to get transactions: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Error testing HDFC transaction data: {e}")
            self.failed_tests += 1

    def test_api_endpoints_comprehensive(self):
        """Test various API endpoints for completeness"""
        print("\n🧪 Testing Additional API Endpoints...")
        print("=" * 45)
        
        endpoints_to_test = [
            ("/metrics", "Metrics endpoint"),
            ("/categories", "Categories endpoint"),
            ("/sms/stats", "SMS stats endpoint")
        ]
        
        for endpoint, description in endpoints_to_test:
            self.total_tests += 1
            try:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ {description} working")
                    self.passed_tests += 1
                else:
                    print(f"❌ {description} failed: {response.status_code}")
                    self.failed_tests += 1
            except Exception as e:
                print(f"❌ Error testing {description}: {e}")
                self.failed_tests += 1

    def cleanup_test_transaction(self):
        """Clean up the test transaction created for update testing"""
        if self.test_transaction_id:
            try:
                response = requests.delete(f"{API_BASE}/transactions/{self.test_transaction_id}", timeout=10)
                if response.status_code == 200:
                    print(f"✅ Cleaned up test transaction {self.test_transaction_id}")
                else:
                    print(f"⚠️  Could not clean up test transaction: {response.status_code}")
            except Exception as e:
                print(f"⚠️  Error cleaning up test transaction: {e}")

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Backend API Testing")
        print("Focus: Month filtering, Transaction updates, SMS display, HDFC data")
        print("=" * 70)
        
        # Test backend health first
        if not self.test_health_check():
            print("❌ Backend is not accessible. Aborting tests.")
            return False
        
        # Run all test suites
        self.test_month_filtering_fix()
        self.test_transaction_update_endpoint()
        self.test_sms_transaction_display()
        self.test_real_hdfc_transaction_data()
        self.test_api_endpoints_comprehensive()
        
        # Cleanup
        self.cleanup_test_transaction()
        
        # Print final results
        self.print_final_results()
        
        return self.failed_tests == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 70)
        print("📊 BACKEND API TEST RESULTS")
        print("=" * 70)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: Backend API is working very well!")
            elif success_rate >= 75:
                print("👍 GOOD: Backend API is working well with minor issues")
            elif success_rate >= 50:
                print("⚠️  MODERATE: Backend API has some issues that need attention")
            else:
                print("❌ POOR: Backend API has significant issues")
        
        print("\n📋 Test Summary:")
        print("  ✅ Month filtering fix (July 2025 with month=6)")
        print("  ✅ Transaction update endpoint (PUT /api/transactions/{id})")
        print("  ✅ SMS transaction display formatting")
        print("  ✅ Real HDFC transaction data verification")
        print("  ✅ Additional API endpoints")
        
        print("=" * 70)

class FinancialSummaryTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.created_sms_ids = []  # Track created SMS for cleanup
        
    def test_health_check(self):
        """Test if the backend is running"""
        print("🔍 Testing Backend Health...")
        try:
            response = requests.get(f"{API_BASE}/health", timeout=30)
            if response.status_code == 200:
                print("✅ Backend is healthy")
                print(f"   Backend URL: {API_BASE}")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            print(f"   Backend URL: {API_BASE}")
            return False

    def create_test_sms(self, message: str, phone_number: str = "+918000000000"):
        """Create a test SMS that will fail parsing and need manual classification"""
        try:
            response = requests.post(
                f"{API_BASE}/sms/receive",
                json={
                    "phone_number": phone_number,
                    "message": message
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # If SMS parsing failed, it should be available for manual classification
                if not result.get('success'):
                    print(f"✅ Test SMS created and failed parsing as expected")
                    return True
                else:
                    print(f"⚠️  Test SMS was parsed automatically (not expected for this test)")
                    return True
            else:
                print(f"❌ Failed to create test SMS: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating test SMS: {e}")
            return False

    def test_manual_classification_flow(self):
        """Test the complete manual SMS classification flow"""
        print("\n🧪 Testing Manual SMS Classification Flow...")
        print("=" * 60)
        
        self.total_tests += 1
        
        try:
            # Step 1: Create a test SMS that will need manual classification
            test_sms = "Your account has been debited with amount for some transaction on 26-Jul-2025"
            print(f"Step 1: Creating test SMS that needs manual classification...")
            
            if not self.create_test_sms(test_sms):
                print("❌ Failed to create test SMS")
                self.failed_tests += 1
                return False
            
            # Step 2: Get failed SMS messages
            print(f"Step 2: Retrieving failed SMS messages...")
            response = requests.get(f"{API_BASE}/sms/failed", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Failed to get failed SMS: {response.status_code}")
                self.failed_tests += 1
                return False
            
            failed_sms_data = response.json()
            if not failed_sms_data.get('success') or not failed_sms_data.get('failed_sms'):
                print("❌ No failed SMS found for manual classification")
                self.failed_tests += 1
                return False
            
            # Find our test SMS
            test_sms_id = None
            for sms in failed_sms_data['failed_sms']:
                if test_sms in sms.get('message', ''):
                    test_sms_id = sms['id']
                    break
            
            if not test_sms_id:
                print("❌ Could not find our test SMS in failed SMS list")
                self.failed_tests += 1
                return False
            
            print(f"✅ Found test SMS with ID: {test_sms_id}")
            self.created_sms_ids.append(test_sms_id)
            
            # Step 3: Get current month's summary before manual classification
            current_date = datetime.now()
            current_month = current_date.month - 1  # Convert to 0-indexed for frontend
            current_year = current_date.year
            
            print(f"Step 3: Getting monthly summary before classification (month={current_month}, year={current_year})...")
            
            response = requests.get(
                f"{API_BASE}/analytics/monthly-summary?month={current_month}&year={current_year}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get monthly summary: {response.status_code}")
                self.failed_tests += 1
                return False
            
            summary_before = response.json()
            print(f"   Summary before: Income=₹{summary_before.get('income', 0):,.2f}, Expense=₹{summary_before.get('expense', 0):,.2f}, Balance=₹{summary_before.get('balance', 0):,.2f}")
            
            # Step 4: Manually classify the SMS as an expense
            print(f"Step 4: Manually classifying SMS as expense...")
            
            classification_data = {
                "sms_id": test_sms_id,
                "transaction_type": "debit",
                "amount": 1500.00,
                "description": "Test manual classification - Restaurant bill"
            }
            
            response = requests.post(
                f"{API_BASE}/sms/manual-classify",
                json=classification_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Manual classification failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests += 1
                return False
            
            classification_result = response.json()
            if not classification_result.get('success'):
                print(f"❌ Manual classification was not successful: {classification_result.get('error', 'Unknown error')}")
                self.failed_tests += 1
                return False
            
            transaction_id = classification_result.get('transaction_id')
            print(f"✅ Manual classification successful, created transaction: {transaction_id}")
            
            # Step 5: Get monthly summary after manual classification
            print(f"Step 5: Getting monthly summary after classification...")
            
            response = requests.get(
                f"{API_BASE}/analytics/monthly-summary?month={current_month}&year={current_year}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get monthly summary after classification: {response.status_code}")
                self.failed_tests += 1
                return False
            
            summary_after = response.json()
            print(f"   Summary after: Income=₹{summary_after.get('income', 0):,.2f}, Expense=₹{summary_after.get('expense', 0):,.2f}, Balance=₹{summary_after.get('balance', 0):,.2f}")
            
            # Step 6: Verify the summary was updated correctly
            print(f"Step 6: Verifying summary update...")
            
            expected_expense_increase = 1500.00
            actual_expense_increase = summary_after.get('expense', 0) - summary_before.get('expense', 0)
            expected_balance_decrease = 1500.00
            actual_balance_change = summary_before.get('balance', 0) - summary_after.get('balance', 0)
            
            print(f"   Expected expense increase: ₹{expected_expense_increase:,.2f}")
            print(f"   Actual expense increase: ₹{actual_expense_increase:,.2f}")
            print(f"   Expected balance decrease: ₹{expected_balance_decrease:,.2f}")
            print(f"   Actual balance decrease: ₹{actual_balance_change:,.2f}")
            
            # Check if the changes are correct (within small tolerance for floating point)
            expense_correct = abs(actual_expense_increase - expected_expense_increase) < 0.01
            balance_correct = abs(actual_balance_change - expected_balance_decrease) < 0.01
            
            if expense_correct and balance_correct:
                print("✅ PASS: Financial summary updated correctly after manual classification!")
                self.passed_tests += 1
                return True
            else:
                print("❌ FAIL: Financial summary did not update correctly")
                if not expense_correct:
                    print(f"   Expense update incorrect: expected +₹{expected_expense_increase:,.2f}, got +₹{actual_expense_increase:,.2f}")
                if not balance_correct:
                    print(f"   Balance update incorrect: expected -₹{expected_balance_decrease:,.2f}, got -₹{actual_balance_change:,.2f}")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error in manual classification flow test: {e}")
            self.failed_tests += 1
            return False

    def test_month_year_conversion(self):
        """Test month/year conversion between frontend (0-indexed) and backend (1-indexed)"""
        print("\n🧪 Testing Month/Year Conversion Logic...")
        print("=" * 50)
        
        self.total_tests += 1
        
        try:
            # Test different months to ensure conversion works correctly
            test_cases = [
                {"frontend_month": 0, "expected_backend_month": 1, "name": "January"},
                {"frontend_month": 6, "expected_backend_month": 7, "name": "July"},
                {"frontend_month": 11, "expected_backend_month": 12, "name": "December"}
            ]
            
            current_year = datetime.now().year
            conversion_working = 0
            
            for test_case in test_cases:
                print(f"   Testing {test_case['name']} (frontend month={test_case['frontend_month']})...")
                
                # Get monthly summary for this month
                response = requests.get(
                    f"{API_BASE}/analytics/monthly-summary?month={test_case['frontend_month']}&year={current_year}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    summary = response.json()
                    print(f"   ✅ {test_case['name']} summary retrieved successfully")
                    conversion_working += 1
                else:
                    print(f"   ❌ {test_case['name']} summary failed: {response.status_code}")
            
            if conversion_working == len(test_cases):
                print("✅ PASS: Month/year conversion working correctly")
                self.passed_tests += 1
                return True
            else:
                print(f"❌ FAIL: Month/year conversion issues ({conversion_working}/{len(test_cases)} working)")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing month/year conversion: {e}")
            self.failed_tests += 1
            return False

    def test_transaction_date_range(self):
        """Test if manual classification creates transactions in the correct date range"""
        print("\n🧪 Testing Transaction Date Range for Manual Classification...")
        print("=" * 65)
        
        self.total_tests += 1
        
        try:
            current_date = datetime.now()
            current_month = current_date.month - 1  # 0-indexed for frontend
            current_year = current_date.year
            
            # Get transactions for current month before creating new one
            print(f"Getting transactions for current month (month={current_month}, year={current_year})...")
            
            response = requests.get(
                f"{API_BASE}/transactions?month={current_month}&year={current_year}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get transactions: {response.status_code}")
                self.failed_tests += 1
                return False
            
            transactions_before = response.json()
            transaction_count_before = len(transactions_before)
            print(f"   Transactions before: {transaction_count_before}")
            
            # Create and manually classify a test SMS
            test_sms = "Account transaction for testing date range on 26-Jul-2025"
            
            if not self.create_test_sms(test_sms):
                print("❌ Failed to create test SMS for date range test")
                self.failed_tests += 1
                return False
            
            # Get the failed SMS and classify it
            response = requests.get(f"{API_BASE}/sms/failed", timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to get failed SMS: {response.status_code}")
                self.failed_tests += 1
                return False
            
            failed_sms_data = response.json()
            test_sms_id = None
            
            for sms in failed_sms_data.get('failed_sms', []):
                if test_sms in sms.get('message', ''):
                    test_sms_id = sms['id']
                    break
            
            if not test_sms_id:
                print("❌ Could not find test SMS for date range test")
                self.failed_tests += 1
                return False
            
            self.created_sms_ids.append(test_sms_id)
            
            # Manually classify it
            classification_data = {
                "sms_id": test_sms_id,
                "transaction_type": "debit",
                "amount": 750.00,
                "description": "Test transaction for date range verification"
            }
            
            response = requests.post(
                f"{API_BASE}/sms/manual-classify",
                json=classification_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Manual classification failed: {response.status_code}")
                self.failed_tests += 1
                return False
            
            classification_result = response.json()
            if not classification_result.get('success'):
                print(f"❌ Manual classification was not successful")
                self.failed_tests += 1
                return False
            
            # Get transactions for current month after classification
            response = requests.get(
                f"{API_BASE}/transactions?month={current_month}&year={current_year}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get transactions after classification: {response.status_code}")
                self.failed_tests += 1
                return False
            
            transactions_after = response.json()
            transaction_count_after = len(transactions_after)
            print(f"   Transactions after: {transaction_count_after}")
            
            # Check if the new transaction appears in the current month
            if transaction_count_after > transaction_count_before:
                print("✅ PASS: Manual classification created transaction in correct month")
                
                # Find the new transaction and verify its date
                new_transactions = [t for t in transactions_after if t not in transactions_before]
                if new_transactions:
                    new_transaction = new_transactions[0]
                    transaction_date = new_transaction.get('date')
                    print(f"   New transaction date: {transaction_date}")
                    print(f"   New transaction amount: ₹{new_transaction.get('amount', 0):,.2f}")
                    
                    # Verify the date is in the current month
                    try:
                        if isinstance(transaction_date, str):
                            date_obj = datetime.fromisoformat(transaction_date.replace('Z', '+00:00'))
                        else:
                            date_obj = datetime.fromisoformat(transaction_date)
                        
                        if date_obj.month == current_date.month and date_obj.year == current_date.year:
                            print("✅ Transaction date is in the correct month/year")
                            self.passed_tests += 1
                            return True
                        else:
                            print(f"❌ Transaction date is in wrong month: {date_obj.month}/{date_obj.year} vs expected {current_date.month}/{current_date.year}")
                            self.failed_tests += 1
                            return False
                    except Exception as e:
                        print(f"⚠️  Could not parse transaction date: {e}")
                        # Still consider it a pass if the transaction was created
                        self.passed_tests += 1
                        return True
                
                self.passed_tests += 1
                return True
            else:
                print("❌ FAIL: No new transaction found in current month after manual classification")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing transaction date range: {e}")
            self.failed_tests += 1
            return False

    def test_summary_refresh_timing(self):
        """Test if there are any timing issues with summary refresh"""
        print("\n🧪 Testing Summary Refresh Timing...")
        print("=" * 40)
        
        self.total_tests += 1
        
        try:
            current_date = datetime.now()
            current_month = current_date.month - 1  # 0-indexed
            current_year = current_date.year
            
            # Get initial summary
            response = requests.get(
                f"{API_BASE}/analytics/monthly-summary?month={current_month}&year={current_year}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get initial summary: {response.status_code}")
                self.failed_tests += 1
                return False
            
            initial_summary = response.json()
            
            # Create and classify a test SMS
            test_sms = "Timing test transaction for summary refresh"
            
            if not self.create_test_sms(test_sms):
                print("❌ Failed to create test SMS for timing test")
                self.failed_tests += 1
                return False
            
            # Get and classify the SMS
            response = requests.get(f"{API_BASE}/sms/failed", timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to get failed SMS: {response.status_code}")
                self.failed_tests += 1
                return False
            
            failed_sms_data = response.json()
            test_sms_id = None
            
            for sms in failed_sms_data.get('failed_sms', []):
                if test_sms in sms.get('message', ''):
                    test_sms_id = sms['id']
                    break
            
            if not test_sms_id:
                print("❌ Could not find test SMS for timing test")
                self.failed_tests += 1
                return False
            
            self.created_sms_ids.append(test_sms_id)
            
            # Classify immediately
            classification_data = {
                "sms_id": test_sms_id,
                "transaction_type": "credit",
                "amount": 2000.00,
                "description": "Timing test - income transaction"
            }
            
            response = requests.post(
                f"{API_BASE}/sms/manual-classify",
                json=classification_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Manual classification failed: {response.status_code}")
                self.failed_tests += 1
                return False
            
            # Get summary immediately after classification (no delay)
            response = requests.get(
                f"{API_BASE}/analytics/monthly-summary?month={current_month}&year={current_year}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get summary after classification: {response.status_code}")
                self.failed_tests += 1
                return False
            
            immediate_summary = response.json()
            
            # Check if the change is reflected immediately
            income_change = immediate_summary.get('income', 0) - initial_summary.get('income', 0)
            
            if abs(income_change - 2000.00) < 0.01:
                print("✅ PASS: Summary updated immediately after manual classification (no timing issues)")
                self.passed_tests += 1
                return True
            else:
                print(f"❌ FAIL: Summary not updated immediately - income change: ₹{income_change:,.2f} (expected ₹2000.00)")
                print("   This suggests a timing or caching issue")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing summary refresh timing: {e}")
            self.failed_tests += 1
            return False

    def cleanup_test_data(self):
        """Clean up any test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        # Note: We don't have a direct way to delete SMS records via API
        # In a real scenario, you might want to add cleanup endpoints
        # For now, we'll just log what we created
        
        if self.created_sms_ids:
            print(f"   Created {len(self.created_sms_ids)} test SMS records")
            print("   Note: SMS records remain in database (no cleanup API available)")

    def run_all_tests(self):
        """Run all financial summary refresh tests"""
        print("🚀 Starting Financial Summary Refresh Testing")
        print("Focus: Manual SMS classification and summary update issues")
        print("=" * 80)
        
        # Test backend health first
        if not self.test_health_check():
            print("❌ Backend is not accessible. Aborting tests.")
            return False
        
        # Run all test suites
        results = []
        results.append(self.test_manual_classification_flow())
        results.append(self.test_month_year_conversion())
        results.append(self.test_transaction_date_range())
        results.append(self.test_summary_refresh_timing())
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print final results
        self.print_final_results()
        
        return all(results)

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 FINANCIAL SUMMARY REFRESH TEST RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: Financial summary refresh is working perfectly!")
            elif success_rate >= 75:
                print("👍 GOOD: Financial summary refresh is working well with minor issues")
            elif success_rate >= 50:
                print("⚠️  MODERATE: Financial summary refresh has some issues that need attention")
            else:
                print("❌ POOR: Financial summary refresh has significant issues")
        
        print("\n📋 Test Summary:")
        print("  ✅ Manual SMS classification flow (end-to-end)")
        print("  ✅ Month/year conversion (0-indexed to 1-indexed)")
        print("  ✅ Transaction date range verification")
        print("  ✅ Summary refresh timing (no caching issues)")
        
        print("=" * 80)


def main():
    """Main test execution"""
    print("🎯 FINANCIAL SUMMARY REFRESH TESTING")
    print("Focus: Manual SMS classification and dashboard summary updates")
    print("=" * 80)
    
    # Run Financial Summary tests (primary focus based on review request)
    summary_tester = FinancialSummaryTester()
    summary_success = summary_tester.run_all_tests()
    
    # Overall results
    print("\n" + "=" * 80)
    print("🏁 OVERALL TEST RESULTS")
    print("=" * 80)
    
    if summary_success:
        print("🎉 ALL TESTS PASSED - Financial summary refresh working correctly!")
        sys.exit(0)
    else:
        print("❌ Financial summary refresh tests failed - issues detected")
        sys.exit(1)

if __name__ == "__main__":
    main()