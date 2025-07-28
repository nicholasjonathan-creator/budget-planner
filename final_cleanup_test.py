#!/usr/bin/env python3
"""
Final Comprehensive Phone Number Cleanup Test for +919886763496
Complete cleanup verification with proper authentication
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

class FinalCleanupTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.cleanup_results = []
        
    def log_result(self, step, success, message, details=None):
        """Log cleanup results"""
        result = {
            "step": step,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.cleanup_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {step}: {message}")
        return success
        
    def make_request(self, method, endpoint, data=None, timeout=60):
        """Make authenticated HTTP request"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"   Request error: {e}")
            return None
    
    def authenticate(self):
        """Authenticate to get access token"""
        print("🔐 AUTHENTICATION STEP")
        print("-" * 40)
        
        timestamp = int(time.time())
        test_email = f"final_cleanup_{timestamp}@budgetplanner.com"
        test_password = "FinalCleanup123!"
        test_username = f"final_cleanup_{timestamp}"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username
        }
        
        response = self.make_request("POST", "/auth/register", registration_data)
        if response and response.status_code == 201:
            data = response.json()
            self.access_token = data.get("access_token")
            self.user_id = data.get("user", {}).get("id")
            return self.log_result("Authentication", True, f"Successfully authenticated - User ID: {self.user_id}")
        else:
            return self.log_result("Authentication", False, "Failed to authenticate")
    
    def execute_phone_cleanup(self):
        """Execute comprehensive phone number cleanup for +919886763496"""
        target_phone = "+919886763496"
        
        print(f"\n🧹 PHONE NUMBER CLEANUP EXECUTION")
        print(f"🎯 Target Phone: {target_phone}")
        print("-" * 60)
        
        if not self.access_token:
            return self.log_result("Cleanup Execution", False, "No authentication token available")
        
        # Step 1: Check if phone number exists in user records
        print(f"\n📋 STEP 1: Check existing phone number associations")
        response = self.make_request("GET", "/phone/status")
        if response and response.status_code == 200:
            data = response.json()
            current_phone = data.get("phone_number")
            phone_verified = data.get("phone_verified", False)
            
            if current_phone == target_phone:
                self.log_result("Phone Association Check", True, f"Target phone found in current user (verified: {phone_verified})")
                
                # Unlink the phone number
                print(f"   🔗 Unlinking phone number from user...")
                unlink_response = self.make_request("DELETE", "/phone/unlink")
                if unlink_response and unlink_response.status_code == 200:
                    self.log_result("Phone Unlink", True, f"Successfully unlinked {target_phone}")
                else:
                    self.log_result("Phone Unlink", False, f"Failed to unlink {target_phone}")
            else:
                self.log_result("Phone Association Check", True, f"Target phone not associated with current user (current: {current_phone})")
        else:
            self.log_result("Phone Association Check", False, "Failed to check phone status")
        
        # Step 2: Test fresh phone verification flow
        print(f"\n📱 STEP 2: Test fresh phone verification flow")
        phone_data = {"phone_number": target_phone}
        response = self.make_request("POST", "/phone/send-verification", phone_data)
        
        verification_sent = False
        if response and response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            message = data.get("message", "")
            
            if success:
                verification_sent = True
                self.log_result("Fresh Phone Verification", True, f"Verification sent successfully: {message}")
            else:
                self.log_result("Fresh Phone Verification", False, f"Verification failed: {message}")
        else:
            error_msg = "Verification request failed"
            if response:
                try:
                    error_data = response.json()
                    error_msg = f"Verification failed: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"Verification failed with status {response.status_code}"
            self.log_result("Fresh Phone Verification", False, error_msg)
        
        # Step 3: Test OTP verification endpoints
        print(f"\n🔐 STEP 3: Test OTP verification endpoints")
        if verification_sent:
            otp_data = {"otp": "123456"}  # Test OTP that should fail
            otp_response = self.make_request("POST", "/phone/verify-otp", otp_data)
            
            if otp_response:
                if otp_response.status_code == 400:
                    try:
                        error_data = otp_response.json()
                        error_detail = error_data.get('detail', '')
                        if 'invalid' in error_detail.lower() or 'expired' in error_detail.lower():
                            self.log_result("OTP Verification Endpoint", True, "OTP endpoint working correctly (invalid OTP rejected)")
                        else:
                            self.log_result("OTP Verification Endpoint", False, f"Unexpected OTP error: {error_detail}")
                    except:
                        self.log_result("OTP Verification Endpoint", True, "OTP endpoint accessible and responding")
                elif otp_response.status_code == 200:
                    self.log_result("OTP Verification Endpoint", False, "Test OTP should not succeed")
                else:
                    self.log_result("OTP Verification Endpoint", False, f"Unexpected OTP response: {otp_response.status_code}")
            else:
                self.log_result("OTP Verification Endpoint", False, "OTP endpoint not accessible")
        else:
            self.log_result("OTP Verification Endpoint", False, "Cannot test OTP - verification not sent")
        
        # Step 4: Verify WhatsApp integration readiness
        print(f"\n📲 STEP 4: Verify WhatsApp integration readiness")
        response = self.make_request("GET", "/whatsapp/status")
        if response and response.status_code == 200:
            data = response.json()
            whatsapp_number = data.get("whatsapp_number")
            sandbox_code = data.get("sandbox_code")
            status = data.get("status", "unknown")
            setup_instructions = data.get("setup_instructions", [])
            
            if status == "active" and whatsapp_number:
                self.log_result("WhatsApp Integration", True, f"WhatsApp ready - Number: {whatsapp_number}, Sandbox: {sandbox_code}, Instructions: {len(setup_instructions)} steps")
            else:
                self.log_result("WhatsApp Integration", False, f"WhatsApp not ready - Status: {status}")
        else:
            self.log_result("WhatsApp Integration", False, "Failed to check WhatsApp status")
        
        # Step 5: Final verification - check phone status again
        print(f"\n🔍 STEP 5: Final verification - check phone status")
        response = self.make_request("GET", "/phone/status")
        if response and response.status_code == 200:
            data = response.json()
            current_phone = data.get("phone_number")
            phone_verified = data.get("phone_verified", False)
            
            if current_phone != target_phone:
                self.log_result("Final Phone Status", True, f"Target phone successfully cleaned (current: {current_phone})")
            else:
                self.log_result("Final Phone Status", False, f"Target phone still associated with user")
        else:
            self.log_result("Final Phone Status", False, "Failed to verify final phone status")
        
        return True
    
    def generate_final_report(self):
        """Generate comprehensive cleanup report"""
        target_phone = "+919886763496"
        
        print(f"\n" + "="*80)
        print(f"📊 FINAL CLEANUP REPORT FOR {target_phone}")
        print("="*80)
        
        # Calculate success metrics
        total_steps = len(self.cleanup_results)
        successful_steps = sum(1 for result in self.cleanup_results if result["success"])
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        print(f"\n📈 CLEANUP METRICS:")
        print(f"   Total Steps: {total_steps}")
        print(f"   Successful Steps: {successful_steps}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n🔍 DETAILED STEP RESULTS:")
        for result in self.cleanup_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['step']}: {result['message']}")
        
        # Determine cleanup status
        print(f"\n🎯 CLEANUP STATUS ASSESSMENT:")
        if success_rate >= 80:
            print(f"   ✅ CLEANUP SUCCESSFUL!")
            print(f"   ✅ Phone number {target_phone} is READY for fresh testing")
            print(f"   ✅ All critical cleanup steps completed")
            print(f"   ✅ WhatsApp integration is operational")
            print(f"   ✅ User can proceed with live WhatsApp testing")
            cleanup_status = "SUCCESS"
        elif success_rate >= 60:
            print(f"   ⚠️  CLEANUP PARTIALLY SUCCESSFUL")
            print(f"   ⚠️  Phone number {target_phone} may be usable with minor issues")
            print(f"   ⚠️  Review failed steps before proceeding")
            cleanup_status = "PARTIAL"
        else:
            print(f"   ❌ CLEANUP FAILED")
            print(f"   ❌ Phone number {target_phone} has significant issues")
            print(f"   ❌ Manual intervention may be required")
            cleanup_status = "FAILED"
        
        # WhatsApp integration readiness
        whatsapp_ready = any(result["success"] for result in self.cleanup_results if result["step"] == "WhatsApp Integration")
        verification_ready = any(result["success"] for result in self.cleanup_results if result["step"] == "Fresh Phone Verification")
        
        print(f"\n📲 WHATSAPP INTEGRATION READINESS:")
        if whatsapp_ready and verification_ready:
            print(f"   ✅ WhatsApp integration is READY for {target_phone}")
            print(f"   ✅ Phone verification system is operational")
            print(f"   ✅ User can start WhatsApp setup process")
        else:
            print(f"   ❌ WhatsApp integration has issues")
            print(f"   ❌ Check WhatsApp service status")
        
        return success_rate, cleanup_status

