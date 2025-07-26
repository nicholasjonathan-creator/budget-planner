#!/usr/bin/env python3
"""
Debug Date Validation - Targeted Analysis
This script will help identify exactly why date validation is failing
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://45029e2d-ce68-4057-a50f-b6a3f9f23132.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_specific_failing_cases():
    """Test the specific cases that are failing date validation"""
    
    failing_cases = [
        {
            "sms": "Dear Customer, Rs 1000.00 debited from your account XX0003 on 26-Aug-2025.",
            "expected_to_fail": True,
            "description": "Generic pattern with future date",
            "expected_parsing_method": "generic"
        },
        {
            "sms": "UPDATE: INR 750.00 debited from HDFC Bank XX2953 on 01-SEP-25. Info: Test transaction",
            "expected_to_fail": True,
            "description": "HDFC UPDATE pattern with future date",
            "expected_parsing_method": "hdfc_specific"
        },
        {
            "sms": "Hi! Your txn of ₹400.00 at Future Store on your Scapia Federal Bank credit card was successful",
            "expected_to_fail": True,
            "description": "Scapia pattern (uses current date fallback)",
            "expected_parsing_method": "scapia_specific"
        },
        {
            "sms": "Dear Customer, Rs 2000.00 debited from your account XX0003 on 26-Jul-2023.",
            "expected_to_fail": True,
            "description": "Generic pattern with past date",
            "expected_parsing_method": "generic"
        },
        {
            "sms": "UPDATE: INR 1200.00 debited from HDFC Bank XX2953 on 15-JAN-23. Info: Old transaction",
            "expected_to_fail": True,
            "description": "HDFC UPDATE pattern with past date",
            "expected_parsing_method": "hdfc_specific"
        }
    ]
    
    print("🔍 Debug Analysis: Date Validation Failures")
    print("=" * 60)
    
    for i, case in enumerate(failing_cases, 1):
        print(f"\n--- Debug Case {i}: {case['description']} ---")
        print(f"SMS: {case['sms']}")
        print(f"Expected to fail: {case['expected_to_fail']}")
        print(f"Expected parsing method: {case['expected_parsing_method']}")
        
        try:
            # Send SMS to parser endpoint
            response = requests.post(
                f"{API_BASE}/sms/receive",
                json={
                    "phone_number": "+918000000000",
                    "message": case['sms']
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                parsing_successful = result.get('success', False)
                
                print(f"Parsing result: {'SUCCESS' if parsing_successful else 'FAILED'}")
                
                if parsing_successful:
                    transaction_id = result.get('transaction_id')
                    print(f"🚨 CRITICAL: SMS should have failed but was parsed successfully!")
                    print(f"   Transaction ID: {transaction_id}")
                    
                    # Get transaction details to see what parsing method was used
                    if transaction_id:
                        try:
                            tx_response = requests.get(f"{API_BASE}/transactions/{transaction_id}", timeout=5)
                            if tx_response.status_code == 200:
                                tx_data = tx_response.json()
                                raw_data = tx_data.get('raw_data', {})
                                parsing_method = raw_data.get('parsing_method', 'unknown')
                                bank = raw_data.get('bank', 'unknown')
                                
                                print(f"   Actual parsing method: {parsing_method}")
                                print(f"   Bank detected: {bank}")
                                print(f"   Transaction date: {tx_data.get('date', 'N/A')}")
                                print(f"   Amount: ₹{tx_data.get('amount', 0):,.2f}")
                                
                                # Check if parsing method matches expectation
                                if parsing_method != case['expected_parsing_method']:
                                    print(f"   ⚠️  Parsing method mismatch! Expected: {case['expected_parsing_method']}, Got: {parsing_method}")
                                
                        except Exception as e:
                            print(f"   Error getting transaction details: {e}")
                else:
                    print(f"✅ SMS failed parsing as expected")
                    print(f"   Reason: {result.get('message', 'Unknown')}")
                    
            else:
                print(f"❌ SMS receive endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing SMS: {e}")
    
    print(f"\n📋 Analysis Summary:")
    print("The main issues appear to be:")
    print("1. Generic parsing method bypasses date validation (uses datetime.now() directly)")
    print("2. Some HDFC patterns may not be calling _parse_date properly")
    print("3. Scapia patterns use current date fallback, bypassing validation")
    print("4. Exception handling might be catching ValueError from date validation")

def test_date_parsing_directly():
    """Test date parsing logic directly by examining the patterns"""
    print(f"\n🔍 Direct Date Parsing Analysis")
    print("=" * 40)
    
    # Test dates that should fail
    test_dates = [
        ("26-Aug-2025", "Future date - should fail"),
        ("01-SEP-25", "Future date DD-MMM-YY - should fail"),
        ("15/12/25", "Future date DD/MM/YY - should fail"),
        ("26-Jul-2023", "Past date - should fail"),
        ("15-JAN-23", "Past date DD-MMM-YY - should fail"),
        ("25/07/25", "Valid current date - should pass"),
        ("25-JUL-25", "Valid current date DD-MMM-YY - should pass")
    ]
    
    print("Testing date parsing patterns:")
    for date_str, description in test_dates:
        print(f"  {date_str} ({description})")
        # We can't test _parse_date directly from here, but we can see the patterns
    
    print(f"\nThe issue is likely in the SMS parsing flow where:")
    print("1. Generic patterns don't extract dates from SMS text")
    print("2. They fall back to datetime.now() instead of parsing SMS date")
    print("3. This bypasses the smart date validation entirely")

if __name__ == "__main__":
    test_specific_failing_cases()
    test_date_parsing_directly()