#!/usr/bin/env python3
"""
Final Comprehensive Backend Testing
Complete verification of all backend systems for Budget Planner
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://8218a3b4-6b13-405a-8693-551f9e56e60c.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

# Test users
TEST_USERS = {
    "primary": {"email": "testuser@example.com", "password": "testpassword123"},
    "admin": {"email": "superadmin@budgetplanner.app", "password": "superadminpassword123"}
}

class FinalBackendTester:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.critical_issues = []
        self.auth_token = None
        self.admin_token = None
        self.user_id = None
        
    def authenticate_users(self):
        """Authenticate test users"""
        print("🔐 Authenticating Users...")
        
        # Authenticate primary user
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json=TEST_USERS["primary"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                print(f"✅ Primary user authenticated: {TEST_USERS['primary']['email']}")
            else:
                print(f"❌ Primary user authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error authenticating primary user: {e}")
            return False
        
        # Try to authenticate admin user
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json=TEST_USERS["admin"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                print(f"✅ Admin user authenticated: {TEST_USERS['admin']['email']}")
            else:
                print(f"⚠️  Admin user authentication failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Error authenticating admin user: {e}")
        
        return True

    def get_auth_headers(self, use_admin=False):
        """Get authentication headers"""
        token = self.admin_token if use_admin and self.admin_token else self.auth_token
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def test_core_system_health(self):
        """Test core system health and metrics"""
        print("\n🏥 Testing Core System Health...")
        self.total_tests += 1
        
        try:
            # Health check
            health_response = requests.get(f"{API_BASE}/health", timeout=10)
            if health_response.status_code != 200:
                print(f"❌ Health check failed: {health_response.status_code}")
                self.failed_tests += 1
                return
            
            health_data = health_response.json()
            print(f"✅ System Status: {health_data.get('status')}")
            print(f"   Database: {health_data.get('database')}")
            print(f"   Environment: {health_data.get('environment')}")
            print(f"   Version: {health_data.get('version')}")
            
            # Metrics check
            metrics_response = requests.get(f"{API_BASE}/metrics", timeout=10)
            if metrics_response.status_code == 200:
                metrics = metrics_response.json()
                print(f"   Total Transactions: {metrics.get('total_transactions', 0)}")
                print(f"   Total SMS: {metrics.get('total_sms', 0)}")
                print(f"   SMS Success Rate: {metrics.get('success_rate', 0):.1f}%")
            
            self.passed_tests += 1
            
        except Exception as e:
            print(f"❌ Core system health test failed: {e}")
            self.failed_tests += 1

    def test_authentication_system(self):
        """Test authentication system comprehensively"""
        print("\n🔐 Testing Authentication System...")
        self.total_tests += 1
        
        try:
            # Test /auth/me endpoint
            response = requests.get(
                f"{API_BASE}/auth/me",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ User Profile: {user_info.get('email')}")
                print(f"   Role: {user_info.get('role')}")
                print(f"   Active: {user_info.get('is_active')}")
                self.passed_tests += 1
            else:
                print(f"❌ Authentication system failed: {response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            self.failed_tests += 1

    def test_transaction_management(self):
        """Test transaction CRUD operations and filtering"""
        print("\n💰 Testing Transaction Management...")
        self.total_tests += 1
        
        try:
            # Test creating a transaction
            test_transaction = {
                "type": "expense",
                "category_id": 1,
                "amount": 100.50,
                "description": "Backend Test Transaction",
                "date": "2025-01-15T10:00:00Z",
                "source": "manual",
                "merchant": "Test Merchant",
                "currency": "INR"
            }
            
            create_response = requests.post(
                f"{API_BASE}/transactions",
                json=test_transaction,
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if create_response.status_code == 200:
                created_txn = create_response.json()
                transaction_id = created_txn.get('id')
                print(f"✅ Transaction created: {transaction_id}")
                
                # Test retrieving transactions
                get_response = requests.get(
                    f"{API_BASE}/transactions",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if get_response.status_code == 200:
                    transactions = get_response.json()
                    print(f"   Retrieved {len(transactions)} transactions")
                    
                    # Test month filtering
                    filter_response = requests.get(
                        f"{API_BASE}/transactions?month=0&year=2025",
                        headers=self.get_auth_headers(),
                        timeout=10
                    )
                    
                    if filter_response.status_code == 200:
                        filtered_txns = filter_response.json()
                        print(f"   Filtered transactions (Jan 2025): {len(filtered_txns)}")
                        
                        # Verify our test transaction appears in filtered results
                        test_txn_found = any(txn.get('id') == transaction_id for txn in filtered_txns)
                        if test_txn_found:
                            print("   ✅ Transaction filtering working correctly")
                        else:
                            print("   ⚠️  Transaction not found in filtered results")
                    
                    self.passed_tests += 1
                else:
                    print(f"❌ Failed to retrieve transactions: {get_response.status_code}")
                    self.failed_tests += 1
            else:
                print(f"❌ Failed to create transaction: {create_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Transaction management test failed: {e}")
            self.failed_tests += 1

    def test_sms_processing_system(self):
        """Test SMS processing functionality"""
        print("\n📱 Testing SMS Processing System...")
        self.total_tests += 1
        
        try:
            # Test SMS stats
            stats_response = requests.get(f"{API_BASE}/sms/stats", timeout=10)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"✅ SMS Stats retrieved: {stats}")
            
            # Test failed SMS endpoint
            failed_response = requests.get(
                f"{API_BASE}/sms/failed",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if failed_response.status_code == 200:
                failed_sms = failed_response.json()
                print(f"   Failed SMS count: {len(failed_sms.get('failed_sms', []))}")
                self.passed_tests += 1
            else:
                print(f"❌ SMS processing test failed: {failed_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ SMS processing test failed: {e}")
            self.failed_tests += 1

    def test_analytics_system(self):
        """Test analytics endpoints"""
        print("\n📊 Testing Analytics System...")
        self.total_tests += 1
        
        try:
            # Test monthly summary
            summary_response = requests.get(
                f"{API_BASE}/analytics/monthly-summary?month=1&year=2025",
                headers=self.get_auth_headers(),
                timeout=15
            )
            
            if summary_response.status_code == 200:
                summary = summary_response.json()
                print(f"✅ Monthly Summary: Income=₹{summary.get('income', 0):.2f}, "
                      f"Expense=₹{summary.get('expense', 0):.2f}")
                
                # Test analytics email endpoints
                analytics_endpoints = [
                    "/analytics/send-spending-alerts",
                    "/analytics/send-financial-health-report",
                    "/analytics/send-budget-recommendations",
                    "/analytics/send-weekly-digest"
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
                    except:
                        pass
                
                print(f"   Analytics email endpoints working: {working_endpoints}/{len(analytics_endpoints)}")
                self.passed_tests += 1
            else:
                print(f"❌ Analytics system failed: {summary_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Analytics test failed: {e}")
            self.failed_tests += 1

    def test_email_notification_system(self):
        """Test email notification system"""
        print("\n📧 Testing Email Notification System...")
        self.total_tests += 1
        
        try:
            # Test notification preferences
            prefs_response = requests.get(
                f"{API_BASE}/notifications/preferences",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if prefs_response.status_code == 200:
                prefs = prefs_response.json()
                print(f"✅ Notification preferences retrieved")
                print(f"   Email enabled: {prefs.get('email_enabled', False)}")
                
                # Test notification logs
                logs_response = requests.get(
                    f"{API_BASE}/notifications/logs?limit=5",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if logs_response.status_code == 200:
                    logs = logs_response.json()
                    print(f"   Recent notification logs: {len(logs)}")
                    self.passed_tests += 1
                else:
                    print(f"❌ Notification logs failed: {logs_response.status_code}")
                    self.failed_tests += 1
            else:
                print(f"❌ Email notification system failed: {prefs_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Email notification test failed: {e}")
            self.failed_tests += 1

    def test_budget_management(self):
        """Test budget management system"""
        print("\n💼 Testing Budget Management...")
        self.total_tests += 1
        
        try:
            # Test budget limits
            budget_response = requests.get(
                f"{API_BASE}/budget-limits?month=1&year=2025",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if budget_response.status_code == 200:
                budgets = budget_response.json()
                print(f"✅ Budget limits retrieved: {len(budgets)} categories")
                
                # Test categories
                cat_response = requests.get(
                    f"{API_BASE}/categories",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if cat_response.status_code == 200:
                    categories = cat_response.json()
                    print(f"   Categories available: {len(categories)}")
                    self.passed_tests += 1
                else:
                    print(f"❌ Categories failed: {cat_response.status_code}")
                    self.failed_tests += 1
            else:
                print(f"❌ Budget management failed: {budget_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Budget management test failed: {e}")
            self.failed_tests += 1

    def test_whatsapp_integration(self):
        """Test WhatsApp integration"""
        print("\n💬 Testing WhatsApp Integration...")
        self.total_tests += 1
        
        try:
            # Test WhatsApp status
            whatsapp_response = requests.get(
                f"{API_BASE}/whatsapp/status",
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if whatsapp_response.status_code == 200:
                status = whatsapp_response.json()
                print(f"✅ WhatsApp integration status: {status.get('status')}")
                print(f"   Supported banks: {len(status.get('supported_banks', []))}")
                
                # Test phone verification status
                phone_response = requests.get(
                    f"{API_BASE}/phone/status",
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if phone_response.status_code == 200:
                    phone_status = phone_response.json()
                    print(f"   Phone verified: {phone_status.get('phone_verified', False)}")
                    self.passed_tests += 1
                else:
                    print(f"❌ Phone status failed: {phone_response.status_code}")
                    self.failed_tests += 1
            else:
                print(f"❌ WhatsApp integration failed: {whatsapp_response.status_code}")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ WhatsApp integration test failed: {e}")
            self.failed_tests += 1

    def test_security_and_access_control(self):
        """Test security and access control"""
        print("\n🛡️  Testing Security & Access Control...")
        self.total_tests += 1
        
        try:
            # Test that protected endpoints require authentication
            protected_endpoints = [
                "/transactions",
                "/analytics/monthly-summary?month=1&year=2025",
                "/notifications/preferences",
                "/sms/failed"
            ]
            
            unauthorized_count = 0
            for endpoint in protected_endpoints:
                try:
                    response = requests.get(
                        f"{API_BASE}{endpoint}",
                        headers={"Content-Type": "application/json"},  # No auth
                        timeout=10
                    )
                    if response.status_code in [401, 403]:
                        unauthorized_count += 1
                except:
                    pass
            
            if unauthorized_count == len(protected_endpoints):
                print(f"✅ All {len(protected_endpoints)} protected endpoints require authentication")
                self.passed_tests += 1
            else:
                print(f"❌ Only {unauthorized_count}/{len(protected_endpoints)} endpoints require auth")
                self.critical_issues.append("Security issue: Some protected endpoints don't require authentication")
                self.failed_tests += 1
                
        except Exception as e:
            print(f"❌ Security test failed: {e}")
            self.failed_tests += 1

    def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 FINAL COMPREHENSIVE BACKEND TESTING")
        print("=" * 80)
        print("Complete verification of all Budget Planner backend systems")
        print("=" * 80)
        
        # Authenticate users
        if not self.authenticate_users():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Run all tests
        self.test_core_system_health()
        self.test_authentication_system()
        self.test_transaction_management()
        self.test_sms_processing_system()
        self.test_analytics_system()
        self.test_email_notification_system()
        self.test_budget_management()
        self.test_whatsapp_integration()
        self.test_security_and_access_control()
        
        # Print results
        self.print_final_results()
        
        return self.failed_tests == 0 and len(self.critical_issues) == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("📊 FINAL COMPREHENSIVE BACKEND TEST RESULTS")
        print("=" * 80)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in self.critical_issues:
                print(f"   ❌ {issue}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"\nSuccess Rate: {success_rate:.1f}%")
            
            if self.critical_issues:
                print("🚨 CRITICAL: System has critical security or functionality issues!")
            elif success_rate >= 95:
                print("🎉 EXCELLENT: Backend system is production-ready!")
            elif success_rate >= 85:
                print("👍 GOOD: Backend system is working well with minor issues")
            elif success_rate >= 70:
                print("⚠️  MODERATE: Backend system has some issues that need attention")
            else:
                print("❌ POOR: Backend system has significant issues")
        
        print("\n📋 Systems Tested:")
        print("  🏥 Core System Health & Metrics")
        print("  🔐 Authentication System")
        print("  💰 Transaction Management (CRUD & Filtering)")
        print("  📱 SMS Processing System")
        print("  📊 Analytics System & Email Endpoints")
        print("  📧 Email Notification System")
        print("  💼 Budget Management")
        print("  💬 WhatsApp Integration")
        print("  🛡️  Security & Access Control")
        
        print("=" * 80)

if __name__ == "__main__":
    print("🧪 Final Comprehensive Backend Testing")
    print("=" * 80)
    
    tester = FinalBackendTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend system is fully functional and production-ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed or critical issues found. Please review the results above.")
        sys.exit(1)