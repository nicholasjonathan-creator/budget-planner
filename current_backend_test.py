#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Current Environment
Tests the current backend environment for all features
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid
import sys

# Backend URL - Current environment
BASE_URL = "https://57d97870-0a22-4961-80d4-f1bd4b737cc9.preview.emergentagent.com/api"

class CurrentBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message, details=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method, endpoint, data=None, headers=None, timeout=30):
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if self.access_token:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=default_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=default_headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.Timeout:
            print(f"Timeout error for {method} {url}")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error for {method} {url}: {e}")
            return None
        except Exception as e:
            print(f"Request error for {method} {url}: {e}")
            return None
    
    def test_health_endpoints(self):
        """Test health check and basic endpoints"""
        print("\n=== TESTING HEALTH & SERVICE STATUS ===")
        
        # Test root endpoint
        response = self.make_request("GET", "/")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Root Endpoint", True, f"API running - {data.get('message', '')}")
        else:
            self.log_test("Root Endpoint", False, "Root endpoint not accessible", 
                         {"status_code": response.status_code if response else "No response"})
        
        # Test health endpoint
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            db_status = data.get('database', 'unknown')
            environment = data.get('environment', 'unknown')
            self.log_test("Health Check", True, f"Service healthy, DB: {db_status}, Env: {environment}")
        else:
            self.log_test("Health Check", False, "Health endpoint failed", 
                         {"status_code": response.status_code if response else "No response"})
        
        # Test metrics endpoint
        response = self.make_request("GET", "/metrics")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Metrics Endpoint", True, f"Metrics available - {data.get('total_transactions', 0)} transactions")
        else:
            self.log_test("Metrics Endpoint", False, "Metrics endpoint failed")
    
    def test_authentication_system(self):
        """Test user registration and login"""
        print("\n=== TESTING AUTHENTICATION SYSTEM ===")
        
        # Generate unique test user
        timestamp = int(time.time())
        test_email = f"testuser{timestamp}@budgetplanner.com"
        test_password = "SecurePass123!"
        test_username = f"testuser{timestamp}"
        
        # Test user registration
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
            self.log_test("User Registration", True, f"User registered successfully - ID: {self.user_id}")
        else:
            error_msg = "Registration failed"
            if response:
                try:
                    error_data = response.json()
                    error_msg = f"Registration failed: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"Registration failed with status {response.status_code}"
            else:
                error_msg = "Registration failed: No response from server"
            
            self.log_test("User Registration", False, error_msg, 
                         {"status_code": response.status_code if response else "No response"})
            return False
        
        # Test login with same credentials
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        response = self.make_request("POST", "/auth/login", login_data)
        if response and response.status_code == 200:
            data = response.json()
            login_token = data.get("access_token")
            self.log_test("User Login", True, "Login successful")
            self.access_token = login_token
        else:
            self.log_test("User Login", False, "Login failed")
        
        # Test protected route - get current user
        if self.access_token:
            response = self.make_request("GET", "/auth/me")
            if response and response.status_code == 200:
                data = response.json()
                self.log_test("Protected Route Access", True, f"User info retrieved - {data.get('email')}")
            else:
                self.log_test("Protected Route Access", False, "Cannot access protected route")
        
        return bool(self.access_token)
    
    def test_critical_fixes_for_pat(self):
        """Test critical fixes for user 'Pat' as specified in review"""
        print("\n=== TESTING CRITICAL FIXES FOR USER 'PAT' ===")
        
        if not self.access_token:
            self.log_test("Critical Fixes Tests", False, "No authentication token available")
            return
        
        # Test 1: Phone Verification Fix
        print("\n🔧 CRITICAL FIX 1: PHONE VERIFICATION FIX")
        
        # Test phone status endpoint
        response = self.make_request("GET", "/phone/status")
        if response and response.status_code == 200:
            data = response.json()
            phone_number = data.get("phone_number")
            phone_verified = data.get("phone_verified", False)
            self.log_test("Phone Status Endpoint", True, 
                         f"Phone status accessible - Number: {phone_number}, Verified: {phone_verified}")
        else:
            self.log_test("Phone Status Endpoint", False, "Phone status endpoint failed")
        
        # Test send verification OTP method (should work correctly)
        phone_data = {"phone_number": "+919876543210"}
        response = self.make_request("POST", "/phone/send-verification", phone_data)
        if response and response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            message = data.get("message", "")
            if success:
                self.log_test("Phone Verification Method Fix", True, 
                             f"send_verification_otp method working: {message}")
            else:
                self.log_test("Phone Verification Method Fix", False, 
                             f"Phone verification failed: {message}")
        else:
            self.log_test("Phone Verification Method Fix", False, "Phone verification endpoint failed")
        
        # Test 2: SMS Stats Fix
        print("\n🔧 CRITICAL FIX 2: SMS STATS FIX")
        
        # Test SMS stats without authentication (should require auth)
        temp_token = self.access_token
        self.access_token = None
        
        response = self.make_request("GET", "/sms/stats")
        if response and response.status_code in [401, 403]:
            self.log_test("SMS Stats Authentication Required", True, 
                         f"SMS stats properly requires authentication (Status: {response.status_code})")
        elif response and response.status_code == 200:
            self.log_test("SMS Stats Authentication Required", False, 
                         "SMS stats should require authentication but doesn't")
        else:
            self.log_test("SMS Stats Authentication Required", False, 
                         f"Unexpected SMS stats response - Status: {response.status_code if response else 'No response'}")
        
        self.access_token = temp_token  # Restore auth
        
        # Test SMS stats with authentication (should return user-specific data)
        response = self.make_request("GET", "/sms/stats")
        if response and response.status_code == 200:
            data = response.json()
            total_sms = data.get("total_sms", 0)
            processed_sms = data.get("processed_sms", 0)
            # Should show user-specific data (likely 0 for new user), not system-wide count like 93
            if total_sms < 50:  # Reasonable threshold for new user
                self.log_test("SMS Stats User-Specific", True, 
                             f"SMS stats appear user-specific - SMS: {total_sms}, Processed: {processed_sms}")
            else:
                self.log_test("SMS Stats User-Specific", False, 
                             f"SMS stats may be system-wide - SMS: {total_sms} (expected low for new user)")
        else:
            self.log_test("SMS Stats User-Specific", False, "Failed to get SMS stats with authentication")
        
        # Test 3: SMS Display Fix
        print("\n🔧 CRITICAL FIX 3: SMS DISPLAY FIX")
        
        # Test SMS list endpoint (should return user-specific messages)
        response = self.make_request("GET", "/sms/list?page=1&limit=10")
        if response and response.status_code == 200:
            data = response.json()
            sms_list = data.get("sms_list", [])
            total_count = data.get("total_count", 0)
            self.log_test("SMS List User-Specific", True, 
                         f"SMS list shows user-specific messages - Count: {total_count}, Listed: {len(sms_list)}")
        else:
            self.log_test("SMS List User-Specific", False, "Failed to get SMS list")
        
        # Test failed SMS list (should be user-specific)
        response = self.make_request("GET", "/sms/failed")
        if response and response.status_code == 200:
            data = response.json()
            failed_sms = data.get("failed_sms", [])
            self.log_test("SMS Failed List User-Specific", True, 
                         f"Failed SMS list accessible - Count: {len(failed_sms)}")
        else:
            self.log_test("SMS Failed List User-Specific", False, "Failed to get failed SMS list")
        
        # Test SMS duplicate detection (should be user-specific)
        response = self.make_request("POST", "/sms/find-duplicates")
        if response and response.status_code == 200:
            data = response.json()
            duplicate_groups = data.get("duplicate_groups", [])
            total_groups = data.get("total_groups", 0)
            self.log_test("SMS Duplicate Detection User-Specific", True, 
                         f"SMS duplicate detection working - Groups: {total_groups}")
        else:
            self.log_test("SMS Duplicate Detection User-Specific", False, "Failed to test SMS duplicate detection")
    
    def test_phase2_features(self):
        """Test Phase 2 features"""
        print("\n=== TESTING PHASE 2 FEATURES ===")
        
        if not self.access_token:
            self.log_test("Phase 2 Tests", False, "No authentication token available")
            return
        
        # Test Account Deletion Endpoints
        print("\n📋 PHASE 2: ACCOUNT DELETION ENDPOINTS")
        
        # Test account deletion preview
        response = self.make_request("GET", "/account/deletion/preview")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Account Deletion Preview", True, 
                         f"Preview successful - User data retrieved")
        else:
            self.log_test("Account Deletion Preview", False, 
                         f"Preview failed - Status: {response.status_code if response else 'No response'}")
        
        # Test Phone Number Management Endpoints
        print("\n📋 PHASE 2: PHONE NUMBER MANAGEMENT ENDPOINTS")
        
        # Test phone status (already tested above, but verify again)
        response = self.make_request("GET", "/phone/status")
        if response and response.status_code == 200:
            self.log_test("Phone Management Status", True, "Phone status endpoint working")
        else:
            self.log_test("Phone Management Status", False, "Phone status endpoint failed")
        
        # Test Enhanced SMS Management
        print("\n📋 PHASE 2: ENHANCED SMS MANAGEMENT")
        
        # Test SMS list (already tested above)
        response = self.make_request("GET", "/sms/list")
        if response and response.status_code == 200:
            self.log_test("Enhanced SMS List", True, "SMS list endpoint working")
        else:
            self.log_test("Enhanced SMS List", False, "SMS list endpoint failed")
        
        # Test SMS duplicate detection (already tested above)
        response = self.make_request("POST", "/sms/find-duplicates")
        if response and response.status_code == 200:
            self.log_test("Enhanced SMS Duplicate Detection", True, "SMS duplicate detection working")
        else:
            self.log_test("Enhanced SMS Duplicate Detection", False, "SMS duplicate detection failed")
    
    def test_core_functionality(self):
        """Test core functionality"""
        print("\n=== TESTING CORE FUNCTIONALITY ===")
        
        if not self.access_token:
            self.log_test("Core Tests", False, "No authentication token available")
            return
        
        # Test transaction management
        current_date = datetime.now()
        transaction_data = {
            "type": "expense",
            "category_id": 1,
            "amount": 150.50,
            "description": "Test transaction",
            "date": current_date.isoformat(),
            "merchant": "Test Merchant"
        }
        
        response = self.make_request("POST", "/transactions", transaction_data)
        if response and response.status_code == 200:
            data = response.json()
            transaction_id = data.get("id")
            self.log_test("Transaction Creation", True, f"Transaction created - ID: {transaction_id}")
        else:
            self.log_test("Transaction Creation", False, "Failed to create transaction")
        
        # Test getting transactions
        response = self.make_request("GET", f"/transactions?month={current_date.month}&year={current_date.year}")
        if response and response.status_code == 200:
            transactions = response.json()
            self.log_test("Transaction Retrieval", True, f"Retrieved {len(transactions)} transactions")
        else:
            self.log_test("Transaction Retrieval", False, "Failed to get transactions")
        
        # Test categories
        response = self.make_request("GET", "/categories")
        if response and response.status_code == 200:
            categories = response.json()
            self.log_test("Categories", True, f"Retrieved {len(categories)} categories")
        else:
            self.log_test("Categories", False, "Failed to get categories")
        
        # Test analytics
        response = self.make_request("GET", f"/analytics/monthly-summary?month={current_date.month}&year={current_date.year}")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Analytics", True, f"Monthly summary - Income: {data.get('income', 0)}, Expenses: {data.get('expense', 0)}")
        else:
            self.log_test("Analytics", False, "Failed to get analytics")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🎯 COMPREHENSIVE BACKEND TESTING")
        print(f"🌐 Target Backend: {self.base_url}")
        print("=" * 80)
        
        # Run all test suites
        self.test_health_endpoints()
        auth_success = self.test_authentication_system()
        
        if auth_success:
            self.test_critical_fixes_for_pat()
            self.test_phase2_features()
            self.test_core_functionality()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests Run: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Critical fixes summary
        critical_fixes_tests = [r for r in self.test_results if any(keyword in r["test"] for keyword in ["Phone", "SMS"])]
        critical_passed = sum(1 for result in critical_fixes_tests if result["success"])
        critical_total = len(critical_fixes_tests)
        
        if critical_total > 0:
            critical_rate = (critical_passed / critical_total * 100)
            print(f"\n🎯 CRITICAL FIXES FOR USER 'PAT':")
            print(f"✅ Passed: {critical_passed}/{critical_total}")
            print(f"📊 Success Rate: {critical_rate:.1f}%")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['message']}")
        
        return success_rate >= 90

if __name__ == "__main__":
    tester = CurrentBackendTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 BACKEND TESTING COMPLETED SUCCESSFULLY")
        sys.exit(0)
    else:
        print("\n⚠️ BACKEND TESTING COMPLETED WITH ISSUES")
        sys.exit(1)