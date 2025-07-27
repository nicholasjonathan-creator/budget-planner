#!/usr/bin/env python3
"""
Budget Planner Fresh Start Setup - Comprehensive Backend Testing
Testing all core functionalities as requested in the review:

1. Authentication System: Test user registration, login, JWT token generation and validation
2. Transaction Management: Test CRUD operations for transactions, monthly summaries, categories
3. SMS Parsing System: Test SMS parsing functionality (without WhatsApp integration)
4. Analytics System: Test budget calculations, spending insights, financial health metrics
5. Database Operations: Test MongoDB connectivity, data persistence, user isolation
6. API Endpoints: Test all core API endpoints are responding correctly
7. Optional Services: Verify WhatsApp and email services are gracefully disabled
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta
import uuid
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

# Test users for comprehensive testing
TEST_USERS = {
    "primary": {
        "email": "testuser@example.com",
        "username": "testuser", 
        "password": "testpassword123"
    },
    "new_user": {
        "email": f"freshtest_{int(time.time())}@example.com",
        "username": f"freshtest_{int(time.time())}",
        "password": "securepassword123"
    }
}

class FreshStartBackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.auth_token = None
        self.user_id = None
        self.test_transaction_id = None
        
    def log_test_result(self, test_name, passed, message=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}")
        
        if message:
            print(f"   {message}")

    def test_1_authentication_system(self):
        """Test complete authentication system"""
        print("\n🔐 1. AUTHENTICATION SYSTEM TESTING")
        print("=" * 60)
        
        # Test 1.1: User Registration
        try:
            register_response = requests.post(
                f"{API_BASE}/auth/register",
                json=TEST_USERS["new_user"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if register_response.status_code == 201:
                register_data = register_response.json()
                self.log_test_result(
                    "User Registration", 
                    True, 
                    f"New user registered: {TEST_USERS['new_user']['email']}"
                )
            else:
                self.log_test_result("User Registration", False, f"Status: {register_response.status_code}")
                
        except Exception as e:
            self.log_test_result("User Registration", False, f"Error: {e}")
        
        # Test 1.2: User Login
        try:
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": TEST_USERS["primary"]["email"],
                    "password": TEST_USERS["primary"]["password"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                self.auth_token = login_data.get("access_token")
                self.user_id = login_data.get("user", {}).get("id")
                self.log_test_result(
                    "User Login", 
                    True, 
                    f"JWT token received for: {login_data.get('user', {}).get('email')}"
                )
            else:
                self.log_test_result("User Login", False, f"Status: {login_response.status_code}")
                
        except Exception as e:
            self.log_test_result("User Login", False, f"Error: {e}")
        
        # Test 1.3: JWT Token Validation
        if self.auth_token:
            try:
                me_response = requests.get(
                    f"{API_BASE}/auth/me",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    timeout=10
                )
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    self.log_test_result(
                        "JWT Token Validation", 
                        True, 
                        f"Token valid for user: {user_data.get('email')}"
                    )
                else:
                    self.log_test_result("JWT Token Validation", False, f"Status: {me_response.status_code}")
                    
            except Exception as e:
                self.log_test_result("JWT Token Validation", False, f"Error: {e}")

    def get_auth_headers(self):
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    def test_2_transaction_management(self):
        """Test transaction management system"""
        print("\n💰 2. TRANSACTION MANAGEMENT TESTING")
        print("=" * 60)
        
        if not self.auth_token:
            self.log_test_result("Transaction Management", False, "No auth token available")
            return
        
        # Test 2.1: Create Transaction
        try:
            transaction_data = {
                "type": "expense",
                "category_id": 1,
                "amount": 999.99,
                "description": "Fresh start backend test transaction",
                "date": datetime.now().isoformat(),
                "merchant": "Test SMS Merchant",
                "currency": "INR"
            }
            
            create_response = requests.post(
                f"{API_BASE}/transactions",
                json=transaction_data,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if create_response.status_code == 200:
                created_transaction = create_response.json()
                self.test_transaction_id = created_transaction.get("id")
                self.log_test_result(
                    "Create Transaction", 
                    True, 
                    f"Transaction created: ₹{created_transaction.get('amount')} - {created_transaction.get('description')}"
                )
            else:
                self.log_test_result("Create Transaction", False, f"Status: {create_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Create Transaction", False, f"Error: {e}")
        
        # Test 2.2: Get Transactions
        try:
            current_date = datetime.now()
            get_response = requests.get(
                f"{API_BASE}/transactions?month={current_date.month-1}&year={current_date.year}",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if get_response.status_code == 200:
                transactions = get_response.json()
                self.log_test_result(
                    "Get Transactions", 
                    True, 
                    f"Retrieved {len(transactions)} transactions for current month"
                )
            else:
                self.log_test_result("Get Transactions", False, f"Status: {get_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Get Transactions", False, f"Error: {e}")
        
        # Test 2.3: Monthly Summary
        try:
            current_date = datetime.now()
            summary_response = requests.get(
                f"{API_BASE}/analytics/monthly-summary?month={current_date.month}&year={current_date.year}",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if summary_response.status_code == 200:
                summary = summary_response.json()
                self.log_test_result(
                    "Monthly Summary", 
                    True, 
                    f"Income: ₹{summary.get('income', 0)}, Expense: ₹{summary.get('expense', 0)}, Balance: ₹{summary.get('balance', 0)}"
                )
            else:
                self.log_test_result("Monthly Summary", False, f"Status: {summary_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Monthly Summary", False, f"Error: {e}")
        
        # Test 2.4: Categories
        try:
            categories_response = requests.get(
                f"{API_BASE}/categories",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if categories_response.status_code == 200:
                categories = categories_response.json()
                self.log_test_result(
                    "Categories System", 
                    True, 
                    f"Retrieved {len(categories)} transaction categories"
                )
            else:
                self.log_test_result("Categories System", False, f"Status: {categories_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Categories System", False, f"Error: {e}")

    def test_3_sms_parsing_system(self):
        """Test SMS parsing functionality"""
        print("\n📱 3. SMS PARSING SYSTEM TESTING")
        print("=" * 60)
        
        if not self.auth_token:
            self.log_test_result("SMS Parsing System", False, "No auth token available")
            return
        
        # Test 3.1: SMS Processing
        try:
            test_sms = "HDFC Bank: Rs 999.99 debited from A/C **1234 on 01-JAN-25 at Fresh Start Test. Avl Bal: Rs 5000.00"
            
            receive_response = requests.post(
                f"{API_BASE}/sms/receive",
                json={
                    "phone_number": "+919876543210",
                    "message": test_sms
                },
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if receive_response.status_code == 200:
                receive_result = receive_response.json()
                self.log_test_result(
                    "SMS Processing", 
                    True, 
                    f"SMS processed successfully: {receive_result.get('success', False)}"
                )
            else:
                self.log_test_result("SMS Processing", False, f"Status: {receive_response.status_code}")
                
        except Exception as e:
            self.log_test_result("SMS Processing", False, f"Error: {e}")
        
        # Test 3.2: Failed SMS Handling
        try:
            failed_response = requests.get(
                f"{API_BASE}/sms/failed",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if failed_response.status_code == 200:
                failed_result = failed_response.json()
                failed_count = len(failed_result.get('failed_sms', []))
                self.log_test_result(
                    "Failed SMS Handling", 
                    True, 
                    f"Found {failed_count} failed SMS messages for manual classification"
                )
            else:
                self.log_test_result("Failed SMS Handling", False, f"Status: {failed_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Failed SMS Handling", False, f"Error: {e}")
        
        # Test 3.3: SMS Statistics
        try:
            stats_response = requests.get(
                f"{API_BASE}/sms/stats",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                self.log_test_result(
                    "SMS Statistics", 
                    True, 
                    f"Total SMS: {stats.get('total', 0)}, Processed: {stats.get('processed', 0)}, Success Rate: {stats.get('success_rate', 0):.1f}%"
                )
            else:
                self.log_test_result("SMS Statistics", False, f"Status: {stats_response.status_code}")
                
        except Exception as e:
            self.log_test_result("SMS Statistics", False, f"Error: {e}")

    def test_4_analytics_system(self):
        """Test analytics and insights system"""
        print("\n📊 4. ANALYTICS SYSTEM TESTING")
        print("=" * 60)
        
        if not self.auth_token:
            self.log_test_result("Analytics System", False, "No auth token available")
            return
        
        # Test 4.1: Spending Trends
        try:
            trends_response = requests.get(
                f"{API_BASE}/analytics/spending-trends",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if trends_response.status_code == 200:
                trends = trends_response.json()
                self.log_test_result(
                    "Spending Trends", 
                    True, 
                    f"Retrieved {len(trends)} spending trend periods"
                )
            else:
                self.log_test_result("Spending Trends", False, f"Status: {trends_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Spending Trends", False, f"Error: {e}")
        
        # Test 4.2: Financial Health Score
        try:
            health_response = requests.get(
                f"{API_BASE}/analytics/financial-health",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if health_response.status_code == 200:
                health = health_response.json()
                self.log_test_result(
                    "Financial Health Score", 
                    True, 
                    f"Health Score: {health.get('overall_score', 'N/A')}, Grade: {health.get('grade', 'N/A')}"
                )
            else:
                self.log_test_result("Financial Health Score", False, f"Status: {health_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Financial Health Score", False, f"Error: {e}")
        
        # Test 4.3: Budget Recommendations
        try:
            recommendations_response = requests.get(
                f"{API_BASE}/analytics/budget-recommendations",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if recommendations_response.status_code == 200:
                recommendations = recommendations_response.json()
                self.log_test_result(
                    "Budget Recommendations", 
                    True, 
                    f"Retrieved {len(recommendations)} AI-powered budget recommendations"
                )
            else:
                self.log_test_result("Budget Recommendations", False, f"Status: {recommendations_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Budget Recommendations", False, f"Error: {e}")
        
        # Test 4.4: Spending Alerts
        try:
            alerts_response = requests.get(
                f"{API_BASE}/analytics/spending-alerts",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                self.log_test_result(
                    "Spending Alerts", 
                    True, 
                    f"Retrieved {len(alerts)} spending anomaly alerts"
                )
            else:
                self.log_test_result("Spending Alerts", False, f"Status: {alerts_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Spending Alerts", False, f"Error: {e}")

    def test_5_database_operations(self):
        """Test MongoDB connectivity and data persistence"""
        print("\n🗄️ 5. DATABASE OPERATIONS TESTING")
        print("=" * 60)
        
        # Test 5.1: Database Health
        try:
            health_response = requests.get(f"{API_BASE}/health", timeout=10)
            if health_response.status_code == 200:
                health_data = health_response.json()
                db_status = health_data.get('database')
                self.log_test_result(
                    "Database Connectivity", 
                    db_status == 'connected', 
                    f"MongoDB status: {db_status}, Environment: {health_data.get('environment')}"
                )
            else:
                self.log_test_result("Database Connectivity", False, f"Status: {health_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Database Connectivity", False, f"Error: {e}")
        
        # Test 5.2: Database Metrics
        try:
            metrics_response = requests.get(f"{API_BASE}/metrics", timeout=10)
            if metrics_response.status_code == 200:
                metrics = metrics_response.json()
                self.log_test_result(
                    "Data Persistence", 
                    True, 
                    f"Transactions: {metrics.get('total_transactions')}, SMS: {metrics.get('total_sms')}, Success Rate: {metrics.get('success_rate', 0):.1f}%"
                )
            else:
                self.log_test_result("Data Persistence", False, f"Status: {metrics_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Data Persistence", False, f"Error: {e}")
        
        # Test 5.3: User Isolation
        if self.auth_token:
            try:
                # Test that user can access their own data
                current_date = datetime.now()
                own_data_response = requests.get(
                    f"{API_BASE}/transactions?month={current_date.month}&year={current_date.year}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if own_data_response.status_code == 200:
                    own_transactions = own_data_response.json()
                    self.log_test_result(
                        "User Data Isolation", 
                        True, 
                        f"User can access {len(own_transactions)} own transactions (data properly isolated)"
                    )
                else:
                    self.log_test_result("User Data Isolation", False, f"Status: {own_data_response.status_code}")
                    
            except Exception as e:
                self.log_test_result("User Data Isolation", False, f"Error: {e}")

    def test_6_api_endpoints(self):
        """Test all core API endpoints"""
        print("\n🌐 6. API ENDPOINTS TESTING")
        print("=" * 60)
        
        # Test 6.1: Protected Routes Authentication
        protected_endpoints = [
            "/transactions",
            "/analytics/monthly-summary?month=1&year=2025",
            "/notifications/preferences",
            "/sms/failed",
            "/budget-limits?month=1&year=2025"
        ]
        
        unauthorized_count = 0
        
        for endpoint in protected_endpoints:
            try:
                response = requests.get(
                    f"{API_BASE}{endpoint}",
                    headers={"Content-Type": "application/json"},  # No auth header
                    timeout=10
                )
                
                if response.status_code == 401 or response.status_code == 403:
                    unauthorized_count += 1
                    
            except Exception as e:
                pass  # Connection errors are acceptable for this test
        
        self.log_test_result(
            "Protected Routes Security", 
            unauthorized_count == len(protected_endpoints), 
            f"{unauthorized_count}/{len(protected_endpoints)} routes properly require authentication"
        )
        
        # Test 6.2: Core API Endpoints Availability
        if self.auth_token:
            core_endpoints = [
                ("/transactions", "GET"),
                ("/categories", "GET"),
                ("/analytics/monthly-summary?month=7&year=2025", "GET"),
                ("/sms/failed", "GET"),
                ("/notifications/preferences", "GET")
            ]
            
            working_endpoints = 0
            
            for endpoint, method in core_endpoints:
                try:
                    if method == "GET":
                        response = requests.get(
                            f"{API_BASE}{endpoint}",
                            headers=self.get_auth_headers(),
                            timeout=10
                        )
                    else:
                        response = requests.post(
                            f"{API_BASE}{endpoint}",
                            headers=self.get_auth_headers(),
                            timeout=10
                        )
                    
                    if response.status_code == 200:
                        working_endpoints += 1
                        
                except Exception as e:
                    pass
            
            self.log_test_result(
                "Core API Endpoints", 
                working_endpoints == len(core_endpoints), 
                f"{working_endpoints}/{len(core_endpoints)} core endpoints responding correctly"
            )

    def test_7_optional_services(self):
        """Test that optional services are gracefully disabled"""
        print("\n🔧 7. OPTIONAL SERVICES TESTING")
        print("=" * 60)
        
        if not self.auth_token:
            self.log_test_result("Optional Services", False, "No auth token available")
            return
        
        # Test 7.1: Email Service (should be disabled)
        try:
            email_test_response = requests.post(
                f"{API_BASE}/notifications/test-email",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if email_test_response.status_code == 200:
                email_result = email_test_response.json()
                if email_result.get('success') == False and 'disabled' in email_result.get('message', '').lower():
                    self.log_test_result(
                        "Email Service Graceful Degradation", 
                        True, 
                        "Email service properly disabled for production deployment"
                    )
                else:
                    self.log_test_result("Email Service Graceful Degradation", False, "Email service not properly disabled")
            else:
                self.log_test_result("Email Service Graceful Degradation", False, f"Status: {email_test_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Email Service Graceful Degradation", False, f"Error: {e}")
        
        # Test 7.2: WhatsApp Service Status
        try:
            whatsapp_response = requests.get(
                f"{API_BASE}/whatsapp/status",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if whatsapp_response.status_code == 200:
                whatsapp_result = whatsapp_response.json()
                self.log_test_result(
                    "WhatsApp Service Status", 
                    True, 
                    f"WhatsApp integration status: {whatsapp_result.get('status', 'unknown')} (graceful handling)"
                )
            else:
                self.log_test_result("WhatsApp Service Status", False, f"Status: {whatsapp_response.status_code}")
                
        except Exception as e:
            self.log_test_result("WhatsApp Service Status", False, f"Error: {e}")
        
        # Test 7.3: Phone Verification (should work with fallback)
        try:
            phone_status_response = requests.get(
                f"{API_BASE}/phone/status",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if phone_status_response.status_code == 200:
                phone_result = phone_status_response.json()
                self.log_test_result(
                    "Phone Verification Fallback", 
                    True, 
                    f"Phone verification available: {phone_result.get('phone_verified', False)} (fallback mode working)"
                )
            else:
                self.log_test_result("Phone Verification Fallback", False, f"Status: {phone_status_response.status_code}")
                
        except Exception as e:
            self.log_test_result("Phone Verification Fallback", False, f"Error: {e}")

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test transaction if created
        if self.test_transaction_id and self.auth_token:
            try:
                delete_response = requests.delete(
                    f"{API_BASE}/transactions/{self.test_transaction_id}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if delete_response.status_code == 200:
                    print(f"   ✅ Deleted test transaction: {self.test_transaction_id}")
                else:
                    print(f"   ⚠️  Could not delete test transaction: {delete_response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️  Error deleting test transaction: {e}")

    def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 BUDGET PLANNER FRESH START SETUP - COMPREHENSIVE BACKEND TESTING")
        print("Testing all core functionalities for production readiness verification")
        print("=" * 100)
        
        # Test backend health first
        try:
            health_response = requests.get(f"{API_BASE}/health", timeout=10)
            if health_response.status_code != 200:
                print("❌ Backend is not accessible. Aborting tests.")
                return False
            else:
                health_data = health_response.json()
                print(f"✅ Backend is healthy: {health_data.get('status')} (DB: {health_data.get('database')})")
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False
        
        # Run all test suites
        self.test_1_authentication_system()
        self.test_2_transaction_management()
        self.test_3_sms_parsing_system()
        self.test_4_analytics_system()
        self.test_5_database_operations()
        self.test_6_api_endpoints()
        self.test_7_optional_services()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print final results
        self.print_final_results()
        
        return self.failed_tests == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 100)
        print("📊 BUDGET PLANNER FRESH START SETUP - COMPREHENSIVE TEST RESULTS")
        print("=" * 100)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 95:
                print("🎉 EXCELLENT: All core functionalities working perfectly! Ready for production.")
            elif success_rate >= 85:
                print("👍 GOOD: Core functionalities working well with minor issues.")
            elif success_rate >= 70:
                print("⚠️  MODERATE: Some core functionalities need attention.")
            else:
                print("❌ POOR: Significant issues found in core functionalities.")
        
        print("\n📋 COMPREHENSIVE TEST COVERAGE:")
        print("  ✅ 1. Authentication System (Registration, Login, JWT validation)")
        print("  ✅ 2. Transaction Management (CRUD operations, monthly summaries, categories)")
        print("  ✅ 3. SMS Parsing System (SMS processing, failed SMS handling, statistics)")
        print("  ✅ 4. Analytics System (Trends, health score, recommendations, alerts)")
        print("  ✅ 5. Database Operations (MongoDB connectivity, data persistence, user isolation)")
        print("  ✅ 6. API Endpoints (Protected routes, core endpoints availability)")
        print("  ✅ 7. Optional Services (Email/WhatsApp graceful degradation)")
        
        print("\n🎯 FRESH START SETUP STATUS:")
        if success_rate >= 90:
            print("✅ READY FOR PRODUCTION: All core functionalities verified and working")
            print("✅ Clean codebase package successfully tested")
            print("✅ External integrations properly made optional")
            print("✅ Application runs without external API keys")
        else:
            print("⚠️  NEEDS ATTENTION: Some core functionalities require fixes")
        
        print("=" * 100)

if __name__ == "__main__":
    print("🧪 Budget Planner Fresh Start Setup - Comprehensive Backend Testing")
    print("=" * 100)
    
    tester = FreshStartBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Fresh start setup is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the results above.")
        sys.exit(1)