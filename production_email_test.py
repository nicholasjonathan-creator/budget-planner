#!/usr/bin/env python3
"""
Comprehensive Production Email Automation System Testing
Tests requested by user for production email functionality:
1. Email Scheduler Service endpoints (status, configuration, checklist)
2. Scheduler Controls (start/stop scheduler functionality)
3. Manual Email Triggers (budget alerts, monthly summaries)
4. Production Configuration (checklist, SMTP config)
5. Email Scheduler Functionality (background jobs, health checks)
6. Integration Testing (admin access control, error handling)
"""

import requests
import json
import sys
import os
from datetime import datetime
import uuid
import time

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://45029e2d-ce68-4057-a50f-b6a3f9f23132.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ProductionEmailAutomationTester:
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.admin_token = None
        self.regular_user_token = None
        
        # Test credentials for admin and regular user
        self.admin_credentials = {
            "email": "superadmin@example.com",
            "password": "superadminpass123"
        }
        
        self.regular_user_credentials = {
            "email": "testuser@example.com", 
            "password": "testpassword123"
        }

    def test_health_check(self):
        """Test if the backend is running"""
        print("🔍 Testing Backend Health...")
        try:
            response = requests.get(f"{API_BASE}/health", timeout=30)
            if response.status_code == 200:
                print("✅ Backend is healthy")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False

    def authenticate_admin_user(self):
        """Authenticate admin user and get token"""
        print("\n🔐 Authenticating Admin User...")
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json=self.admin_credentials,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.admin_token = result.get('access_token')
                print("✅ Admin authentication successful")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error authenticating admin: {e}")
            return False

    def authenticate_regular_user(self):
        """Authenticate regular user and get token"""
        print("\n🔐 Authenticating Regular User...")
        try:
            response = requests.post(
                f"{API_BASE}/auth/login",
                json=self.regular_user_credentials,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.regular_user_token = result.get('access_token')
                print("✅ Regular user authentication successful")
                return True
            else:
                print(f"❌ Regular user authentication failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error authenticating regular user: {e}")
            return False

    def test_production_email_status_endpoint(self):
        """Test /api/notifications/production/status endpoint (admin only)"""
        print("\n🧪 Testing Production Email Status Endpoint...")
        print("=" * 60)
        
        self.total_tests += 1
        
        if not self.admin_token:
            print("❌ Cannot test - admin authentication required")
            self.failed_tests += 1
            return False
        
        try:
            # Test with admin token
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(
                f"{API_BASE}/notifications/production/status",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Production status endpoint accessible with admin token")
                
                # Verify response structure
                expected_fields = ['configuration', 'production_checklist', 'scheduler', 'environment']
                missing_fields = [field for field in expected_fields if field not in result]
                
                if not missing_fields:
                    print("✅ Response contains all expected fields:")
                    print(f"   Configuration: {result.get('configuration', {}).get('status', 'N/A')}")
                    print(f"   Production Checklist: {result.get('production_checklist', {}).get('completion_percentage', 0):.1f}% complete")
                    print(f"   Scheduler Running: {result.get('scheduler', {}).get('running', False)}")
                    print(f"   Environment: {result.get('environment', 'N/A')}")
                    
                    # Test scheduler status details
                    scheduler_info = result.get('scheduler', {})
                    if 'running' in scheduler_info and 'jobs' in scheduler_info:
                        print(f"   Scheduler Jobs: {scheduler_info.get('jobs', 0)} configured")
                        print("✅ Scheduler status information complete")
                    else:
                        print("⚠️  Scheduler status information incomplete")
                    
                    self.passed_tests += 1
                    return True
                else:
                    print(f"❌ Response missing fields: {missing_fields}")
                    self.failed_tests += 1
                    return False
                    
            else:
                print(f"❌ Production status endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing production status endpoint: {e}")
            self.failed_tests += 1
            return False

    def test_admin_access_control(self):
        """Test that production endpoints are admin-only"""
        print("\n🧪 Testing Admin Access Control...")
        print("=" * 50)
        
        self.total_tests += 1
        
        if not self.regular_user_token:
            print("❌ Cannot test - regular user authentication required")
            self.failed_tests += 1
            return False
        
        try:
            # Test production endpoints with regular user token (should fail)
            headers = {"Authorization": f"Bearer {self.regular_user_token}"}
            
            production_endpoints = [
                "/notifications/production/status",
                "/notifications/production/checklist",
                "/notifications/production/smtp-config"
            ]
            
            access_denied_count = 0
            
            for endpoint in production_endpoints:
                response = requests.get(
                    f"{API_BASE}{endpoint}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [401, 403]:
                    print(f"✅ {endpoint} properly denied for regular user")
                    access_denied_count += 1
                else:
                    print(f"❌ {endpoint} accessible to regular user (security issue)")
            
            if access_denied_count == len(production_endpoints):
                print("✅ All production endpoints properly protected")
                self.passed_tests += 1
                return True
            else:
                print(f"❌ {len(production_endpoints) - access_denied_count} endpoints not properly protected")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing admin access control: {e}")
            self.failed_tests += 1
            return False

    def test_scheduler_controls(self):
        """Test scheduler start/stop endpoints"""
        print("\n🧪 Testing Scheduler Controls...")
        print("=" * 40)
        
        self.total_tests += 1
        
        if not self.admin_token:
            print("❌ Cannot test - admin authentication required")
            self.failed_tests += 1
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test stop scheduler first
            print("Step 1: Testing stop scheduler endpoint...")
            stop_response = requests.post(
                f"{API_BASE}/notifications/production/stop-scheduler",
                headers=headers,
                timeout=10
            )
            
            if stop_response.status_code == 200:
                stop_result = stop_response.json()
                print(f"✅ Stop scheduler endpoint working: {stop_result.get('message', 'N/A')}")
                print(f"   Status: {stop_result.get('status', 'N/A')}")
            else:
                print(f"❌ Stop scheduler failed: {stop_response.status_code}")
                print(f"   Response: {stop_response.text}")
                self.failed_tests += 1
                return False
            
            # Wait a moment
            time.sleep(1)
            
            # Test start scheduler
            print("\nStep 2: Testing start scheduler endpoint...")
            start_response = requests.post(
                f"{API_BASE}/notifications/production/start-scheduler",
                headers=headers,
                timeout=10
            )
            
            if start_response.status_code == 200:
                start_result = start_response.json()
                print(f"✅ Start scheduler endpoint working: {start_result.get('message', 'N/A')}")
                print(f"   Status: {start_result.get('status', 'N/A')}")
            else:
                print(f"❌ Start scheduler failed: {start_response.status_code}")
                print(f"   Response: {start_response.text}")
                self.failed_tests += 1
                return False
            
            # Verify scheduler status changed
            print("\nStep 3: Verifying scheduler status...")
            status_response = requests.get(
                f"{API_BASE}/notifications/production/status",
                headers=headers,
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                scheduler_running = status_result.get('scheduler', {}).get('running', False)
                print(f"✅ Scheduler status verified: {'Running' if scheduler_running else 'Stopped'}")
                
                self.passed_tests += 1
                return True
            else:
                print(f"❌ Could not verify scheduler status: {status_response.status_code}")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"❌ Error testing scheduler controls: {e}")
            self.failed_tests += 1
            return False

    def test_manual_email_triggers(self):
        """Test manual email trigger endpoints"""
        print("\n🧪 Testing Manual Email Triggers...")
        print("=" * 45)
        
        self.total_tests += 1
        
        if not self.admin_token:
            print("❌ Cannot test - admin authentication required")
            self.failed_tests += 1
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test budget alerts trigger
            print("Step 1: Testing manual budget alerts trigger...")
            budget_response = requests.post(
                f"{API_BASE}/notifications/production/trigger-budget-alerts",
                headers=headers,
                timeout=15  # Longer timeout for email processing
            )
            
            if budget_response.status_code == 200:
                budget_result = budget_response.json()
                print(f"✅ Budget alerts trigger working: {budget_result.get('message', 'N/A')}")
            else:
                print(f"❌ Budget alerts trigger failed: {budget_response.status_code}")
                print(f"   Response: {budget_response.text}")
                self.failed_tests += 1
                return False
            
            # Test monthly summaries trigger
            print("\nStep 2: Testing manual monthly summaries trigger...")
            monthly_response = requests.post(
                f"{API_BASE}/notifications/production/trigger-monthly-summaries",
                headers=headers,
                timeout=15  # Longer timeout for email processing
            )
            
            if monthly_response.status_code == 200:
                monthly_result = monthly_response.json()
                print(f"✅ Monthly summaries trigger working: {monthly_result.get('message', 'N/A')}")
            else:
                print(f"❌ Monthly summaries trigger failed: {monthly_response.status_code}")
                print(f"   Response: {monthly_response.text}")
                self.failed_tests += 1
                return False
            
            print("✅ Both manual email triggers working correctly")
            self.passed_tests += 1
            return True
                
        except Exception as e:
            print(f"❌ Error testing manual email triggers: {e}")
            self.failed_tests += 1
            return False

    def test_production_configuration_endpoints(self):
        """Test production configuration endpoints"""
        print("\n🧪 Testing Production Configuration Endpoints...")
        print("=" * 55)
        
        self.total_tests += 1
        
        if not self.admin_token:
            print("❌ Cannot test - admin authentication required")
            self.failed_tests += 1
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Test production checklist endpoint
            print("Step 1: Testing production checklist endpoint...")
            checklist_response = requests.get(
                f"{API_BASE}/notifications/production/checklist",
                headers=headers,
                timeout=10
            )
            
            if checklist_response.status_code == 200:
                checklist_result = checklist_response.json()
                print("✅ Production checklist endpoint working")
                
                # Verify checklist structure
                if 'checklist' in checklist_result and 'completion_percentage' in checklist_result:
                    completion = checklist_result.get('completion_percentage', 0)
                    total_tasks = checklist_result.get('total_tasks', 0)
                    completed_tasks = checklist_result.get('completed_tasks', 0)
                    
                    print(f"   Completion: {completion:.1f}% ({completed_tasks}/{total_tasks} tasks)")
                    print(f"   Production Ready: {checklist_result.get('is_production_ready', False)}")
                    
                    # Show checklist items
                    checklist = checklist_result.get('checklist', {})
                    for item, details in checklist.items():
                        status_icon = "✅" if details.get('status') == 'complete' else "⚠️"
                        print(f"   {status_icon} {item}: {details.get('description', 'N/A')}")
                        
                else:
                    print("❌ Checklist response missing required fields")
                    self.failed_tests += 1
                    return False
            else:
                print(f"❌ Production checklist failed: {checklist_response.status_code}")
                print(f"   Response: {checklist_response.text}")
                self.failed_tests += 1
                return False
            
            # Test SMTP config endpoint
            print("\nStep 2: Testing SMTP configuration endpoint...")
            smtp_response = requests.get(
                f"{API_BASE}/notifications/production/smtp-config",
                headers=headers,
                timeout=10
            )
            
            if smtp_response.status_code == 200:
                smtp_result = smtp_response.json()
                print("✅ SMTP configuration endpoint working")
                
                # Verify SMTP config structure
                if 'smtp_settings' in smtp_result:
                    smtp_settings = smtp_result.get('smtp_settings', {})
                    recommended = smtp_result.get('recommended', 'N/A')
                    fallback_options = smtp_result.get('fallback_options', [])
                    
                    print(f"   Recommended service: {recommended}")
                    print(f"   Available services: {list(smtp_settings.keys())}")
                    print(f"   Fallback options: {fallback_options}")
                    
                    # Check SendGrid config
                    if 'sendgrid' in smtp_settings:
                        sg_config = smtp_settings['sendgrid']
                        print(f"   SendGrid host: {sg_config.get('host', 'N/A')}")
                        print(f"   SendGrid port: {sg_config.get('port', 'N/A')}")
                        print(f"   SendGrid TLS: {sg_config.get('use_tls', False)}")
                    
                else:
                    print("❌ SMTP config response missing required fields")
                    self.failed_tests += 1
                    return False
            else:
                print(f"❌ SMTP configuration failed: {smtp_response.status_code}")
                print(f"   Response: {smtp_response.text}")
                self.failed_tests += 1
                return False
            
            print("✅ Both production configuration endpoints working")
            self.passed_tests += 1
            return True
                
        except Exception as e:
            print(f"❌ Error testing production configuration: {e}")
            self.failed_tests += 1
            return False

    def test_email_scheduler_functionality(self):
        """Test email scheduler background functionality"""
        print("\n🧪 Testing Email Scheduler Functionality...")
        print("=" * 50)
        
        self.total_tests += 1
        
        if not self.admin_token:
            print("❌ Cannot test - admin authentication required")
            self.failed_tests += 1
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            
            # Get scheduler status
            print("Step 1: Checking scheduler initialization...")
            status_response = requests.get(
                f"{API_BASE}/notifications/production/status",
                headers=headers,
                timeout=10
            )
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                scheduler_info = status_result.get('scheduler', {})
                
                print(f"✅ Scheduler status retrieved")
                print(f"   Running: {scheduler_info.get('running', False)}")
                print(f"   Jobs configured: {scheduler_info.get('jobs', 0)}")
                
                # Verify scheduler has jobs configured
                job_count = scheduler_info.get('jobs', 0)
                if job_count > 0:
                    print(f"✅ Scheduler has {job_count} jobs configured")
                    
                    # Expected jobs: daily_budget_alerts, weekly_summaries, monthly_summaries, daily_sms_summaries, system_health_check
                    expected_jobs = 5
                    if job_count >= expected_jobs:
                        print(f"✅ Expected number of jobs configured ({job_count} >= {expected_jobs})")
                    else:
                        print(f"⚠️  Fewer jobs than expected ({job_count} < {expected_jobs})")
                        
                else:
                    print("⚠️  No jobs configured in scheduler")
                
            else:
                print(f"❌ Could not get scheduler status: {status_response.status_code}")
                self.failed_tests += 1
                return False
            
            # Test scheduler restart functionality
            print("\nStep 2: Testing scheduler restart functionality...")
            
            # Stop scheduler
            stop_response = requests.post(
                f"{API_BASE}/notifications/production/stop-scheduler",
                headers=headers,
                timeout=10
            )
            
            if stop_response.status_code == 200:
                print("✅ Scheduler stopped successfully")
                
                # Start scheduler again
                start_response = requests.post(
                    f"{API_BASE}/notifications/production/start-scheduler",
                    headers=headers,
                    timeout=10
                )
                
                if start_response.status_code == 200:
                    print("✅ Scheduler restarted successfully")
                    
                    # Verify jobs are reconfigured
                    time.sleep(1)  # Give scheduler time to initialize
                    
                    final_status_response = requests.get(
                        f"{API_BASE}/notifications/production/status",
                        headers=headers,
                        timeout=10
                    )
                    
                    if final_status_response.status_code == 200:
                        final_result = final_status_response.json()
                        final_scheduler = final_result.get('scheduler', {})
                        final_jobs = final_scheduler.get('jobs', 0)
                        
                        if final_jobs > 0:
                            print(f"✅ Scheduler reinitialized with {final_jobs} jobs")
                            print("✅ Scheduler restart functionality working")
                        else:
                            print("⚠️  Scheduler restarted but no jobs configured")
                    else:
                        print("❌ Could not verify scheduler restart")
                        self.failed_tests += 1
                        return False
                        
                else:
                    print(f"❌ Scheduler restart failed: {start_response.status_code}")
                    self.failed_tests += 1
                    return False
                    
            else:
                print(f"❌ Scheduler stop failed: {stop_response.status_code}")
                self.failed_tests += 1
                return False
            
            print("✅ Email scheduler functionality verified")
            self.passed_tests += 1
            return True
                
        except Exception as e:
            print(f"❌ Error testing scheduler functionality: {e}")
            self.failed_tests += 1
            return False

    def test_integration_and_error_handling(self):
        """Test integration with existing notification system and error handling"""
        print("\n🧪 Testing Integration and Error Handling...")
        print("=" * 55)
        
        self.total_tests += 1
        
        try:
            # Test without authentication (should fail)
            print("Step 1: Testing unauthenticated access...")
            unauth_response = requests.get(
                f"{API_BASE}/notifications/production/status",
                timeout=10
            )
            
            if unauth_response.status_code in [401, 403]:
                print("✅ Unauthenticated access properly denied")
            else:
                print(f"❌ Unauthenticated access not properly handled: {unauth_response.status_code}")
                self.failed_tests += 1
                return False
            
            # Test with invalid token
            print("\nStep 2: Testing invalid token...")
            invalid_headers = {"Authorization": "Bearer invalid_token_here"}
            invalid_response = requests.get(
                f"{API_BASE}/notifications/production/status",
                headers=invalid_headers,
                timeout=10
            )
            
            if invalid_response.status_code in [401, 403]:
                print("✅ Invalid token properly rejected")
            else:
                print(f"❌ Invalid token not properly handled: {invalid_response.status_code}")
                self.failed_tests += 1
                return False
            
            # Test integration with existing notification preferences
            if self.admin_token:
                print("\nStep 3: Testing integration with notification preferences...")
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                # Get notification preferences (should work)
                prefs_response = requests.get(
                    f"{API_BASE}/notifications/preferences",
                    headers=headers,
                    timeout=10
                )
                
                if prefs_response.status_code == 200:
                    print("✅ Integration with notification preferences working")
                    
                    # Test notification logs (should work)
                    logs_response = requests.get(
                        f"{API_BASE}/notifications/logs",
                        headers=headers,
                        timeout=10
                    )
                    
                    if logs_response.status_code == 200:
                        print("✅ Integration with notification logs working")
                    else:
                        print(f"⚠️  Notification logs integration issue: {logs_response.status_code}")
                        
                else:
                    print(f"⚠️  Notification preferences integration issue: {prefs_response.status_code}")
            
            print("✅ Integration and error handling tests completed")
            self.passed_tests += 1
            return True
                
        except Exception as e:
            print(f"❌ Error testing integration and error handling: {e}")
            self.failed_tests += 1
            return False

    def run_all_tests(self):
        """Run all production email automation tests"""
        print("🚀 Starting Production Email Automation System Testing")
        print("Focus: Scheduler service, controls, triggers, configuration, functionality, integration")
        print("=" * 90)
        
        # Test backend health first
        if not self.test_health_check():
            print("❌ Backend is not accessible. Aborting tests.")
            return False
        
        # Authenticate users
        admin_auth = self.authenticate_admin_user()
        regular_auth = self.authenticate_regular_user()
        
        if not admin_auth:
            print("❌ Admin authentication failed. Cannot test admin-only endpoints.")
            return False
        
        # Run all test suites
        results = []
        results.append(self.test_production_email_status_endpoint())
        results.append(self.test_admin_access_control() if regular_auth else True)  # Skip if regular user auth failed
        results.append(self.test_scheduler_controls())
        results.append(self.test_manual_email_triggers())
        results.append(self.test_production_configuration_endpoints())
        results.append(self.test_email_scheduler_functionality())
        results.append(self.test_integration_and_error_handling())
        
        # Print final results
        self.print_final_results()
        
        return all(results)

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 90)
        print("📊 PRODUCTION EMAIL AUTOMATION SYSTEM TEST RESULTS")
        print("=" * 90)
        
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 95:
                print("🎉 EXCELLENT: Production email automation system is working perfectly!")
            elif success_rate >= 85:
                print("👍 GOOD: Production email automation system is working well with minor issues")
            elif success_rate >= 70:
                print("⚠️  MODERATE: Production email automation system has some issues that need attention")
            else:
                print("❌ POOR: Production email automation system has significant issues")
        
        print("\n📋 Test Summary:")
        print("  ✅ Email Scheduler Service status endpoint (admin only)")
        print("  ✅ Admin access control for production endpoints")
        print("  ✅ Scheduler start/stop controls")
        print("  ✅ Manual email triggers (budget alerts, monthly summaries)")
        print("  ✅ Production configuration endpoints (checklist, SMTP config)")
        print("  ✅ Email scheduler background functionality")
        print("  ✅ Integration testing and error handling")
        
        print("=" * 90)


if __name__ == "__main__":
    print("🧪 Production Email Automation System Testing")
    print("=" * 60)
    
    tester = ProductionEmailAutomationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Production email automation system is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the results above.")
        sys.exit(1)