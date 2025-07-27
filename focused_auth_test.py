#!/usr/bin/env python3
"""
Focused Authentication and Database Testing for MongoDB Atlas User Role Update
Tests specifically the authentication system and database operations that were previously failing
"""

import requests
import json
import time
from datetime import datetime
import uuid
import sys

# Production backend URL
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

class FocusedAuthTester:
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
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def make_request_with_timing(self, method, endpoint, data=None, headers=None, timeout=120):
        """Make HTTP request with detailed timing and error information"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if self.access_token:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        if headers:
            default_headers.update(headers)
        
        start_time = time.time()
        
        try:
            print(f"   🔄 Making {method} request to {endpoint}...")
            
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
            
            end_time = time.time()
            response_time = end_time - start_time
            
            print(f"   ⏱️  Response time: {response_time:.2f}s")
            print(f"   📊 Status code: {response.status_code}")
            
            return response, response_time
            
        except requests.exceptions.Timeout as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"   ⏱️  Timeout after: {response_time:.2f}s")
            print(f"   ❌ Timeout error: {e}")
            return None, response_time
        except requests.exceptions.ConnectionError as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"   ⏱️  Connection failed after: {response_time:.2f}s")
            print(f"   ❌ Connection error: {e}")
            return None, response_time
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"   ⏱️  Request failed after: {response_time:.2f}s")
            print(f"   ❌ Request error: {e}")
            return None, response_time
    
    def test_database_connection_health(self):
        """Test database connection through health endpoint"""
        print("\n=== TESTING DATABASE CONNECTION HEALTH ===")
        
        response, response_time = self.make_request_with_timing("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            db_status = data.get('database', 'unknown')
            environment = data.get('environment', 'unknown')
            self.log_test("Database Health Check", True, 
                         f"DB: {db_status}, Environment: {environment}, Response time: {response_time:.2f}s")
            return True
        else:
            self.log_test("Database Health Check", False, 
                         f"Health check failed, Response time: {response_time:.2f}s",
                         {"status_code": response.status_code if response else "No response"})
            return False
    
    def test_categories_endpoint_detailed(self):
        """Test categories endpoint with detailed error analysis"""
        print("\n=== TESTING CATEGORIES ENDPOINT (REQUIRES AUTH) ===")
        
        # First test without authentication
        response, response_time = self.make_request_with_timing("GET", "/categories")
        
        if response:
            if response.status_code == 401:
                self.log_test("Categories Without Auth", True, 
                             f"Correctly requires authentication (401), Response time: {response_time:.2f}s")
            elif response.status_code == 200:
                categories = response.json()
                self.log_test("Categories Without Auth", False, 
                             f"Should require auth but returned {len(categories)} categories, Response time: {response_time:.2f}s")
            else:
                try:
                    error_data = response.json()
                    self.log_test("Categories Without Auth", False, 
                                 f"Unexpected status {response.status_code}, Response time: {response_time:.2f}s",
                                 {"error": error_data})
                except:
                    self.log_test("Categories Without Auth", False, 
                                 f"Unexpected status {response.status_code}, Response time: {response_time:.2f}s",
                                 {"response_text": response.text[:200]})
        else:
            self.log_test("Categories Without Auth", False, 
                         f"No response from server, Response time: {response_time:.2f}s")
    
    def test_user_registration_detailed(self):
        """Test user registration with detailed timing and error analysis"""
        print("\n=== TESTING USER REGISTRATION (DETAILED) ===")
        
        # Generate unique test user with realistic data
        timestamp = int(time.time())
        test_email = f"sarah.johnson{timestamp}@budgetplanner.com"
        test_password = "SecureBudget2024!"
        test_username = f"sarah_johnson_{timestamp}"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username
        }
        
        print(f"   📝 Registering user: {test_email}")
        
        response, response_time = self.make_request_with_timing("POST", "/auth/register", registration_data, timeout=180)
        
        if response:
            if response.status_code == 201:
                try:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    user_data = data.get("user", {})
                    self.user_id = user_data.get("id")
                    
                    self.log_test("User Registration", True, 
                                 f"Registration successful! User ID: {self.user_id}, Response time: {response_time:.2f}s")
                    
                    # Validate token structure
                    if self.access_token and len(self.access_token) > 50:
                        self.log_test("JWT Token Generation", True, 
                                     f"Valid JWT token generated (length: {len(self.access_token)})")
                    else:
                        self.log_test("JWT Token Generation", False, 
                                     "Invalid or missing JWT token")
                    
                    return True
                    
                except json.JSONDecodeError as e:
                    self.log_test("User Registration", False, 
                                 f"Registration returned 201 but invalid JSON, Response time: {response_time:.2f}s",
                                 {"json_error": str(e), "response_text": response.text[:200]})
                    
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    self.log_test("User Registration", False, 
                                 f"Registration failed with validation error, Response time: {response_time:.2f}s",
                                 {"error": error_data})
                except:
                    self.log_test("User Registration", False, 
                                 f"Registration failed (400), Response time: {response_time:.2f}s",
                                 {"response_text": response.text[:200]})
                    
            elif response.status_code == 422:
                try:
                    error_data = response.json()
                    self.log_test("User Registration", False, 
                                 f"Registration failed with validation error, Response time: {response_time:.2f}s",
                                 {"validation_error": error_data})
                except:
                    self.log_test("User Registration", False, 
                                 f"Registration failed (422), Response time: {response_time:.2f}s",
                                 {"response_text": response.text[:200]})
                    
            elif response.status_code == 500:
                try:
                    error_data = response.json()
                    self.log_test("User Registration", False, 
                                 f"Server error during registration, Response time: {response_time:.2f}s",
                                 {"server_error": error_data})
                except:
                    self.log_test("User Registration", False, 
                                 f"Server error (500), Response time: {response_time:.2f}s",
                                 {"response_text": response.text[:500]})
            else:
                try:
                    error_data = response.json()
                    self.log_test("User Registration", False, 
                                 f"Unexpected status {response.status_code}, Response time: {response_time:.2f}s",
                                 {"error": error_data})
                except:
                    self.log_test("User Registration", False, 
                                 f"Unexpected status {response.status_code}, Response time: {response_time:.2f}s",
                                 {"response_text": response.text[:200]})
        else:
            self.log_test("User Registration", False, 
                         f"No response from server (likely timeout), Response time: {response_time:.2f}s")
        
        return False
    
    def test_user_login_detailed(self):
        """Test user login with the registered user"""
        print("\n=== TESTING USER LOGIN (DETAILED) ===")
        
        if not hasattr(self, 'test_email'):
            self.log_test("User Login", False, "No test user available for login test")
            return False
        
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response, response_time = self.make_request_with_timing("POST", "/auth/login", login_data)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                login_token = data.get("access_token")
                user_data = data.get("user", {})
                
                self.log_test("User Login", True, 
                             f"Login successful! Response time: {response_time:.2f}s")
                
                # Update token for subsequent requests
                self.access_token = login_token
                return True
                
            except json.JSONDecodeError:
                self.log_test("User Login", False, 
                             f"Login returned 200 but invalid JSON, Response time: {response_time:.2f}s")
        else:
            error_msg = "Login failed"
            if response:
                try:
                    error_data = response.json()
                    error_msg = f"Login failed: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"Login failed with status {response.status_code}"
            
            self.log_test("User Login", False, 
                         f"{error_msg}, Response time: {response_time:.2f}s")
        
        return False
    
    def test_protected_routes_access(self):
        """Test access to protected routes with authentication"""
        print("\n=== TESTING PROTECTED ROUTES ACCESS ===")
        
        if not self.access_token:
            self.log_test("Protected Routes", False, "No authentication token available")
            return
        
        # Test /auth/me endpoint
        response, response_time = self.make_request_with_timing("GET", "/auth/me")
        if response and response.status_code == 200:
            try:
                data = response.json()
                email = data.get('email', 'unknown')
                self.log_test("Get Current User", True, 
                             f"User info retrieved: {email}, Response time: {response_time:.2f}s")
            except:
                self.log_test("Get Current User", False, 
                             f"Invalid JSON response, Response time: {response_time:.2f}s")
        else:
            self.log_test("Get Current User", False, 
                         f"Cannot access user info, Response time: {response_time:.2f}s")
        
        # Test categories with authentication
        response, response_time = self.make_request_with_timing("GET", "/categories")
        if response and response.status_code == 200:
            try:
                categories = response.json()
                self.log_test("Categories With Auth", True, 
                             f"Retrieved {len(categories)} categories, Response time: {response_time:.2f}s")
            except:
                self.log_test("Categories With Auth", False, 
                             f"Invalid JSON response, Response time: {response_time:.2f}s")
        else:
            error_msg = "Failed to get categories"
            if response:
                try:
                    error_data = response.json()
                    error_msg = f"Categories failed: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"Categories failed with status {response.status_code}"
            
            self.log_test("Categories With Auth", False, 
                         f"{error_msg}, Response time: {response_time:.2f}s")
    
    def test_database_operations_performance(self):
        """Test database operations performance"""
        print("\n=== TESTING DATABASE OPERATIONS PERFORMANCE ===")
        
        if not self.access_token:
            self.log_test("Database Performance", False, "No authentication token available")
            return
        
        # Test transaction creation
        transaction_data = {
            "type": "expense",
            "category_id": 1,
            "amount": 125.50,
            "description": "Coffee and pastry",
            "date": datetime.now().isoformat(),
            "merchant": "Local Cafe"
        }
        
        response, response_time = self.make_request_with_timing("POST", "/transactions", transaction_data)
        if response and response.status_code == 200:
            try:
                data = response.json()
                transaction_id = data.get("id")
                self.log_test("Create Transaction", True, 
                             f"Transaction created: {transaction_id}, Response time: {response_time:.2f}s")
                
                # Test getting the transaction back
                if transaction_id:
                    response, response_time = self.make_request_with_timing("GET", f"/transactions/{transaction_id}")
                    if response and response.status_code == 200:
                        self.log_test("Retrieve Transaction", True, 
                                     f"Transaction retrieved successfully, Response time: {response_time:.2f}s")
                    else:
                        self.log_test("Retrieve Transaction", False, 
                                     f"Failed to retrieve transaction, Response time: {response_time:.2f}s")
                
            except:
                self.log_test("Create Transaction", False, 
                             f"Invalid JSON response, Response time: {response_time:.2f}s")
        else:
            error_msg = "Failed to create transaction"
            if response:
                try:
                    error_data = response.json()
                    error_msg = f"Transaction creation failed: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"Transaction creation failed with status {response.status_code}"
            
            self.log_test("Create Transaction", False, 
                         f"{error_msg}, Response time: {response_time:.2f}s")
    
    def test_mongodb_atlas_connection_stability(self):
        """Test MongoDB Atlas connection stability with multiple requests"""
        print("\n=== TESTING MONGODB ATLAS CONNECTION STABILITY ===")
        
        stable_connections = 0
        total_tests = 5
        
        for i in range(total_tests):
            print(f"   🔄 Connection test {i+1}/{total_tests}")
            response, response_time = self.make_request_with_timing("GET", "/health")
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('database') == 'connected':
                        stable_connections += 1
                        print(f"   ✅ Connection {i+1} stable ({response_time:.2f}s)")
                    else:
                        print(f"   ❌ Connection {i+1} unstable ({response_time:.2f}s)")
                except:
                    print(f"   ❌ Connection {i+1} invalid response ({response_time:.2f}s)")
            else:
                print(f"   ❌ Connection {i+1} failed ({response_time:.2f}s)")
            
            # Small delay between tests
            time.sleep(1)
        
        stability_rate = (stable_connections / total_tests) * 100
        
        if stability_rate >= 80:
            self.log_test("MongoDB Atlas Stability", True, 
                         f"Connection stable: {stable_connections}/{total_tests} ({stability_rate:.1f}%)")
        else:
            self.log_test("MongoDB Atlas Stability", False, 
                         f"Connection unstable: {stable_connections}/{total_tests} ({stability_rate:.1f}%)")
    
    def run_focused_tests(self):
        """Run focused authentication and database tests"""
        print("🎯 Starting Focused Authentication & Database Testing")
        print(f"🔗 Target: {self.base_url}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Test database connection health first
        db_healthy = self.test_database_connection_health()
        
        # Test MongoDB Atlas connection stability
        self.test_mongodb_atlas_connection_stability()
        
        # Test categories endpoint (requires auth)
        self.test_categories_endpoint_detailed()
        
        # Test user registration (the main issue)
        registration_success = self.test_user_registration_detailed()
        
        if registration_success:
            # Test login with the same user
            login_success = self.test_user_login_detailed()
            
            if login_success:
                # Test protected routes
                self.test_protected_routes_access()
                
                # Test database operations performance
                self.test_database_operations_performance()
        else:
            print("\n⚠️  Skipping authenticated tests due to registration failure")
        
        # Generate focused summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("📊 FOCUSED TEST RESULTS - MONGODB ATLAS USER ROLE UPDATE")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 AUTHENTICATION SYSTEM STATUS:")
        auth_tests = ["User Registration", "User Login", "JWT Token Generation", "Get Current User"]
        for test_name in auth_tests:
            test_result = next((r for r in self.test_results if r["test"] == test_name), None)
            if test_result:
                status = "✅" if test_result["success"] else "❌"
                print(f"   {status} {test_name}")
            else:
                print(f"   ⏸️  {test_name} - Not tested")
        
        print("\n🗄️  DATABASE OPERATIONS STATUS:")
        db_tests = ["Database Health Check", "MongoDB Atlas Stability", "Categories With Auth", "Create Transaction"]
        for test_name in db_tests:
            test_result = next((r for r in self.test_results if r["test"] == test_name), None)
            if test_result:
                status = "✅" if test_result["success"] else "❌"
                print(f"   {status} {test_name}")
            else:
                print(f"   ⏸️  {test_name} - Not tested")
        
        print("\n🎯 MONGODB ATLAS USER ROLE UPDATE ASSESSMENT:")
        
        # Check if the main issues are resolved
        registration_working = any(r["test"] == "User Registration" and r["success"] for r in self.test_results)
        categories_working = any(r["test"] == "Categories With Auth" and r["success"] for r in self.test_results)
        db_stable = any(r["test"] == "MongoDB Atlas Stability" and r["success"] for r in self.test_results)
        
        if registration_working:
            print("   ✅ RESOLVED: User registration timeout issues fixed")
        else:
            print("   ❌ PERSISTS: User registration still failing (likely timeout/connection)")
        
        if categories_working:
            print("   ✅ RESOLVED: Categories endpoint accessible with authentication")
        else:
            print("   ❌ PERSISTS: Categories endpoint still requires authentication fix")
        
        if db_stable:
            print("   ✅ IMPROVED: MongoDB Atlas connection stability good")
        else:
            print("   ❌ PERSISTS: MongoDB Atlas connection stability issues remain")
        
        if failed_tests > 0:
            print("\n🔍 REMAINING ISSUES:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        return passed_tests, failed_tests, total_tests

def main():
    """Main test execution"""
    tester = FocusedAuthTester()
    passed, failed, total = tester.run_focused_tests()
    
    # Exit with appropriate code
    if failed == 0:
        print("\n🎉 All authentication and database tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} tests still failing after MongoDB Atlas user role update.")
        sys.exit(1)

if __name__ == "__main__":
    main()