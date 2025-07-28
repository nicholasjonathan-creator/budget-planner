#!/usr/bin/env python3
"""
Final Twilio Integration Test - Complete Assessment
"""

import requests
import json
import time

BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

def test_twilio_integration():
    """Complete Twilio integration test"""
    print("🔥 FINAL TWILIO INTEGRATION ASSESSMENT")
    print("=" * 60)
    
    # Test 1: Basic service health
    response = requests.get(f"{BASE_URL}/health", timeout=30)
    if response.status_code == 200:
        print("✅ Backend Service: HEALTHY")
    else:
        print("❌ Backend Service: UNHEALTHY")
        return
    
    # Test 2: WhatsApp monitoring status (no auth required)
    response = requests.get(f"{BASE_URL}/monitoring/whatsapp-status", timeout=30)
    if response.status_code == 200:
        data = response.json()
        print(f"📊 WhatsApp Monitoring: {data}")
        
        if "Twilio not configured" in str(data):
            print("❌ TWILIO STATUS: NOT CONFIGURED")
        elif data.get("status") == "warning" and "No successful WhatsApp transactions" in str(data):
            print("✅ TWILIO STATUS: CONFIGURED (No transactions yet - expected)")
        else:
            print("✅ TWILIO STATUS: CONFIGURED")
    else:
        print("❌ WhatsApp Monitoring: FAILED")
    
    # Test 3: Authenticate and test WhatsApp status
    timestamp = int(time.time())
    auth_data = {
        "email": f"finaltest{timestamp}@test.com",
        "password": "Test123!",
        "username": f"finaltest{timestamp}"
    }
    
    # Register
    response = requests.post(f"{BASE_URL}/auth/register", json=auth_data, timeout=30)
    if response.status_code == 201:
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test WhatsApp status
        response = requests.get(f"{BASE_URL}/whatsapp/status", headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            whatsapp_number = data.get("whatsapp_number")
            status = data.get("status")
            
            if whatsapp_number and whatsapp_number.startswith("+") and status == "active":
                print("✅ WHATSAPP SERVICE: FULLY ENABLED")
                print(f"   📱 Number: {whatsapp_number}")
                print(f"   🏷️  Sandbox: {data.get('sandbox_code')}")
            else:
                print("❌ WHATSAPP SERVICE: NOT PROPERLY CONFIGURED")
        else:
            print("❌ WhatsApp Status Check: FAILED")
        
        # Test Phone Verification
        phone_data = {"phone_number": "+919876543210"}
        response = requests.post(f"{BASE_URL}/phone/send-verification", json=phone_data, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            demo_mode = data.get("demo_mode", False)
            fallback_mode = data.get("fallback_mode", False)
            
            if success and not demo_mode and not fallback_mode:
                print("✅ PHONE VERIFICATION: TWILIO WORKING")
            elif success and (demo_mode or fallback_mode):
                print("⚠️  PHONE VERIFICATION: FALLBACK MODE (Twilio not fully configured)")
            else:
                print("❌ PHONE VERIFICATION: FAILED")
        else:
            print("❌ Phone Verification: FAILED")
        
        # Test WhatsApp Webhook
        response = requests.post(f"{BASE_URL}/whatsapp/webhook", data={}, timeout=30)
        if response.status_code == 200 and "xml" in response.headers.get('content-type', '').lower():
            print("✅ WHATSAPP WEBHOOK: READY")
        else:
            print("❌ WhatsApp Webhook: NOT READY")
    else:
        print("❌ Authentication: FAILED")
    
    print("\n" + "=" * 60)
    print("🎯 TWILIO INTEGRATION FINAL ASSESSMENT")
    print("=" * 60)

if __name__ == "__main__":
    test_twilio_integration()