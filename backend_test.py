#!/usr/bin/env python3
"""
Comprehensive Backend Testing for HDFC SMS Parser
Tests the improved SMS parser with real-world HDFC bank SMS formats
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://faec72d5-b1ac-459e-9b2a-3a68f118503b.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class SMSParserTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Real HDFC SMS examples from the review request
        self.real_hdfc_sms_examples = [
            {
                "name": "Multiline UPI Transfer",
                "sms": "Sent Rs.134985.00\nFrom HDFC Bank A/C *2953\nTo FINZOOM INVESTMENT ADVISORS PRIVATE LIMITED\nOn 25/07/25\nRef 520648518501\nNot You?\nCall 18002586161/SMS BLOCK UPI to 7308080808",
                "expected": {
                    "amount": 134985.00,
                    "type": "expense",
                    "payee": "FINZOOM INVESTMENT ADVISORS PRIVATE LIMITED",
                    "account": "2953"
                }
            },
            {
                "name": "UPDATE Debit with IMPS",
                "sms": "UPDATE: INR 1,37,083.00 debited from HDFC Bank XX2953 on 25-JUL-25. Info: IMPS-520611360945-Old Man-HDFC-xxxxxxxxxx5124-Rent. Avl bal:INR 3,75,261.90",
                "expected": {
                    "amount": 137083.00,
                    "type": "expense",
                    "payee": "Old Man",
                    "account": "XX2953",
                    "balance": 375261.90
                }
            },
            {
                "name": "Card Transaction",
                "sms": "Spent Rs.15065.08 From HDFC Bank Card x7722 At RAZ*Allard Educational On 2025-07-15:00:18:09 Bal Rs.25407.31 Not You? Call 18002586161/SMS BLOCK DC 7722 to 7308080808",
                "expected": {
                    "amount": 15065.08,
                    "type": "expense",
                    "payee": "RAZ*Allard Educational",
                    "account": "x7722",
                    "balance": 25407.31
                }
            },
            {
                "name": "ACH Debit",
                "sms": "UPDATE: INR 5,000.00 debited from HDFC Bank XX2953 on 01-JUL-25. Info: ACH D- TP ACH INDIANESIGN-1862188817. Avl bal:INR 2,40,315.16",
                "expected": {
                    "amount": 5000.00,
                    "type": "expense",
                    "payee": "INDIANESIGN",
                    "account": "XX2953",
                    "balance": 240315.16
                }
            },
            {
                "name": "UPDATE Credit",
                "sms": "Update! INR 4,95,865.00 deposited in HDFC Bank A/c XX2953 on 25-JUL-25 for WFISPL CREDIT.Avl bal INR 5,12,344.90. Cheque deposits in A/C are subject to clearing",
                "expected": {
                    "amount": 495865.00,
                    "type": "income",
                    "payee": "WFISPL CREDIT",
                    "account": "XX2953",
                    "balance": 512344.90
                }
            },
            {
                "name": "Multiline IMPS",
                "sms": "IMPS INR 5,000.00\nsent from HDFC Bank A/c XX2953 on 25-07-25\nTo A/c xxxxxxxxxxx1254\nRef-520611366849\nNot you?Call 18002586161/SMS BLOCK OB to 7308080808",
                "expected": {
                    "amount": 5000.00,
                    "type": "expense",
                    "account": "XX2953"
                }
            },
            {
                "name": "Simple UPI with x account format",
                "sms": "Sent Rs.549.00\nFrom HDFC Bank A/C x2953\nTo Blinkit\nOn 29/06/25\nRef 107215970082\nNot You?\nCall 18002586161/SMS BLOCK UPI to 7308080808",
                "expected": {
                    "amount": 549.00,
                    "type": "expense",
                    "payee": "Blinkit",
                    "account": "x2953"
                }
            },
            {
                "name": "Single Line UPI",
                "sms": "Sent Rs.5000.00 From HDFC Bank A/C *2953 To MELODY HENRIETTA NICHOLAS On 25/07/25 Ref 108669255361 Not You? Call 18002586161/SMS BLOCK UPI to 7308080808",
                "expected": {
                    "amount": 5000.00,
                    "type": "expense",
                    "payee": "MELODY HENRIETTA NICHOLAS",
                    "account": "2953"
                }
            }
        ]
        
        # Edge cases for testing
        self.edge_cases = [
            {
                "name": "Invalid SMS Format",
                "sms": "This is not a bank SMS message",
                "should_fail": True
            },
            {
                "name": "Empty SMS",
                "sms": "",
                "should_fail": True
            },
            {
                "name": "Partial SMS",
                "sms": "Sent Rs.100 From HDFC",
                "should_fail": True
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

    def test_sms_receive_endpoint(self, sms_text, phone_number="+918000000000"):
        """Test SMS processing through /api/sms/receive endpoint"""
        try:
            payload = {
                "phone_number": phone_number,
                "message": sms_text
            }
            
            response = requests.post(
                f"{API_BASE}/sms/receive",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ SMS receive endpoint failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error calling SMS receive endpoint: {e}")
            return None

    def test_real_hdfc_sms_examples(self):
        """Test with real HDFC SMS examples"""
        print("\n🧪 Testing Real HDFC SMS Examples...")
        print("=" * 60)
        
        for i, test_case in enumerate(self.real_hdfc_sms_examples, 1):
            self.total_tests += 1
            print(f"\n--- Test Case {i}: {test_case['name']} ---")
            print(f"SMS: {test_case['sms'][:80]}...")
            
            result = self.test_sms_receive_endpoint(test_case['sms'])
            
            if result and result.get('success'):
                print("✅ SMS processed successfully")
                
                # Get transaction details if available
                if 'transaction_id' in result:
                    transaction_details = self.get_transaction_details(result['transaction_id'])
                    if transaction_details:
                        self.validate_parsed_data(transaction_details, test_case['expected'], test_case['name'])
                    else:
                        print("⚠️  Could not retrieve transaction details")
                        self.failed_tests += 1
                else:
                    print("⚠️  No transaction ID returned")
                    self.failed_tests += 1
            else:
                print(f"❌ SMS parsing failed: {result.get('message', 'Unknown error') if result else 'No response'}")
                self.failed_tests += 1
                
            self.test_results.append({
                'test_case': test_case['name'],
                'success': result and result.get('success', False),
                'result': result
            })

    def get_transaction_details(self, transaction_id):
        """Get transaction details by ID"""
        try:
            response = requests.get(f"{API_BASE}/transactions/{transaction_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get transaction details: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting transaction details: {e}")
            return None

    def validate_parsed_data(self, transaction, expected, test_name):
        """Validate that parsed data matches expected values"""
        validation_passed = True
        
        # Check amount
        if 'amount' in expected:
            if abs(transaction.get('amount', 0) - expected['amount']) > 0.01:
                print(f"❌ Amount mismatch: Expected {expected['amount']}, got {transaction.get('amount')}")
                validation_passed = False
            else:
                print(f"✅ Amount correct: ₹{transaction.get('amount'):,.2f}")
        
        # Check transaction type
        if 'type' in expected:
            if transaction.get('type') != expected['type']:
                print(f"❌ Type mismatch: Expected {expected['type']}, got {transaction.get('type')}")
                validation_passed = False
            else:
                print(f"✅ Type correct: {transaction.get('type')}")
        
        # Check payee/merchant
        if 'payee' in expected:
            merchant = transaction.get('merchant', '')
            if expected['payee'].lower() not in merchant.lower():
                print(f"❌ Payee mismatch: Expected '{expected['payee']}', got '{merchant}'")
                validation_passed = False
            else:
                print(f"✅ Payee correct: {merchant}")
        
        # Check account number
        if 'account' in expected:
            account = transaction.get('account_number', '')
            if expected['account'] not in account:
                print(f"❌ Account mismatch: Expected '{expected['account']}', got '{account}'")
                validation_passed = False
            else:
                print(f"✅ Account correct: {account}")
        
        # Check balance
        if 'balance' in expected and expected['balance']:
            balance = transaction.get('balance')
            if balance is None:
                print(f"⚠️  Balance not extracted (expected ₹{expected['balance']:,.2f})")
            elif abs(balance - expected['balance']) > 0.01:
                print(f"❌ Balance mismatch: Expected ₹{expected['balance']:,.2f}, got ₹{balance:,.2f}")
                validation_passed = False
            else:
                print(f"✅ Balance correct: ₹{balance:,.2f}")
        
        if validation_passed:
            self.passed_tests += 1
            print(f"✅ {test_name} - All validations passed")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name} - Some validations failed")

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n🧪 Testing Edge Cases...")
        print("=" * 40)
        
        for i, test_case in enumerate(self.edge_cases, 1):
            self.total_tests += 1
            print(f"\n--- Edge Case {i}: {test_case['name']} ---")
            
            result = self.test_sms_receive_endpoint(test_case['sms'])
            
            if test_case.get('should_fail', False):
                if result and not result.get('success'):
                    print("✅ Correctly failed to parse invalid SMS")
                    self.passed_tests += 1
                else:
                    print("❌ Should have failed but didn't")
                    self.failed_tests += 1
            else:
                if result and result.get('success'):
                    print("✅ Edge case handled successfully")
                    self.passed_tests += 1
                else:
                    print("❌ Edge case failed unexpectedly")
                    self.failed_tests += 1

    def test_sms_stats_endpoint(self):
        """Test SMS statistics endpoint"""
        print("\n🧪 Testing SMS Stats Endpoint...")
        try:
            response = requests.get(f"{API_BASE}/sms/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                print("✅ SMS Stats endpoint working")
                print(f"   Total SMS: {stats.get('total_sms', 0)}")
                print(f"   Processed SMS: {stats.get('processed_sms', 0)}")
                print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
                return True
            else:
                print(f"❌ SMS Stats endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error testing SMS stats: {e}")
            return False

    def test_pattern_matching_accuracy(self):
        """Test specific pattern matching scenarios"""
        print("\n🧪 Testing Pattern Matching Accuracy...")
        print("=" * 50)
        
        pattern_tests = [
            {
                "name": "Indian Number Format",
                "sms": "UPDATE: INR 1,37,083.00 debited from HDFC Bank XX2953",
                "expected_amount": 137083.00
            },
            {
                "name": "Account Format *XXXX",
                "sms": "Sent Rs.1000.00 From HDFC Bank A/C *2953 To Test",
                "expected_account": "2953"
            },
            {
                "name": "Account Format XXXX",
                "sms": "UPDATE: INR 500.00 debited from HDFC Bank XX2953",
                "expected_account": "XX2953"
            },
            {
                "name": "Account Format xXXXX",
                "sms": "Spent Rs.100.00 From HDFC Bank Card x7722",
                "expected_account": "x7722"
            }
        ]
        
        for test in pattern_tests:
            self.total_tests += 1
            print(f"\n--- {test['name']} ---")
            
            result = self.test_sms_receive_endpoint(test['sms'])
            
            if result and result.get('success'):
                transaction_id = result.get('transaction_id')
                if transaction_id:
                    transaction = self.get_transaction_details(transaction_id)
                    if transaction:
                        # Validate specific pattern
                        if 'expected_amount' in test:
                            amount = transaction.get('amount', 0)
                            if abs(amount - test['expected_amount']) < 0.01:
                                print(f"✅ Amount pattern correct: ₹{amount:,.2f}")
                                self.passed_tests += 1
                            else:
                                print(f"❌ Amount pattern failed: Expected ₹{test['expected_amount']:,.2f}, got ₹{amount:,.2f}")
                                self.failed_tests += 1
                        
                        if 'expected_account' in test:
                            account = transaction.get('account_number', '')
                            if test['expected_account'] in account:
                                print(f"✅ Account pattern correct: {account}")
                                self.passed_tests += 1
                            else:
                                print(f"❌ Account pattern failed: Expected '{test['expected_account']}', got '{account}'")
                                self.failed_tests += 1
                    else:
                        print("❌ Could not retrieve transaction")
                        self.failed_tests += 1
                else:
                    print("❌ No transaction ID returned")
                    self.failed_tests += 1
            else:
                print("❌ SMS parsing failed")
                self.failed_tests += 1

    def run_all_tests(self):
        """Run all SMS parser tests"""
        print("🚀 Starting Comprehensive HDFC SMS Parser Testing")
        print("=" * 60)
        
        # Test backend health first
        if not self.test_health_check():
            print("❌ Backend is not accessible. Aborting tests.")
            return False
        
        # Run all test suites
        self.test_real_hdfc_sms_examples()
        self.test_edge_cases()
        self.test_pattern_matching_accuracy()
        self.test_sms_stats_endpoint()
        
        # Print final results
        self.print_final_results()
        
        return self.failed_tests == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("📊 FINAL TEST RESULTS")
        print("=" * 60)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: SMS parser is working very well!")
            elif success_rate >= 75:
                print("👍 GOOD: SMS parser is working well with minor issues")
            elif success_rate >= 50:
                print("⚠️  MODERATE: SMS parser has some issues that need attention")
            else:
                print("❌ POOR: SMS parser has significant issues")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['test_case']}")
        
        print("=" * 60)

def main():
    """Main test execution"""
    tester = SMSParserTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()