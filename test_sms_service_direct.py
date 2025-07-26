#!/usr/bin/env python3
"""
Direct SMS Service Testing
Test the SMS service directly to understand the issue
"""

import sys
import os
import asyncio
sys.path.append('/app/backend')

from services.sms_service import SMSService
from database import init_db

async def test_sms_service_direct():
    # Initialize database
    await init_db()
    
    sms_service = SMSService()
    
    # Test cases focusing on XX0003 pattern
    test_cases = [
        "Dear Customer, A/C XX0003 debited with INR 1000.00 on 26-Jul-2025.",
        "Your A/C XX0003 has been debited by Rs. 500.00 on 26/07/2025.",
        "Transaction Alert: Your account XX0003 debited INR 250.00",
    ]
    
    print("🧪 Direct SMS Service Testing")
    print("=" * 50)
    
    for i, sms in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"SMS: {sms}")
        
        try:
            result = await sms_service.receive_sms("+918000000000", sms)
            print(f"Service Result: {result}")
            
            if result.get('success') and result.get('transaction_id'):
                # Fetch the created transaction from database
                from database import db
                from bson import ObjectId
                try:
                    transaction_doc = await db.transactions.find_one({"_id": ObjectId(result['transaction_id'])})
                except:
                    # Try with string ID as well
                    transaction_doc = await db.transactions.find_one({"_id": result['transaction_id']})
                
                if transaction_doc:
                    print(f"✅ Transaction created in database:")
                    print(f"   Amount: ₹{transaction_doc.get('amount', 0):,.2f}")
                    print(f"   Type: {transaction_doc.get('type', 'N/A')}")
                    print(f"   Merchant: {transaction_doc.get('merchant', 'N/A')}")
                    print(f"   Account: {transaction_doc.get('account_number', 'N/A')}")
                    print(f"   Category: {transaction_doc.get('category_id', 'N/A')}")
                else:
                    print(f"❌ Transaction not found in database")
            else:
                print(f"❌ SMS Service failed: {result}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sms_service_direct())