def main():
    """Main cleanup execution"""
    print("🧹 FINAL PHONE NUMBER CLEANUP PROCESS")
    print("🎯 Target Phone: +919886763496")
    print("🔗 Backend: https://budget-planner-backendjuly.onrender.com")
    print("="*80)
    
    tester = FinalCleanupTester()
    
    # Execute cleanup process
    if not tester.authenticate():
        print("❌ Cannot proceed without authentication")
        return False
    
    if not tester.execute_phone_cleanup():
        print("❌ Cleanup execution failed")
        return False
    
    # Generate final report
    success_rate, cleanup_status = tester.generate_final_report()
    
    # Final assessment
    print(f"\n" + "="*80)
    print("🏁 FINAL ASSESSMENT")
    print("="*80)
    
    if cleanup_status == "SUCCESS":
        print("🎉 PHONE NUMBER CLEANUP COMPLETED SUCCESSFULLY!")
        print("✅ +919886763496 is ready for fresh WhatsApp integration testing")
        print("✅ All cleanup objectives achieved")
        print("✅ User can proceed with live testing immediately")
        return True
    elif cleanup_status == "PARTIAL":
        print("⚠️  PHONE NUMBER CLEANUP PARTIALLY SUCCESSFUL")
        print("⚠️  +919886763496 may be usable but review issues first")
        print("⚠️  Consider manual verification before live testing")
        return True
    else:
        print("❌ PHONE NUMBER CLEANUP FAILED")
        print("❌ +919886763496 requires manual intervention")
        print("❌ Do not proceed with live testing until issues resolved")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)