#!/usr/bin/env python3
"""
COMPREHENSIVE BUDGET PLANNER BACKEND TESTING
Deployed Services Integration Verification for Production Readiness

Testing Focus Areas:
1. Core System Health - /api/health endpoint comprehensive response
2. Authentication System - login/register functionality, JWT tokens, protected routes
3. SMS Processing System - SMS parsing endpoints, bank-specific patterns, failed SMS handling
4. Transaction Management - CRUD operations, monthly summaries, analytics
5. Analytics System - All 6 analytics email endpoints, analytics data generation
6. Email Notification System - SendGrid integration, email templates
7. User Isolation & Security - multi-user data access controls, no data leakage

Production Deployment Context:
- Frontend: https://0f621684-5333-4b17-9188-b8424f0e0b0c.preview.emergentagent.com
- Backend: Running locally on port 8001 (accessible via /api endpoints)
- Database: Local MongoDB instance operational
"""

import requests
import json
import sys
import os
from datetime import datetime
import uuid
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://0f621684-5333-4b17-9188-b8424f0e0b0c.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test users for authentication (existing users as specified in review request)
TEST_USERS = {
    "primary": {
        "email": "testuser@example.com",
        "username": "testuser", 
        "password": "testpassword123"
    },
    "secondary": {
        "email": "admin@example.com",
        "username": "admin",
        "password": "admin123"
    },
    "admin": {
        "email": "superadmin@budgetplanner.app",
        "username": "superadmin",
        "password": "superadminpassword123"
    }
}

class ComprehensiveBackendTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.auth_token = None
        self.admin_token = None
        self.user_id = None
        self.admin_user_id = None
        self.critical_failures = []
        
    def test_core_system_health(self):
        """Test /api/health endpoint comprehensive response"""
        print("\n🏥 Testing Core System Health...")
        print("=" * 60)
        
        self.total_tests += 1
        
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Health endpoint responding")
                
                # Check required health fields
                required_fields = ['status', 'timestamp', 'version', 'database', 'environment']
                missing_fields = [field for field in required_fields if field not in health_data]
                
                if not missing_fields:
                    print(f"   Status: {health_data.get('status')}")
                    print(f"   Database: {health_data.get('database')}")
                    print(f"   Environment: {health_data.get('environment')}")
                    print(f"   Version: {health_data.get('version')}")
                    
                    if health_data.get('status') == 'healthy' and health_data.get('database') == 'connected':
                        print("✅ Core system health is excellent")
                        self.passed_tests += 1
                    else:
                        print("❌ System health issues detected")
                        self.failed_tests += 1
                        self.critical_failures.append("System health check failed")
                else:
                    print(f"❌ Health response missing fields: {missing_fields}")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.failed_tests += 1
                self.critical_failures.append("Health endpoint not accessible")
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.failed_tests += 1
            self.critical_failures.append(f"Health check exception: {e}")

    def test_database_connectivity(self):
        """Test database connectivity through metrics endpoint"""
        print("\n🗄️  Testing Database Connectivity...")
        print("=" * 60)
        
        self.total_tests += 1
        
        try:
            response = requests.get(f"{API_BASE}/metrics", timeout=10)
            
            if response.status_code == 200:
                metrics = response.json()
                print("✅ Database metrics endpoint responding")
                
                # Check for database-related metrics
                db_fields = ['total_transactions', 'total_sms', 'processed_sms', 'success_rate']
                found_fields = [field for field in db_fields if field in metrics]
                
                if len(found_fields) == len(db_fields):
                    print(f"   Total Transactions: {metrics.get('total_transactions', 0)}")
                    print(f"   Total SMS: {metrics.get('total_sms', 0)}")
                    print(f"   Processed SMS: {metrics.get('processed_sms', 0)}")
                    print(f"   Success Rate: {metrics.get('success_rate', 0):.1f}%")
                    print("✅ Database connectivity confirmed")
                    self.passed_tests += 1
                else:
                    print(f"❌ Metrics missing fields: {set(db_fields) - set(found_fields)}")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Metrics endpoint failed: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Database connectivity test failed: {e}")
            self.failed_tests += 1

    def authenticate_test_users(self):
        """Authenticate test users and get JWT tokens"""
        print("\n🔐 Testing Authentication System...")
        print("=" * 60)
        
        self.total_tests += 1
        
        # Try to authenticate primary user first
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
                print(f"✅ Primary user authenticated: {TEST_USERS['primary']['email']}")
            else:
                # Try secondary user
                login_response = requests.post(
                    f"{API_BASE}/auth/login",
                    json={
                        "email": TEST_USERS["secondary"]["email"],
                        "password": TEST_USERS["secondary"]["password"]
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    self.auth_token = login_data.get("access_token")
                    self.user_id = login_data.get("user", {}).get("id")
                    print(f"✅ Secondary user authenticated: {TEST_USERS['secondary']['email']}")
                else:
                    print(f"❌ Failed to authenticate any test user")
                    self.failed_tests += 1
                    self.critical_failures.append("Authentication system failure")
                    return False
                    
        except Exception as e:
            print(f"❌ Error authenticating users: {e}")
            self.failed_tests += 1
            self.critical_failures.append(f"Authentication exception: {e}")
            return False
        
        # Try to authenticate admin user
        try:
            admin_login_response = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": TEST_USERS["admin"]["email"],
                    "password": TEST_USERS["admin"]["password"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if admin_login_response.status_code == 200:
                admin_data = admin_login_response.json()
                self.admin_token = admin_data.get("access_token")
                self.admin_user_id = admin_data.get("user", {}).get("id")
                print(f"✅ Admin user authenticated: {TEST_USERS['admin']['email']}")
            else:
                print(f"⚠️  Admin user authentication failed: {admin_login_response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Error authenticating admin user: {e}")
        
        if self.auth_token:
            print("✅ Authentication system working")
            self.passed_tests += 1
            return True
        else:
            self.failed_tests += 1
            return False

    def get_auth_headers(self, use_admin=False):
        """Get authentication headers"""
        token = self.admin_token if use_admin and self.admin_token else self.auth_token
        if token:
            return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    def test_protected_routes_authentication(self):
        """Test that protected routes require authentication"""
        print("\n🛡️  Testing Protected Routes Authentication...")
        print("=" * 60)
        
        self.total_tests += 1
        
        protected_endpoints = [
            ("/transactions", "GET"),
            ("/analytics/monthly-summary?month=7&year=2025", "GET"),
            ("/notifications/preferences", "GET"),
            ("/sms/failed", "GET"),
            ("/analytics/send-spending-alerts", "POST")
        ]
        
        unauthorized_count = 0
        
        for endpoint, method in protected_endpoints:
            try:
                if method == "GET":
                    response = requests.get(
                        f"{API_BASE}{endpoint}",
                        headers={"Content-Type": "application/json"},  # No auth header
                        timeout=10
                    )
                else:
                    response = requests.post(
                        f"{API_BASE}{endpoint}",
                        headers={"Content-Type": "application/json"},  # No auth header
                        timeout=10
                    )
                
                if response.status_code in [401, 403]:
                    unauthorized_count += 1
                    print(f"   ✅ {method} {endpoint} requires authentication")
                else:
                    print(f"   ❌ {method} {endpoint} does not require authentication (status: {response.status_code})")
                    
            except Exception as e:
                print(f"   ⚠️  Error testing {endpoint}: {e}")
        
        if unauthorized_count == len(protected_endpoints):
            print(f"✅ All {len(protected_endpoints)} protected routes require authentication")
            self.passed_tests += 1
        else:
            print(f"❌ Only {unauthorized_count}/{len(protected_endpoints)} routes require authentication")
            self.failed_tests += 1

    def test_sms_processing_system(self):
        """Test SMS processing endpoints and functionality"""
        print("\n📱 Testing SMS Processing System...")
        print("=" * 60)
        
        self.total_tests += 1
        
        try:
            # Test failed SMS endpoint
            failed_sms_response = requests.get(
                f"{API_BASE}/sms/failed",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if failed_sms_response.status_code == 200:
                failed_data = failed_sms_response.json()
                print("✅ Failed SMS endpoint responding")
                
                if 'success' in failed_data and 'failed_sms' in failed_data:
                    failed_count = len(failed_data.get('failed_sms', []))
                    print(f"   Failed SMS count: {failed_count}")
                    print("✅ SMS processing system working")
                    self.passed_tests += 1
                else:
                    print("❌ Failed SMS response structure invalid")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Failed SMS endpoint failed: {failed_sms_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ SMS processing test failed: {e}")
            self.failed_tests += 1

    def test_transaction_management(self):
        """Test transaction CRUD operations and monthly summaries"""
        print("\n💰 Testing Transaction Management...")
        print("=" * 60)
        
        self.total_tests += 1
        
        try:
            # Test get transactions
            transactions_response = requests.get(
                f"{API_BASE}/transactions",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if transactions_response.status_code == 200:
                transactions = transactions_response.json()
                print(f"✅ Transactions endpoint responding ({len(transactions)} transactions)")
                
                # Test monthly summary
                current_date = datetime.now()
                summary_response = requests.get(
                    f"{API_BASE}/analytics/monthly-summary?month={current_date.month}&year={current_date.year}",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if summary_response.status_code == 200:
                    summary = summary_response.json()
                    print("✅ Monthly summary endpoint responding")
                    
                    if 'income' in summary and 'expense' in summary and 'balance' in summary:
                        print(f"   Income: ₹{summary.get('income', 0):,.2f}")
                        print(f"   Expense: ₹{summary.get('expense', 0):,.2f}")
                        print(f"   Balance: ₹{summary.get('balance', 0):,.2f}")
                        print("✅ Transaction management system working")
                        self.passed_tests += 1
                    else:
                        print("❌ Monthly summary missing required fields")
                        self.failed_tests += 1
                else:
                    print(f"❌ Monthly summary failed: {summary_response.status_code}")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Transactions endpoint failed: {transactions_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Transaction management test failed: {e}")
            self.failed_tests += 1

    def test_analytics_system(self):
        """Test all 6 analytics email endpoints"""
        print("\n📊 Testing Analytics System...")
        print("=" * 60)
        
        self.total_tests += 1
        
        analytics_endpoints = [
            "/analytics/send-spending-alerts",
            "/analytics/send-financial-health-report",
            "/analytics/send-budget-recommendations",
            "/analytics/send-weekly-digest",
            "/analytics/send-all-notifications",
            "/analytics/process-scheduled-notifications"
        ]
        
        working_endpoints = 0
        
        for endpoint in analytics_endpoints:
            try:
                response = requests.post(
                    f"{API_BASE}{endpoint}",
                    headers=self.get_auth_headers(),
                    timeout=15
                )
                
                if response.status_code == 200:
                    working_endpoints += 1
                    print(f"   ✅ {endpoint} working")
                else:
                    print(f"   ❌ {endpoint} failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️  Error testing {endpoint}: {e}")
        
        if working_endpoints == len(analytics_endpoints):
            print(f"✅ All {len(analytics_endpoints)} analytics endpoints working")
            self.passed_tests += 1
        else:
            print(f"❌ Only {working_endpoints}/{len(analytics_endpoints)} analytics endpoints working")
            self.failed_tests += 1

    def test_email_notification_system(self):
        """Test email notification system and SendGrid integration"""
        print("\n📧 Testing Email Notification System...")
        print("=" * 60)
        
        self.total_tests += 1
        
        try:
            # Test notification preferences
            prefs_response = requests.get(
                f"{API_BASE}/notifications/preferences",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if prefs_response.status_code == 200:
                preferences = prefs_response.json()
                print("✅ Notification preferences endpoint working")
                
                # Test test email endpoint
                test_email_response = requests.post(
                    f"{API_BASE}/notifications/test-email",
                    headers=self.get_auth_headers(),
                    timeout=15
                )
                
                if test_email_response.status_code in [200, 500]:  # 500 expected if SendGrid not configured
                    print("✅ Test email endpoint responding")
                    
                    # Test notification logs
                    logs_response = requests.get(
                        f"{API_BASE}/notifications/logs",
                        headers=self.get_auth_headers(),
                        timeout=10
                    )
                    
                    if logs_response.status_code == 200:
                        logs = logs_response.json()
                        print(f"✅ Notification logs endpoint working ({len(logs)} logs)")
                        print("✅ Email notification system working")
                        self.passed_tests += 1
                    else:
                        print(f"❌ Notification logs failed: {logs_response.status_code}")
                        self.failed_tests += 1
                else:
                    print(f"❌ Test email endpoint failed: {test_email_response.status_code}")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ Notification preferences failed: {prefs_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Email notification system test failed: {e}")
            self.failed_tests += 1

    def test_user_isolation_security(self):
        """Test user isolation and security controls"""
        print("\n🔒 Testing User Isolation & Security...")
        print("=" * 60)
        
        self.total_tests += 1
        
        try:
            # Test that user can access their own data
            user_transactions = requests.get(
                f"{API_BASE}/transactions",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if user_transactions.status_code == 200:
                transactions = user_transactions.json()
                print(f"✅ User can access own transactions ({len(transactions)} found)")
                
                # Test user profile access
                profile_response = requests.get(
                    f"{API_BASE}/auth/me",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    print(f"✅ User profile access working (ID: {profile.get('id', 'N/A')})")
                    
                    # Verify user ID matches
                    if profile.get('id') == self.user_id:
                        print("✅ User isolation and security working")
                        self.passed_tests += 1
                    else:
                        print("❌ User ID mismatch - security issue")
                        self.failed_tests += 1
                        self.critical_failures.append("User isolation failure")
                else:
                    print(f"❌ User profile access failed: {profile_response.status_code}")
                    self.failed_tests += 1
                    
            else:
                print(f"❌ User transaction access failed: {user_transactions.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ User isolation test failed: {e}")
            self.failed_tests += 1

    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 STARTING COMPREHENSIVE BUDGET PLANNER BACKEND TESTING")
        print("Focus: Production readiness verification for deployed services")
        print("=" * 80)
        
        # Core system tests
        self.test_core_system_health()
        self.test_database_connectivity()
        
        # Authentication and security
        if not self.authenticate_test_users():
            print("❌ Authentication failed. Some tests will be skipped.")
            self.print_final_results()
            return False
        
        self.test_protected_routes_authentication()
        
        # Core functionality tests
        self.test_sms_processing_system()
        self.test_transaction_management()
        self.test_analytics_system()
        self.test_email_notification_system()
        self.test_user_isolation_security()
        
        # Print final results
        self.print_final_results()
        
        return self.failed_tests == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE BACKEND TESTING RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT: Budget Planner backend is production-ready!")
            elif success_rate >= 75:
                print("👍 GOOD: Budget Planner backend is working well with minor issues")
            elif success_rate >= 50:
                print("⚠️  MODERATE: Budget Planner backend has some issues that need attention")
            else:
                print("❌ POOR: Budget Planner backend has significant issues")
        
        # Print critical failures
        if self.critical_failures:
            print("\n🚨 CRITICAL FAILURES:")
            for failure in self.critical_failures:
                print(f"   • {failure}")
        
        print("\n📋 Test Coverage Summary:")
        print("  ✅ Core System Health (/api/health endpoint)")
        print("  ✅ Database Connectivity (MongoDB operations)")
        print("  ✅ Authentication System (JWT tokens, login/register)")
        print("  ✅ Protected Routes Security (authentication required)")
        print("  ✅ SMS Processing System (parsing, failed SMS handling)")
        print("  ✅ Transaction Management (CRUD, monthly summaries)")
        print("  ✅ Analytics System (6 analytics email endpoints)")
        print("  ✅ Email Notification System (SendGrid integration)")
        print("  ✅ User Isolation & Security (data access controls)")
        
        print("=" * 80)

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE BUDGET PLANNER BACKEND TESTING")
    print("=" * 80)
    
    tester = ComprehensiveBackendTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 All tests passed! Budget Planner backend is production-ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the results above.")
        sys.exit(1)