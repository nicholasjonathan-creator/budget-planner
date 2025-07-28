#!/usr/bin/env python3
"""
Focused Twilio Integration Testing for Budget Planner
Tests specifically for Twilio WhatsApp and Phone Verification after credential deployment
"""

import requests
import json
import time
from datetime import datetime

# Production backend URL
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

class TwilioIntegrationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        
    def authenticate(self):
        """Authenticate to get access token"""
        print("🔐 Authenticating...")
        
        # Generate unique test user
        timestamp = int(time.time())
        test_email = f"twiliotest{timestamp}@budgetplanner.com"
        test_password = "TwilioTest123!"
        test_username = f"twiliotest{timestamp}"
        
        # Register user
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username
        }
        
        response = self.session.post(f"{self.base_url}/auth/register", json=registration_data, timeout=30)
        if response.status_code == 201:
            data = response.json()
            self.access_token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            print(f"✅ Authentication successful - User ID: {self.user_id}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
    
    def make_authenticated_request(self, method, endpoint, data=None):
        """Make authenticated request"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def test_twilio_configuration(self):
        """Test Twilio configuration status"""
        print("\n🔧 TESTING TWILIO CONFIGURATION")
        print("=" * 50)
        
        # Test WhatsApp status endpoint
        response = self.make_authenticated_request("GET", "/whatsapp/status")
        if response and response.status_code == 200:
            data = response.json()
            print(f"📱 WhatsApp Status: {json.dumps(data, indent=2)}")
            
            whatsapp_number = data.get("whatsapp_number")
            status = data.get("status")
            sandbox_code = data.get("sandbox_code")
            
            if whatsapp_number and whatsapp_number != "None":
                print(f"✅ TWILIO_WHATSAPP_NUMBER: {whatsapp_number}")
            else:
                print(f"❌ TWILIO_WHATSAPP_NUMBER: Not configured")
            
            if status == "active":
                print(f"✅ WhatsApp Service: ACTIVE")
            else:
                print(f"❌ WhatsApp Service: {status}")
                
            if sandbox_code:
                print(f"✅ Sandbox Code: {sandbox_code}")
            else:
                print(f"❌ Sandbox Code: Not available")
        else:
            print(f"❌ WhatsApp status check failed: {response.status_code if response else 'No response'}")
        
        # Test monitoring WhatsApp status
        response = self.session.get(f"{self.base_url}/monitoring/whatsapp-status", timeout=30)
        if response and response.status_code == 200:
            data = response.json()
            print(f"📊 Monitoring Status: {json.dumps(data, indent=2)}")
            
            if "Twilio not configured" in str(data):
                print("❌ TWILIO CREDENTIALS: Not configured")
            elif "fallback mode" in str(data).lower():
                print("⚠️  TWILIO CREDENTIALS: Fallback mode active")
            else:
                print("✅ TWILIO CREDENTIALS: Configured")
        else:
            print(f"❌ Monitoring status check failed: {response.status_code if response else 'No response'}")
    
    def test_phone_verification(self):
        """Test phone verification with Twilio"""
        print("\n📞 TESTING PHONE VERIFICATION")
        print("=" * 50)
        
        # Test phone status
        response = self.make_authenticated_request("GET", "/phone/status")
        if response and response.status_code == 200:
            data = response.json()
            print(f"📋 Phone Status: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Phone status check failed: {response.status_code if response else 'No response'}")
        
        # Test sending verification code
        phone_data = {"phone_number": "+919876543210"}
        response = self.make_authenticated_request("POST", "/phone/send-verification", phone_data)
        if response and response.status_code == 200:
            data = response.json()
            print(f"📤 Send Verification Response: {json.dumps(data, indent=2)}")
            
            success = data.get("success", False)
            message = data.get("message", "")
            demo_mode = data.get("demo_mode", False)
            fallback_mode = data.get("fallback_mode", False)
            
            if success and not demo_mode and not fallback_mode:
                print("✅ TWILIO PHONE VERIFICATION: WORKING")
            elif success and (demo_mode or fallback_mode):
                print("⚠️  TWILIO PHONE VERIFICATION: Using fallback/demo mode")
            else:
                print("❌ TWILIO PHONE VERIFICATION: FAILED")
        else:
            print(f"❌ Phone verification failed: {response.status_code if response else 'No response'}")
            if response:
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    print(f"   Raw response: {response.text}")
        
        # Test OTP verification endpoint (with invalid OTP to check if endpoint works)
        otp_data = {"otp": "123456"}
        response = self.make_authenticated_request("POST", "/phone/verify-otp", otp_data)
        if response:
            print(f"🔢 OTP Verification Test: Status {response.status_code}")
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"   Expected error: {error_data}")
                    print("✅ OTP VERIFICATION ENDPOINT: Working (invalid OTP rejected)")
                except:
                    print("✅ OTP VERIFICATION ENDPOINT: Working")
            elif response.status_code == 200:
                print("⚠️  OTP VERIFICATION: Unexpected success with test OTP")
            else:
                print(f"❌ OTP VERIFICATION ENDPOINT: Unexpected status {response.status_code}")
        else:
            print("❌ OTP VERIFICATION ENDPOINT: Not accessible")
    
    def test_whatsapp_webhook(self):
        """Test WhatsApp webhook endpoint"""
        print("\n🔗 TESTING WHATSAPP WEBHOOK")
        print("=" * 50)
        
        # Test webhook endpoint with empty data
        response = self.session.post(f"{self.base_url}/whatsapp/webhook", data={}, timeout=30)
        if response:
            print(f"📡 Webhook Response: Status {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200 and "xml" in response.headers.get('content-type', '').lower():
                print("✅ WHATSAPP WEBHOOK: Ready and responding with TwiML")
            elif response.status_code in [400, 422]:
                print("✅ WHATSAPP WEBHOOK: Accessible (expected error for empty data)")
            else:
                print(f"⚠️  WHATSAPP WEBHOOK: Unexpected response")
        else:
            print("❌ WHATSAPP WEBHOOK: Not accessible")
    
    def test_environment_variables(self):
        """Test if Twilio environment variables are loaded"""
        print("\n🌍 TESTING ENVIRONMENT VARIABLES")
        print("=" * 50)
        
        # Check health endpoint for environment info
        response = self.session.get(f"{self.base_url}/health", timeout=30)
        if response and response.status_code == 200:
            data = response.json()
            environment = data.get("environment", "unknown")
            print(f"🏗️  Environment: {environment}")
        
        # The WhatsApp status endpoint will show if Twilio env vars are loaded
        response = self.make_authenticated_request("GET", "/whatsapp/status")
        if response and response.status_code == 200:
            data = response.json()
            whatsapp_number = data.get("whatsapp_number")
            
            if whatsapp_number and whatsapp_number.startswith("+"):
                print(f"✅ TWILIO_WHATSAPP_NUMBER loaded: {whatsapp_number}")
            else:
                print(f"❌ TWILIO_WHATSAPP_NUMBER not loaded: {whatsapp_number}")
        
        print("\n📝 Environment Variable Status:")
        print("   TWILIO_ACCOUNT_SID: Cannot check directly (security)")
        print("   TWILIO_AUTH_TOKEN: Cannot check directly (security)")
        print("   TWILIO_WHATSAPP_NUMBER: Checked via WhatsApp status")
    
    def run_comprehensive_test(self):
        """Run comprehensive Twilio integration test"""
        print("🚀 TWILIO INTEGRATION COMPREHENSIVE TEST")
        print("🎯 Target: https://budget-planner-backendjuly.onrender.com")
        print("🔧 Testing: Twilio WhatsApp and Phone Verification")
        print("=" * 80)
        
        start_time = time.time()
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Cannot proceed without authentication")
            return
        
        # Run Twilio-specific tests
        self.test_environment_variables()
        self.test_twilio_configuration()
        self.test_phone_verification()
        self.test_whatsapp_webhook()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 80)
        print("📊 TWILIO INTEGRATION TEST SUMMARY")
        print("=" * 80)
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"🕐 Timestamp: {datetime.now().isoformat()}")
        
        print("\n🎯 KEY FINDINGS:")
        print("   1. WhatsApp service status and configuration")
        print("   2. Phone verification functionality")
        print("   3. Twilio environment variables loading")
        print("   4. Webhook endpoint readiness")
        
        print("\n✅ NEXT STEPS:")
        print("   - Review the detailed output above")
        print("   - Check if Twilio credentials are properly configured")
        print("   - Verify WhatsApp sandbox setup if needed")

def main():
    """Main test execution"""
    tester = TwilioIntegrationTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()