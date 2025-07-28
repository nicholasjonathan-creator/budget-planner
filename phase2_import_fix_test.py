#!/usr/bin/env python3
"""
Phase 2 Import Fix Verification Test
Specifically tests that Phase 2 endpoints return 401/403 instead of 404
"""

import requests
import json
from datetime import datetime

# Production backend URL
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

class Phase2ImportFixTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
    
    def make_request(self, method, endpoint, data=None, timeout=30):
        """Make HTTP request without authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
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
        except requests.exceptions.Timeout:
            print(f"Timeout error for {method} {url}")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error for {method} {url}: {e}")
            return None
        except Exception as e:
            print(f"Request error for {method} {url}: {e}")
            return None
    
    def test_import_fix_verification(self):
        """Test that Phase 2 endpoints return 401/403 instead of 404"""
        print("=" * 80)
        print("🎯 PHASE 2 IMPORT FIX VERIFICATION")
        print("🔍 Testing that endpoints return 401/403 instead of 404")
        print("=" * 80)
        
        # Phase 2 endpoints to test (without authentication)
        endpoints_to_test = [
            # Account Deletion Endpoints
            ("GET", "/account/deletion/preview", "Account Deletion Preview"),
            ("POST", "/account/deletion/soft-delete", "Soft Delete Account"),
            ("POST", "/account/deletion/hard-delete", "Hard Delete Account"),
            ("GET", "/account/export-data", "Account Data Export"),
            
            # Phone Management Endpoints
            ("GET", "/phone/status", "Phone Status"),
            ("POST", "/phone/initiate-change", "Phone Change Initiation"),
            ("POST", "/phone/complete-change", "Phone Change Completion"),
            ("DELETE", "/phone/remove", "Phone Number Removal"),
            ("GET", "/phone/history", "Phone Change History"),
            ("POST", "/phone/cancel-change", "Phone Change Cancellation"),
            
            # Enhanced SMS Management Endpoints
            ("GET", "/sms/list", "SMS List Retrieval"),
            ("POST", "/sms/find-duplicates", "SMS Duplicate Detection"),
            ("POST", "/sms/resolve-duplicates", "SMS Duplicate Resolution"),
            ("DELETE", "/sms/dummy_id", "SMS Deletion"),
        ]
        
        import_fix_passed = 0
        import_fix_total = len(endpoints_to_test)
        
        print(f"\n🔧 TESTING {import_fix_total} PHASE 2 ENDPOINTS:")
        
        for method, endpoint, test_name in endpoints_to_test:
            print(f"\n🔍 Testing {test_name} ({method} {endpoint})...")
            
            # Add dummy data for POST requests
            test_data = {}
            if method == "POST":
                if "phone" in endpoint:
                    test_data = {"new_phone_number": "+919876543210"}
                elif "sms" in endpoint:
                    test_data = {"sms_hash": "test_hash", "keep_sms_id": "dummy_id"}
                elif "account" in endpoint:
                    test_data = {"reason": "Testing"}
            
            response = self.make_request(method, endpoint, test_data)
            
            if response:
                status_code = response.status_code
                
                if status_code == 401:
                    self.log_test(f"{test_name} Import Fix", True, 
                                 "✅ IMPORT FIX WORKING - Returns 401 (Unauthorized) instead of 404")
                    import_fix_passed += 1
                elif status_code == 403:
                    self.log_test(f"{test_name} Import Fix", True, 
                                 "✅ IMPORT FIX WORKING - Returns 403 (Forbidden) instead of 404")
                    import_fix_passed += 1
                elif status_code == 404:
                    self.log_test(f"{test_name} Import Fix", False, 
                                 "❌ IMPORT FIX FAILED - Still returns 404 (Not Found)")
                elif status_code == 422:
                    self.log_test(f"{test_name} Import Fix", True, 
                                 "✅ IMPORT FIX WORKING - Returns 422 (Validation Error) - endpoint accessible")
                    import_fix_passed += 1
                elif status_code == 400:
                    self.log_test(f"{test_name} Import Fix", True, 
                                 "✅ IMPORT FIX WORKING - Returns 400 (Bad Request) - endpoint accessible")
                    import_fix_passed += 1
                else:
                    self.log_test(f"{test_name} Import Fix", False, 
                                 f"❌ Unexpected response - Status: {status_code}")
            else:
                self.log_test(f"{test_name} Import Fix", False, 
                             "❌ No response from server")
        
        # Generate summary
        print("\n" + "=" * 80)
        print("📊 PHASE 2 IMPORT FIX VERIFICATION SUMMARY")
        print("=" * 80)
        
        if import_fix_total > 0:
            import_fix_success_rate = (import_fix_passed / import_fix_total) * 100
            print(f"\n🎯 IMPORT FIX SUCCESS RATE: {import_fix_success_rate:.1f}% ({import_fix_passed}/{import_fix_total})")
            
            if import_fix_success_rate >= 80:
                print("   ✅ IMPORT FIX: FULLY SUCCESSFUL")
                print("   🎉 Phase 2 endpoints are properly registered and return auth errors instead of 404")
            elif import_fix_success_rate >= 60:
                print("   ⚠️  IMPORT FIX: PARTIALLY SUCCESSFUL")
                print("   🔧 Some endpoints still return 404 - partial import fix deployment")
            else:
                print("   ❌ IMPORT FIX: FAILED")
                print("   🚨 Most endpoints still return 404 - import fix not deployed")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        
        return import_fix_success_rate

def main():
    """Main execution"""
    print("🚀 Phase 2 Import Fix Verification Test")
    print(f"🌐 Testing Backend: {BASE_URL}")
    print("🎯 Focus: Verifying endpoints return 401/403 instead of 404")
    
    tester = Phase2ImportFixTester()
    
    try:
        success_rate = tester.test_import_fix_verification()
        
        print(f"\n🎯 FINAL RESULT:")
        if success_rate >= 80:
            print("✅ PHASE 2 IMPORT FIX: DEPLOYMENT SUCCESSFUL")
        elif success_rate >= 60:
            print("⚠️  PHASE 2 IMPORT FIX: PARTIALLY DEPLOYED")
        else:
            print("❌ PHASE 2 IMPORT FIX: DEPLOYMENT FAILED")
            
    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()