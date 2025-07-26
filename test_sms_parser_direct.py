#!/usr/bin/env python3
"""
Direct SMS Parser Testing
Test the SMS parser directly to understand parsing issues
"""

import sys
import os
sys.path.append('/app/backend')

from services.sms_parser import SMSTransactionParser

def test_sms_parser_direct():
    parser = SMSTransactionParser()
    
    # Test cases focusing on XX0003 pattern
    test_cases = [
        "Dear Customer, A/C XX0003 debited with INR 1000.00 on 26-Jul-2025.",
        "Your A/C XX0003 has been debited by Rs. 500.00 on 26/07/2025.",
        "Transaction Alert: Your account XX0003 debited INR 250.00",
        "A/C XX0003 debited Rs.1500.50 for payment to merchant on 26-Jul-2025",
        "Your account 9876 debited Rs.300.00 for online purchase",
        "INR 450.75 credited to your account 5432 on 26/07/2025",
    ]
    
    print("🧪 Direct SMS Parser Testing")
    print("=" * 50)
    
    for i, sms in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"SMS: {sms}")
        
        try:
            transaction = parser.parse_sms(sms, "+918000000000")
            
            if transaction:
                print(f"✅ PARSED SUCCESSFULLY")
                print(f"   Amount: ₹{transaction.amount:,.2f}")
                print(f"   Type: {transaction.type}")
                print(f"   Merchant: {transaction.merchant}")
                print(f"   Account: {transaction.account_number}")
                print(f"   Date: {transaction.date}")
                print(f"   Category: {transaction.category_id}")
                print(f"   Balance: ₹{transaction.balance:,.2f}" if transaction.balance else "   Balance: N/A")
                print(f"   Raw Data: {transaction.raw_data}")
            else:
                print(f"❌ FAILED TO PARSE")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    # Test fallback patterns specifically
    print(f"\n" + "=" * 50)
    print("🔍 Testing Fallback Pattern Extraction")
    print("=" * 50)
    
    test_sms = "Dear Customer, A/C XX0003 debited with INR 1000.00 on 26-Jul-2025."
    print(f"Test SMS: {test_sms}")
    
    # Test amount extraction
    transaction_type, amount = parser._extract_amount_and_type(test_sms.lower())
    print(f"Amount extraction: Type={transaction_type}, Amount={amount}")
    
    # Test account extraction
    account = parser._extract_account_number(test_sms)
    print(f"Account extraction: {account}")
    
    # Test merchant extraction
    merchant = parser._extract_merchant(test_sms)
    print(f"Merchant extraction: {merchant}")
    
    # Test balance extraction
    balance = parser._extract_balance(test_sms.lower())
    print(f"Balance extraction: {balance}")

if __name__ == "__main__":
    test_sms_parser_direct()