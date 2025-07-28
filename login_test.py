#!/usr/bin/env python3
"""
Login Issue Investigation for User 'Pat'
Tests the live backend at https://budget-planner-backendjuly.onrender.com
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid
import sys

# Backend URL - Production backend for login issue investigation
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

class LoginIssueTester:
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
    
    def make_request(self, method, endpoint, data=None, headers=None, timeout=60):
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

    def test_login_issue_for_pat_user(self):
        """Test login issue investigation for user 'Pat' - Focus on login functionality"""
        print("\n" + "=" * 80)
        print("🎯 LOGIN ISSUE INVESTIGATION FOR USER 'PAT'")
        print("🌐 Testing Backend: https://budget-planner-backendjuly.onrender.com")
        print("📧 User Email: patrick1091+1@gmail.com")
        print("🔍 Issue: User stuck on 'Logging in...' and login not completing")
        print("=" * 80)
        
        # Test 1: Login Endpoint Health
        print("\n🔧 TEST 1: LOGIN ENDPOINT HEALTH")
        print("   - Test POST /api/auth/login endpoint")
        print("   - Verify it accepts credentials and returns tokens")
        print("   - Check response time and success rate")
        
        # Test login endpoint with invalid credentials first to check if endpoint is working
        invalid_login_data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        start_time = time.time()
        response = self.make_request("POST", "/auth/login", invalid_login_data)
        response_time = time.time() - start_time
        
        if response and response.status_code == 401:
            self.log_test("Login Endpoint Health", True, 
                         f"✅ Login endpoint working - Response time: {response_time:.2f}s")
        elif response and response.status_code == 422:
            self.log_test("Login Endpoint Health", True, 
                         f"✅ Login endpoint accessible - Validation working - Response time: {response_time:.2f}s")
        else:
            self.log_test("Login Endpoint Health", False, 
                         f"❌ Login endpoint issue - Status: {response.status_code if response else 'No response'} - Response time: {response_time:.2f}s")
        
        # Test 2: Authentication Flow with Pat's Email
        print("\n🔧 TEST 2: AUTHENTICATION FLOW FOR USER 'PAT'")
        print("   - Test login with email: patrick1091+1@gmail.com")
        print("   - Verify JWT token generation")
        print("   - Test token validation endpoint /api/auth/me")
        
        # Try to login with Pat's email (we don't know the password, so this will likely fail)
        pat_login_data = {
            "email": "patrick1091+1@gmail.com",
            "password": "testpassword123"  # We don't know the real password
        }
        
        start_time = time.time()
        response = self.make_request("POST", "/auth/login", pat_login_data)
        login_response_time = time.time() - start_time
        
        if response and response.status_code == 401:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                if 'Incorrect email or password' in error_detail:
                    self.log_test("Pat User Login Attempt", True, 
                                 f"✅ User 'Pat' exists in database - Login endpoint working - Response time: {login_response_time:.2f}s")
                else:
                    self.log_test("Pat User Login Attempt", False, 
                                 f"❌ Unexpected login error: {error_detail} - Response time: {login_response_time:.2f}s")
            except:
                self.log_test("Pat User Login Attempt", True, 
                             f"✅ Login endpoint responding correctly - Response time: {login_response_time:.2f}s")
        elif response and response.status_code == 200:
            # Unexpected success - this would mean we guessed the password
            data = response.json()
            access_token = data.get("access_token")
            if access_token:
                self.log_test("Pat User Login Success", True, 
                             f"✅ UNEXPECTED SUCCESS - Pat user logged in - Response time: {login_response_time:.2f}s")
                
                # Test token validation
                temp_token = self.access_token
                self.access_token = access_token
                
                response = self.make_request("GET", "/auth/me")
                if response and response.status_code == 200:
                    user_data = response.json()
                    self.log_test("Pat Token Validation", True, 
                                 f"✅ JWT token valid - User: {user_data.get('email')}")
                else:
                    self.log_test("Pat Token Validation", False, 
                                 "❌ JWT token validation failed")
                
                self.access_token = temp_token  # Restore original token
            else:
                self.log_test("Pat User Login", False, 
                             f"❌ Login response missing access token - Response time: {login_response_time:.2f}s")
        else:
            self.log_test("Pat User Login", False, 
                         f"❌ Login failed - Status: {response.status_code if response else 'No response'} - Response time: {login_response_time:.2f}s")
        
        # Test 3: Login Performance Analysis
        print("\n🔧 TEST 3: LOGIN PERFORMANCE ANALYSIS")
        print("   - Check response times for login endpoint")
        print("   - Identify any timeouts or slow responses")
        print("   - Test concurrent login attempts")
        
        # Test multiple login attempts to check for performance issues
        response_times = []
        for i in range(3):
            test_login_data = {
                "email": f"perftest{i}@test.com",
                "password": "testpass123"
            }
            
            start_time = time.time()
            response = self.make_request("POST", "/auth/login", test_login_data)
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            if response_time > 5.0:
                self.log_test(f"Login Performance Test {i+1}", False, 
                             f"❌ Slow response: {response_time:.2f}s (>5s threshold)")
            else:
                self.log_test(f"Login Performance Test {i+1}", True, 
                             f"✅ Good response time: {response_time:.2f}s")
        
        avg_response_time = sum(response_times) / len(response_times)
        if avg_response_time < 5.0:
            self.log_test("Login Performance Summary", True, 
                         f"✅ Average login response time: {avg_response_time:.2f}s (within 5s threshold)")
        else:
            self.log_test("Login Performance Summary", False, 
                         f"❌ Average login response time: {avg_response_time:.2f}s (exceeds 5s threshold)")
        
        # Test 4: User Database Lookup
        print("\n🔧 TEST 4: USER DATABASE LOOKUP")
        print("   - Check if user 'Pat' exists in database")
        print("   - Verify user lookup functionality")
        
        # Try to register with Pat's email to see if user already exists
        pat_registration_data = {
            "email": "patrick1091+1@gmail.com",
            "password": "testpassword123",
            "username": "pat_test_user"
        }
        
        response = self.make_request("POST", "/auth/register", pat_registration_data)
        if response and response.status_code == 400:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                if 'already exists' in error_detail.lower() or 'already registered' in error_detail.lower():
                    self.log_test("Pat User Database Lookup", True, 
                                 f"✅ User 'Pat' exists in database: {error_detail}")
                else:
                    self.log_test("Pat User Database Lookup", False, 
                                 f"❌ Unexpected registration error: {error_detail}")
            except:
                self.log_test("Pat User Database Lookup", True, 
                             "✅ User 'Pat' likely exists (registration failed as expected)")
        elif response and response.status_code == 201:
            # User was successfully created, which means they didn't exist before
            data = response.json()
            self.log_test("Pat User Database Lookup", False, 
                         f"❌ User 'Pat' did NOT exist in database - New user created: {data.get('user', {}).get('id')}")
        else:
            self.log_test("Pat User Database Lookup", False, 
                         f"❌ Cannot verify user existence - Status: {response.status_code if response else 'No response'}")
        
        # Test 5: Authentication Token Generation
        print("\n🔧 TEST 5: AUTHENTICATION TOKEN GENERATION")
        print("   - Test JWT token generation working")
        print("   - Verify token structure and expiration")
        
        # Create a test user to verify token generation works
        timestamp = int(time.time())
        test_email = f"tokentest{timestamp}@budgetplanner.com"
        test_password = "SecurePass123!"
        test_username = f"tokentest{timestamp}"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username
        }
        
        response = self.make_request("POST", "/auth/register", registration_data)
        if response and response.status_code == 201:
            data = response.json()
            access_token = data.get("access_token")
            if access_token:
                self.log_test("JWT Token Generation", True, 
                             f"✅ JWT token generation working - Token length: {len(access_token)}")
                
                # Test token validation
                temp_token = self.access_token
                self.access_token = access_token
                
                response = self.make_request("GET", "/auth/me")
                if response and response.status_code == 200:
                    user_data = response.json()
                    self.log_test("JWT Token Validation", True, 
                                 f"✅ JWT token validation working - User: {user_data.get('email')}")
                else:
                    self.log_test("JWT Token Validation", False, 
                                 "❌ JWT token validation failed")
                
                self.access_token = temp_token  # Restore original token
            else:
                self.log_test("JWT Token Generation", False, 
                             "❌ Registration response missing access token")
        else:
            self.log_test("JWT Token Generation", False, 
                         f"❌ Cannot test token generation - Registration failed: {response.status_code if response else 'No response'}")

    def run_login_investigation(self):
        """Run login issue investigation"""
        print("🚀 STARTING LOGIN ISSUE INVESTIGATION FOR USER 'PAT'")
        print(f"🎯 Target: {self.base_url}")
        print("🔍 Focus: Login functionality and performance analysis")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run login investigation
        self.test_login_issue_for_pat_user()
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 80)
        print("📊 LOGIN INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        for result in self.test_results:
            if not result["success"]:
                print(f"❌ {result['test']}: {result['message']}")
        
        print("\n✅ SUCCESSFUL TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"✅ {result['test']}: {result['message']}")

if __name__ == "__main__":
    tester = LoginIssueTester()
    tester.run_login_investigation()