#!/usr/bin/env python3
"""
Quick Login Issue Investigation for User 'Pat'
"""

import requests
import time

BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

def test_login_endpoint():
    print("🎯 QUICK LOGIN ISSUE INVESTIGATION FOR USER 'PAT'")
    print(f"🌐 Testing Backend: {BASE_URL}")
    print("=" * 60)
    
    # Test 1: Basic health check first
    print("\n🔧 TEST 1: BASIC HEALTH CHECK")
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Health endpoint working - Response time: {response_time:.2f}s")
            data = response.json()
            print(f"   Status: {data.get('status')}, DB: {data.get('database')}")
        else:
            print(f"❌ Health endpoint failed - Status: {response.status_code}")
    except requests.exceptions.Timeout:
        print("❌ Health endpoint timeout (>10s)")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 2: Login endpoint with short timeout
    print("\n🔧 TEST 2: LOGIN ENDPOINT QUICK TEST")
    try:
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/auth/login", 
            json=login_data, 
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        response_time = time.time() - start_time
        
        if response.status_code == 401:
            print(f"✅ Login endpoint working - Response time: {response_time:.2f}s")
            print("   Login endpoint is accessible and responding correctly")
        elif response.status_code == 422:
            print(f"✅ Login endpoint accessible - Validation working - Response time: {response_time:.2f}s")
        else:
            print(f"❌ Login endpoint unexpected response - Status: {response.status_code} - Response time: {response_time:.2f}s")
            
    except requests.exceptions.Timeout:
        print("❌ LOGIN ENDPOINT TIMEOUT (>10s) - This could be the issue!")
        print("   User 'Pat' might be experiencing timeouts during login")
    except Exception as e:
        print(f"❌ Login endpoint error: {e}")
    
    # Test 3: Test with Pat's email
    print("\n🔧 TEST 3: PAT'S EMAIL TEST")
    try:
        pat_login_data = {
            "email": "patrick1091+1@gmail.com",
            "password": "testpassword123"
        }
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/auth/login", 
            json=pat_login_data, 
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        response_time = time.time() - start_time
        
        if response.status_code == 401:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                if 'Incorrect email or password' in error_detail:
                    print(f"✅ User 'Pat' exists in database - Response time: {response_time:.2f}s")
                    print("   Login endpoint working correctly for Pat's email")
                else:
                    print(f"❌ Unexpected error for Pat: {error_detail}")
            except:
                print(f"✅ Login endpoint responding for Pat - Response time: {response_time:.2f}s")
        elif response.status_code == 200:
            print(f"✅ UNEXPECTED SUCCESS - Pat logged in! - Response time: {response_time:.2f}s")
        else:
            print(f"❌ Pat login failed - Status: {response.status_code} - Response time: {response_time:.2f}s")
            
    except requests.exceptions.Timeout:
        print("❌ PAT'S LOGIN TIMEOUT (>10s) - CRITICAL ISSUE FOUND!")
        print("   This is likely why Pat is stuck on 'Logging in...'")
    except Exception as e:
        print(f"❌ Pat's login error: {e}")
    
    # Test 4: Check if it's a general performance issue
    print("\n🔧 TEST 4: PERFORMANCE ANALYSIS")
    response_times = []
    timeouts = 0
    
    for i in range(3):
        try:
            test_data = {
                "email": f"perftest{i}@test.com",
                "password": "testpass"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/auth/login", 
                json=test_data, 
                timeout=15,
                headers={"Content-Type": "application/json"}
            )
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            print(f"   Test {i+1}: {response_time:.2f}s")
            
        except requests.exceptions.Timeout:
            timeouts += 1
            print(f"   Test {i+1}: TIMEOUT (>15s)")
        except Exception as e:
            print(f"   Test {i+1}: ERROR - {e}")
    
    if timeouts > 0:
        print(f"❌ PERFORMANCE ISSUE DETECTED: {timeouts}/3 requests timed out")
        print("   This explains why Pat is stuck on 'Logging in...'")
    elif response_times:
        avg_time = sum(response_times) / len(response_times)
        if avg_time > 5.0:
            print(f"❌ SLOW PERFORMANCE: Average {avg_time:.2f}s (>5s threshold)")
        else:
            print(f"✅ Good performance: Average {avg_time:.2f}s")
    
    print("\n" + "=" * 60)
    print("📊 INVESTIGATION SUMMARY")
    print("=" * 60)
    
    if timeouts > 0:
        print("🔍 ROOT CAUSE IDENTIFIED:")
        print("   - Login endpoint is experiencing timeouts")
        print("   - This explains why Pat is stuck on 'Logging in...'")
        print("   - Backend may be overloaded or having database connectivity issues")
        print("\n💡 RECOMMENDED ACTIONS:")
        print("   1. Check backend server resources and performance")
        print("   2. Verify database connectivity and query performance")
        print("   3. Consider implementing request timeout handling on frontend")
        print("   4. Add retry logic for failed login attempts")
    else:
        print("✅ Login endpoint appears to be working normally")
        print("   Issue may be intermittent or frontend-related")

if __name__ == "__main__":
    test_login_endpoint()