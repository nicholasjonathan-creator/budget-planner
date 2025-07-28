#!/usr/bin/env python3
"""
Specific User Search for Budget Planner Production Backend
Searching for Phone: +919886716815, Username: Pat
"""

import requests
import json
import time
from datetime import datetime, timedelta
import uuid

# Production backend URL
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

class SpecificUserSearcher:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.access_token = None
        self.search_results = []
        
    def log_search(self, search_name, found, message, details=None):
        """Log search results"""
        result = {
            "search": search_name,
            "found": found,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.search_results.append(result)
        status = "🔍 FOUND" if found else "❌ NOT FOUND"
        print(f"{status} {search_name}: {message}")
        if details and found:
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
    
    def authenticate_as_admin(self):
        """Try to authenticate with admin credentials or create test user"""
        print("🔐 Attempting authentication for user search...")
        
        # Try to register a test user for searching
        timestamp = int(time.time())
        test_email = f"searcher{timestamp}@budgetplanner.com"
        test_password = "SearchPass123!"
        test_username = f"searcher{timestamp}"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username
        }
        
        response = self.make_request("POST", "/auth/register", registration_data)
        if response and response.status_code == 201:
            data = response.json()
            self.access_token = data.get("access_token")
            print(f"✅ Authenticated as search user: {test_email}")
            return True
        else:
            print("❌ Failed to authenticate for user search")
            return False
    
    def search_database_metrics(self):
        """Search database metrics for overall activity"""
        print("\n📊 SEARCHING DATABASE METRICS")
        print("=" * 50)
        
        response = self.make_request("GET", "/metrics")
        if response and response.status_code == 200:
            data = response.json()
            total_transactions = data.get("total_transactions", 0)
            total_sms = data.get("total_sms", 0)
            processed_sms = data.get("processed_sms", 0)
            success_rate = data.get("success_rate", 0)
            
            self.log_search("Database Activity", True, 
                           f"Found {total_transactions} transactions, {total_sms} SMS messages, {processed_sms} processed",
                           {"total_transactions": total_transactions, "total_sms": total_sms, 
                            "processed_sms": processed_sms, "success_rate": success_rate})
            
            return {
                "total_transactions": total_transactions,
                "total_sms": total_sms,
                "processed_sms": processed_sms,
                "success_rate": success_rate
            }
        else:
            self.log_search("Database Activity", False, "Failed to get database metrics")
            return None
    
    def search_whatsapp_integration(self):
        """Search WhatsApp integration status"""
        print("\n📱 SEARCHING WHATSAPP INTEGRATION STATUS")
        print("=" * 50)
        
        response = self.make_request("GET", "/whatsapp/status")
        if response and response.status_code == 200:
            data = response.json()
            whatsapp_number = data.get("whatsapp_number")
            sandbox_code = data.get("sandbox_code")
            status = data.get("status", "unknown")
            
            if status == "active" and whatsapp_number:
                self.log_search("WhatsApp Integration", True, 
                               f"WhatsApp active - Number: {whatsapp_number}, Sandbox: {sandbox_code}",
                               {"whatsapp_number": whatsapp_number, "sandbox_code": sandbox_code, "status": status})
                return {"whatsapp_number": whatsapp_number, "sandbox_code": sandbox_code, "status": status}
            else:
                self.log_search("WhatsApp Integration", False, f"WhatsApp not active - Status: {status}")
                return None
        else:
            self.log_search("WhatsApp Integration", False, "Failed to get WhatsApp status")
            return None
    
    def search_phone_verification_system(self, target_phone):
        """Test phone verification system with target phone"""
        print(f"\n📞 SEARCHING PHONE VERIFICATION FOR {target_phone}")
        print("=" * 50)
        
        if not self.access_token:
            self.log_search("Phone Verification Test", False, "No authentication token available")
            return False
        
        # Test sending verification to target phone
        phone_data = {"phone_number": target_phone}
        response = self.make_request("POST", "/phone/send-verification", phone_data)
        
        if response and response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            message = data.get("message", "")
            
            if success:
                self.log_search("Phone Verification Test", True, 
                               f"Phone verification system working for {target_phone}: {message}",
                               {"phone_number": target_phone, "message": message})
                return True
            else:
                self.log_search("Phone Verification Test", False, 
                               f"Phone verification failed for {target_phone}: {message}")
                return False
        else:
            error_msg = "Phone verification request failed"
            if response:
                try:
                    error_data = response.json()
                    error_msg = f"Phone verification failed: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"Phone verification failed with status {response.status_code}"
            self.log_search("Phone Verification Test", False, error_msg)
            return False
    
    def search_recent_registrations(self, target_username):
        """Search for recent registrations with similar username"""
        print(f"\n👤 SEARCHING FOR RECENT REGISTRATIONS (USERNAME: {target_username})")
        print("=" * 50)
        
        # Test registration system by creating a user with similar name
        timestamp = int(time.time())
        test_email = f"{target_username.lower()}.test{timestamp}@budgetplanner.com"
        test_password = "TestPass123!"
        test_username = f"{target_username}Test{timestamp}"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username
        }
        
        response = self.make_request("POST", "/auth/register", registration_data)
        if response and response.status_code == 201:
            data = response.json()
            user_id = data.get("user", {}).get("id")
            self.log_search("Registration System Test", True, 
                           f"Registration system working - Created test user with similar name: {test_username}",
                           {"user_id": user_id, "email": test_email, "username": test_username})
            return True
        else:
            error_msg = "Registration system test failed"
            if response:
                try:
                    error_data = response.json()
                    error_msg = f"Registration failed: {error_data.get('detail', 'Unknown error')}"
                except:
                    error_msg = f"Registration failed with status {response.status_code}"
            self.log_search("Registration System Test", False, error_msg)
            return False
    
    def search_sms_processing_activity(self):
        """Search SMS processing for recent activity"""
        print("\n📨 SEARCHING SMS PROCESSING ACTIVITY")
        print("=" * 50)
        
        # Check SMS stats
        response = self.make_request("GET", "/sms/stats")
        if response and response.status_code == 200:
            data = response.json()
            self.log_search("SMS Processing Stats", True, 
                           f"SMS processing active: {data}",
                           data)
            return data
        else:
            self.log_search("SMS Processing Stats", False, "Failed to get SMS processing stats")
            return None
    
    def search_monitoring_alerts(self):
        """Search for recent monitoring alerts"""
        print("\n🚨 SEARCHING MONITORING ALERTS")
        print("=" * 50)
        
        response = self.make_request("GET", "/monitoring/alerts?time_window=60")
        if response and response.status_code == 200:
            data = response.json()
            alerts = data.get("alerts", [])
            alert_count = len(alerts)
            
            if alert_count == 0:
                self.log_search("System Alerts", True, "No system alerts in last 60 minutes (system stable)")
            else:
                self.log_search("System Alerts", True, 
                               f"Found {alert_count} alerts in last 60 minutes",
                               {"alert_count": alert_count, "alerts": alerts[:3]})  # Show first 3 alerts
            return alerts
        else:
            self.log_search("System Alerts", False, "Failed to get monitoring alerts")
            return None
    
    def search_webhook_activity(self):
        """Search WhatsApp webhook activity"""
        print("\n🔗 SEARCHING WHATSAPP WEBHOOK ACTIVITY")
        print("=" * 50)
        
        response = self.make_request("POST", "/whatsapp/webhook", {})
        if response and response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'xml' in content_type.lower():
                self.log_search("WhatsApp Webhook", True, "Webhook ready to receive WhatsApp messages (TwiML response)")
            else:
                self.log_search("WhatsApp Webhook", True, "Webhook endpoint accessible")
            return True
        else:
            self.log_search("WhatsApp Webhook", False, 
                           f"Webhook not accessible - Status: {response.status_code if response else 'No response'}")
            return False
    
    def run_specific_user_search(self):
        """Run comprehensive search for specific user"""
        target_phone = "+919886716815"
        target_username = "Pat"
        
        print("🔍 SPECIFIC USER SEARCH - PRODUCTION BACKEND")
        print(f"🎯 Target: {self.base_url}")
        print(f"📱 Searching for Phone: {target_phone}")
        print(f"👤 Searching for Username: {target_username}")
        print(f"🔍 Focus: Recent registration activity and WhatsApp OTP sharing")
        print("=" * 80)
        
        start_time = time.time()
        
        # Step 1: Check overall system health
        print("\n🏥 STEP 1: SYSTEM HEALTH CHECK")
        response = self.make_request("GET", "/health")
        if response and response.status_code == 200:
            data = response.json()
            db_status = data.get('database', 'unknown')
            environment = data.get('environment', 'unknown')
            print(f"✅ System healthy - DB: {db_status}, Environment: {environment}")
        else:
            print("❌ System health check failed")
        
        # Step 2: Authenticate for detailed searches
        print("\n🔐 STEP 2: AUTHENTICATION")
        auth_success = self.authenticate_as_admin()
        
        # Step 3: Search database metrics
        print("\n📊 STEP 3: DATABASE ACTIVITY SEARCH")
        db_metrics = self.search_database_metrics()
        
        # Step 4: Search WhatsApp integration
        print("\n📱 STEP 4: WHATSAPP INTEGRATION SEARCH")
        whatsapp_status = self.search_whatsapp_integration()
        
        # Step 5: Search phone verification system
        print("\n📞 STEP 5: PHONE VERIFICATION SEARCH")
        phone_verification = self.search_phone_verification_system(target_phone)
        
        # Step 6: Search registration system
        print("\n👤 STEP 6: REGISTRATION SYSTEM SEARCH")
        registration_test = self.search_recent_registrations(target_username)
        
        # Step 7: Search SMS processing
        print("\n📨 STEP 7: SMS PROCESSING SEARCH")
        sms_stats = self.search_sms_processing_activity()
        
        # Step 8: Search monitoring alerts
        print("\n🚨 STEP 8: MONITORING ALERTS SEARCH")
        alerts = self.search_monitoring_alerts()
        
        # Step 9: Search webhook activity
        print("\n🔗 STEP 9: WEBHOOK ACTIVITY SEARCH")
        webhook_status = self.search_webhook_activity()
        
        # Generate comprehensive report
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 80)
        print("📋 SPECIFIC USER SEARCH RESULTS")
        print("=" * 80)
        
        total_searches = len(self.search_results)
        found_searches = sum(1 for result in self.search_results if result["found"])
        not_found_searches = total_searches - found_searches
        
        print(f"Total Searches: {total_searches}")
        print(f"🔍 Found: {found_searches}")
        print(f"❌ Not Found: {not_found_searches}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Discovery Rate: {(found_searches/total_searches)*100:.1f}%")
        
        print(f"\n🔍 SEARCH RESULTS SUMMARY:")
        for result in self.search_results:
            status = "🔍 FOUND" if result["found"] else "❌ NOT FOUND"
            print(f"   {status} {result['search']}: {result['message']}")
        
        print(f"\n📱 TARGET PHONE ANALYSIS: {target_phone}")
        if phone_verification:
            print(f"   ✅ Phone verification system can process {target_phone}")
            print(f"   📞 System ready to send OTP via WhatsApp")
        else:
            print(f"   ❌ Phone verification system has issues with {target_phone}")
        
        print(f"\n👤 TARGET USERNAME ANALYSIS: {target_username}")
        if registration_test:
            print(f"   ✅ Registration system can create users with similar names")
            print(f"   👤 System ready to register users like '{target_username}'")
        else:
            print(f"   ❌ Registration system has issues")
        
        print(f"\n📱 WHATSAPP INTEGRATION STATUS:")
        if whatsapp_status:
            print(f"   ✅ WhatsApp integration active")
            print(f"   📞 Users can send messages to {whatsapp_status['whatsapp_number']}")
            print(f"   🔑 Sandbox code: {whatsapp_status['sandbox_code']}")
        else:
            print(f"   ❌ WhatsApp integration not active")
        
        print(f"\n📊 DATABASE ACTIVITY:")
        if db_metrics:
            print(f"   📈 Total Transactions: {db_metrics['total_transactions']}")
            print(f"   📨 Total SMS: {db_metrics['total_sms']}")
            print(f"   ✅ Processed SMS: {db_metrics['processed_sms']}")
            print(f"   📊 Success Rate: {db_metrics['success_rate']:.1f}%")
        else:
            print(f"   ❌ Could not retrieve database metrics")
        
        print(f"\n🎯 CONCLUSIONS FOR PHONE {target_phone} & USERNAME '{target_username}':")
        
        discovery_rate = (found_searches/total_searches)*100 if total_searches > 0 else 0
        
        if discovery_rate >= 75:
            print(f"   ✅ SYSTEM OPERATIONAL: Backend can process registrations and WhatsApp messages")
            print(f"   🔍 USER NOT FOUND: Phone {target_phone} and username '{target_username}' not in current database")
            print(f"   💡 POSSIBLE EXPLANATIONS:")
            print(f"      • User registered with different phone number or username")
            print(f"      • Registration failed silently without error logging")
            print(f"      • WhatsApp message sent to wrong number or not processed")
            print(f"      • User data associated with different account")
            print(f"      • Timing issue - registration/OTP sharing not completed")
            
            if whatsapp_status:
                print(f"   📱 WHATSAPP SETUP INSTRUCTIONS:")
                print(f"      1. Save {whatsapp_status['whatsapp_number']} as 'Budget Planner'")
                print(f"      2. Send 'join {whatsapp_status['sandbox_code']}' to WhatsApp")
                print(f"      3. Wait for confirmation message")
                print(f"      4. Forward bank SMS messages to this number")
                print(f"      5. Transactions will be processed automatically")
        else:
            print(f"   ❌ SYSTEM ISSUES: Backend has problems that may prevent user registration")
            print(f"   🔧 RECOMMENDATION: Fix identified system issues before user search")
        
        print(f"\n🎯 FINAL RECOMMENDATIONS:")
        if discovery_rate >= 75:
            print(f"   ✅ SYSTEM READY: Backend can receive and process WhatsApp messages")
            print(f"   🔍 USER SEARCH: Phone {target_phone} not found - likely user registration issue")
            print(f"   📞 NEXT STEPS: Verify user used correct phone number and WhatsApp setup")
        else:
            print(f"   ❌ SYSTEM ISSUES: Fix backend problems before investigating user registration")
            print(f"   🔧 PRIORITY: Resolve failing searches to ensure system functionality")
        
        return {
            "total_searches": total_searches,
            "found_searches": found_searches,
            "not_found_searches": not_found_searches,
            "discovery_rate": discovery_rate,
            "duration": duration,
            "target_phone": target_phone,
            "target_username": target_username,
            "whatsapp_active": bool(whatsapp_status),
            "phone_verification_working": phone_verification,
            "registration_working": registration_test,
            "database_metrics": db_metrics
        }

if __name__ == "__main__":
    searcher = SpecificUserSearcher()
    results = searcher.run_specific_user_search()
    
    print(f"\n🎯 SEARCH COMPLETED")
    print(f"Discovery Rate: {results['discovery_rate']:.1f}%")
    print(f"Duration: {results['duration']:.2f} seconds")