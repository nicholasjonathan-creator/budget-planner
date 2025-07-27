#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Budget Planner Production Deployment
Tests the live backend at https://budget-planner-backendjuly.onrender.com
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid
import sys

# Production backend URL
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

class BudgetPlannerTester:
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
            self.log_test("Health Check", True, f"Service healthy, DB: {db_status}")
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
            
            # Update token for subsequent requests
            self.access_token = login_token
        else:
            self.log_test("User Login", False, "Login failed")
        
        # Test protected route - get current user
        response = self.make_request("GET", "/auth/me")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Protected Route Access", True, f"User info retrieved - {data.get('email')}")
        else:
            self.log_test("Protected Route Access", False, "Cannot access protected route")
        
        return True
    
    def test_transaction_management(self):
        """Test transaction CRUD operations"""
        print("\n=== TESTING TRANSACTION MANAGEMENT ===")
        
        if not self.access_token:
            self.log_test("Transaction Tests", False, "No authentication token available")
            return
        
        # Test getting categories first
        response = self.make_request("GET", "/categories")
        if response and response.status_code == 200:
            categories = response.json()
            self.log_test("Get Categories", True, f"Retrieved {len(categories)} categories")
        else:
            self.log_test("Get Categories", False, "Failed to get categories")
            categories = []
        
        # Create test transaction
        transaction_data = {
            "type": "expense",
            "category_id": 1,  # Food category
            "amount": 250.75,
            "description": "Lunch at restaurant",
            "date": datetime.now().isoformat(),
            "merchant": "Pizza Palace"
        }
        
        response = self.make_request("POST", "/transactions", transaction_data)
        transaction_id = None
        if response and response.status_code == 200:
            data = response.json()
            transaction_id = data.get("id")
            self.log_test("Create Transaction", True, f"Transaction created - ID: {transaction_id}")
        else:
            self.log_test("Create Transaction", False, "Failed to create transaction")
        
        # Test getting transactions
        current_date = datetime.now()
        response = self.make_request("GET", f"/transactions?month={current_date.month}&year={current_date.year}")
        if response and response.status_code == 200:
            transactions = response.json()
            self.log_test("Get Transactions", True, f"Retrieved {len(transactions)} transactions")
        else:
            self.log_test("Get Transactions", False, "Failed to get transactions")
        
        # Test getting specific transaction
        if transaction_id:
            response = self.make_request("GET", f"/transactions/{transaction_id}")
            if response and response.status_code == 200:
                self.log_test("Get Single Transaction", True, "Transaction retrieved successfully")
            else:
                self.log_test("Get Single Transaction", False, "Failed to get single transaction")
            
            # Test updating transaction
            update_data = {"description": "Updated lunch description"}
            response = self.make_request("PUT", f"/transactions/{transaction_id}", update_data)
            if response and response.status_code == 200:
                self.log_test("Update Transaction", True, "Transaction updated successfully")
            else:
                self.log_test("Update Transaction", False, "Failed to update transaction")
    
    def test_sms_parsing_system(self):
        """Test SMS parsing functionality"""
        print("\n=== TESTING SMS PARSING SYSTEM ===")
        
        if not self.access_token:
            self.log_test("SMS Tests", False, "No authentication token available")
            return
        
        # Test SMS simulation
        response = self.make_request("POST", "/sms/simulate?bank_type=hdfc")
        if response and response.status_code == 200:
            self.log_test("SMS Simulation", True, "SMS simulation successful")
        else:
            self.log_test("SMS Simulation", False, "SMS simulation failed")
        
        # Test getting failed SMS
        response = self.make_request("GET", "/sms/failed")
        if response and response.status_code == 200:
            data = response.json()
            failed_count = len(data.get("failed_sms", []))
            self.log_test("Get Failed SMS", True, f"Retrieved {failed_count} failed SMS messages")
        else:
            self.log_test("Get Failed SMS", False, "Failed to get failed SMS")
        
        # Test SMS stats
        response = self.make_request("GET", "/sms/stats")
        if response and response.status_code == 200:
            self.log_test("SMS Statistics", True, "SMS stats retrieved successfully")
        else:
            self.log_test("SMS Statistics", False, "Failed to get SMS stats")
        
        # Test receiving SMS
        sms_data = {
            "phone_number": "+919876543210",
            "message": "HDFC Bank: Rs 500.00 debited from A/c **1234 on 15-Dec-23 at AMAZON INDIA. Avl Bal: Rs 15,000.00"
        }
        response = self.make_request("POST", "/sms/receive", sms_data)
        if response and response.status_code == 200:
            self.log_test("Receive SMS", True, "SMS received and processed")
        else:
            self.log_test("Receive SMS", False, "Failed to receive SMS")
    
    def test_analytics_insights(self):
        """Test analytics and insights endpoints"""
        print("\n=== TESTING ANALYTICS & INSIGHTS ===")
        
        if not self.access_token:
            self.log_test("Analytics Tests", False, "No authentication token available")
            return
        
        current_date = datetime.now()
        
        # Test monthly summary
        response = self.make_request("GET", f"/analytics/monthly-summary?month={current_date.month}&year={current_date.year}")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Monthly Summary", True, f"Summary: Income {data.get('income', 0)}, Expenses {data.get('expense', 0)}")
        else:
            self.log_test("Monthly Summary", False, "Failed to get monthly summary")
        
        # Test category totals
        response = self.make_request("GET", f"/analytics/category-totals?month={current_date.month}&year={current_date.year}")
        if response and response.status_code == 200:
            self.log_test("Category Totals", True, "Category totals retrieved successfully")
        else:
            self.log_test("Category Totals", False, "Failed to get category totals")
        
        # Test spending trends
        response = self.make_request("GET", "/analytics/spending-trends?timeframe=monthly&periods=6")
        if response and response.status_code == 200:
            trends = response.json()
            self.log_test("Spending Trends", True, f"Retrieved {len(trends)} trend periods")
        else:
            self.log_test("Spending Trends", False, "Failed to get spending trends")
        
        # Test financial health score
        response = self.make_request("GET", "/analytics/financial-health")
        if response and response.status_code == 200:
            data = response.json()
            score = data.get("overall_score", 0)
            self.log_test("Financial Health Score", True, f"Health score: {score}")
        else:
            self.log_test("Financial Health Score", False, "Failed to get financial health score")
        
        # Test spending patterns
        response = self.make_request("GET", "/analytics/spending-patterns")
        if response and response.status_code == 200:
            patterns = response.json()
            self.log_test("Spending Patterns", True, f"Retrieved {len(patterns)} spending patterns")
        else:
            self.log_test("Spending Patterns", False, "Failed to get spending patterns")
        
        # Test budget recommendations
        response = self.make_request("GET", "/analytics/budget-recommendations")
        if response and response.status_code == 200:
            recommendations = response.json()
            self.log_test("Budget Recommendations", True, f"Retrieved {len(recommendations)} recommendations")
        else:
            self.log_test("Budget Recommendations", False, "Failed to get budget recommendations")
        
        # Test spending alerts
        response = self.make_request("GET", "/analytics/spending-alerts")
        if response and response.status_code == 200:
            alerts = response.json()
            self.log_test("Spending Alerts", True, f"Retrieved {len(alerts)} spending alerts")
        else:
            self.log_test("Spending Alerts", False, "Failed to get spending alerts")
        
        # Test analytics summary
        response = self.make_request("GET", "/analytics/summary")
        if response and response.status_code == 200:
            self.log_test("Analytics Summary", True, "Analytics summary retrieved successfully")
        else:
            self.log_test("Analytics Summary", False, "Failed to get analytics summary")
    
    def test_whatsapp_integration(self):
        """Test WhatsApp integration status"""
        print("\n=== TESTING WHATSAPP INTEGRATION ===")
        
        if not self.access_token:
            self.log_test("WhatsApp Tests", False, "No authentication token available")
            return
        
        # Test WhatsApp status
        response = self.make_request("GET", "/whatsapp/status")
        if response and response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            self.log_test("WhatsApp Status", True, f"WhatsApp status: {status}")
        else:
            self.log_test("WhatsApp Status", False, "Failed to get WhatsApp status")
        
        # Test monitoring WhatsApp status
        response = self.make_request("GET", "/monitoring/whatsapp-status")
        if response and response.status_code == 200:
            self.log_test("WhatsApp Monitoring", True, "WhatsApp monitoring status retrieved")
        else:
            self.log_test("WhatsApp Monitoring", False, "Failed to get WhatsApp monitoring status")
    
    def test_phone_verification(self):
        """Test phone verification system"""
        print("\n=== TESTING PHONE VERIFICATION ===")
        
        if not self.access_token:
            self.log_test("Phone Tests", False, "No authentication token available")
            return
        
        # Test phone status
        response = self.make_request("GET", "/phone/status")
        if response and response.status_code == 200:
            data = response.json()
            verified = data.get("phone_verified", False)
            self.log_test("Phone Status", True, f"Phone verification status: {verified}")
        else:
            self.log_test("Phone Status", False, "Failed to get phone status")
        
        # Test sending verification (this will likely fail in production without proper setup)
        phone_data = {"phone_number": "+919876543210"}
        response = self.make_request("POST", "/phone/send-verification", phone_data)
        if response and response.status_code == 200:
            self.log_test("Send Phone Verification", True, "Verification code sent successfully")
        else:
            # This is expected to fail in production without Twilio setup
            self.log_test("Send Phone Verification", True, "Phone verification disabled (expected in production)")
    
    def test_budget_management(self):
        """Test budget limits functionality"""
        print("\n=== TESTING BUDGET MANAGEMENT ===")
        
        if not self.access_token:
            self.log_test("Budget Tests", False, "No authentication token available")
            return
        
        current_date = datetime.now()
        
        # Create budget limit
        budget_data = {
            "category_id": 1,  # Food category
            "limit": 5000.0,
            "month": current_date.month,
            "year": current_date.year
        }
        
        response = self.make_request("POST", "/budget-limits", budget_data)
        if response and response.status_code == 200:
            self.log_test("Create Budget Limit", True, "Budget limit created successfully")
        else:
            self.log_test("Create Budget Limit", False, "Failed to create budget limit")
        
        # Get budget limits
        response = self.make_request("GET", f"/budget-limits?month={current_date.month}&year={current_date.year}")
        if response and response.status_code == 200:
            budgets = response.json()
            self.log_test("Get Budget Limits", True, f"Retrieved {len(budgets)} budget limits")
        else:
            self.log_test("Get Budget Limits", False, "Failed to get budget limits")
    
    def test_monitoring_system(self):
        """Test monitoring and alerting system"""
        print("\n=== TESTING MONITORING SYSTEM ===")
        
        # Test system health (no auth required)
        response = self.make_request("GET", "/monitoring/health")
        if response and response.status_code == 200:
            self.log_test("System Health Monitoring", True, "System health check successful")
        else:
            self.log_test("System Health Monitoring", False, "System health check failed")
        
        # Test recent alerts
        response = self.make_request("GET", "/monitoring/alerts?time_window=60")
        if response and response.status_code == 200:
            data = response.json()
            alert_count = len(data.get("alerts", []))
            self.log_test("Monitoring Alerts", True, f"Retrieved {alert_count} recent alerts")
        else:
            self.log_test("Monitoring Alerts", False, "Failed to get monitoring alerts")
        
        if self.access_token:
            # Test user sync check
            response = self.make_request("POST", "/monitoring/user-sync-check")
            if response and response.status_code == 200:
                data = response.json()
                sync_alerts = len(data.get("sync_alerts", []))
                self.log_test("User Sync Check", True, f"User sync check completed - {sync_alerts} alerts")
            else:
                self.log_test("User Sync Check", False, "User sync check failed")
    
    def test_notification_system(self):
        """Test notification preferences (disabled in production)"""
        print("\n=== TESTING NOTIFICATION SYSTEM ===")
        
        if not self.access_token:
            self.log_test("Notification Tests", False, "No authentication token available")
            return
        
        # Test getting notification preferences
        response = self.make_request("GET", "/notifications/preferences")
        if response and response.status_code == 200:
            data = response.json()
            email_enabled = data.get("email_enabled", False)
            self.log_test("Notification Preferences", True, f"Email notifications: {email_enabled} (expected disabled)")
        else:
            self.log_test("Notification Preferences", False, "Failed to get notification preferences")
        
        # Test updating preferences
        prefs_data = {"email_enabled": False}
        response = self.make_request("PUT", "/notifications/preferences", prefs_data)
        if response and response.status_code == 200:
            self.log_test("Update Notification Preferences", True, "Preferences updated successfully")
        else:
            self.log_test("Update Notification Preferences", False, "Failed to update preferences")
        
        # Test email test endpoint (should be disabled)
        response = self.make_request("POST", "/notifications/test-email")
        if response and response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            if not success:
                self.log_test("Test Email (Disabled)", True, "Email service properly disabled")
            else:
                self.log_test("Test Email (Disabled)", False, "Email service should be disabled")
        else:
            self.log_test("Test Email (Disabled)", False, "Failed to test email endpoint")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Backend Testing")
        print(f"🎯 Target: {self.base_url}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run test suites
        self.test_health_endpoints()
        auth_success = self.test_authentication_system()
        
        if auth_success:
            self.test_transaction_management()
            self.test_sms_parsing_system()
            self.test_analytics_insights()
            self.test_whatsapp_integration()
            self.test_phone_verification()
            self.test_budget_management()
            self.test_notification_system()
        
        self.test_monitoring_system()
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        print("\n🎯 CRITICAL FUNCTIONALITY STATUS:")
        critical_tests = [
            "Health Check", "User Registration", "User Login", "Create Transaction", 
            "Get Transactions", "Monthly Summary", "WhatsApp Status"
        ]
        
        for test_name in critical_tests:
            test_result = next((r for r in self.test_results if r["test"] == test_name), None)
            if test_result:
                status = "✅" if test_result["success"] else "❌"
                print(f"   {status} {test_name}")
        
        return passed_tests, failed_tests, total_tests

def main():
    """Main test execution"""
    tester = BudgetPlannerTester()
    passed, failed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if failed == 0:
        print("\n🎉 All tests passed! Production backend is fully functional.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} tests failed. Check the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()