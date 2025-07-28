#!/usr/bin/env python3
"""
Simple Phase 2 Import Fix Verification Test
"""

import requests

# Production backend URL
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

def test_endpoint(method, endpoint, test_name):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            data = {"test": "data"}
            response = requests.post(url, json=data, headers=headers, timeout=30)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=30)
        
        status_code = response.status_code
        
        if status_code == 401:
            return True, "✅ IMPORT FIX WORKING - Returns 401 (Unauthorized) instead of 404"
        elif status_code == 403:
            return True, "✅ IMPORT FIX WORKING - Returns 403 (Forbidden) instead of 404"
        elif status_code == 404:
            return False, "❌ IMPORT FIX FAILED - Still returns 404 (Not Found)"
        elif status_code == 422:
            return True, "✅ IMPORT FIX WORKING - Returns 422 (Validation Error) - endpoint accessible"
        elif status_code == 400:
            return True, "✅ IMPORT FIX WORKING - Returns 400 (Bad Request) - endpoint accessible"
        else:
            return False, f"❌ Unexpected response - Status: {status_code}"
            
    except Exception as e:
        return False, f"❌ Error: {e}"

def main():
    """Main test execution"""
    print("🚀 Phase 2 Import Fix Verification Test")
    print(f"🌐 Testing Backend: {BASE_URL}")
    print("=" * 80)
    
    # Phase 2 endpoints to test
    endpoints = [
        ("GET", "/account/deletion/preview", "Account Deletion Preview"),
        ("POST", "/account/deletion/soft-delete", "Soft Delete Account"),
        ("GET", "/phone/status", "Phone Status"),
        ("POST", "/phone/initiate-change", "Phone Change Initiation"),
        ("GET", "/sms/list", "SMS List Retrieval"),
        ("POST", "/sms/find-duplicates", "SMS Duplicate Detection"),
    ]
    
    passed = 0
    total = len(endpoints)
    
    for method, endpoint, test_name in endpoints:
        print(f"\n🔍 Testing {test_name} ({method} {endpoint})...")
        success, message = test_endpoint(method, endpoint, test_name)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if success:
            passed += 1
    
    print("\n" + "=" * 80)
    print("📊 PHASE 2 IMPORT FIX VERIFICATION SUMMARY")
    print("=" * 80)
    
    success_rate = (passed / total) * 100
    print(f"\n🎯 IMPORT FIX SUCCESS RATE: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 80:
        print("   ✅ IMPORT FIX: FULLY SUCCESSFUL")
        print("   🎉 Phase 2 endpoints are properly registered and return auth errors instead of 404")
    elif success_rate >= 60:
        print("   ⚠️  IMPORT FIX: PARTIALLY SUCCESSFUL")
        print("   🔧 Some endpoints still return 404 - partial import fix deployment")
    else:
        print("   ❌ IMPORT FIX: FAILED")
        print("   🚨 Most endpoints still return 404 - import fix not deployed")

if __name__ == "__main__":
    main()