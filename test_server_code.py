#!/usr/bin/env python3
"""
Test if the production server is running the latest code
"""

import requests
import json
import time

BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

def test_server_version():
    """Test if server is running latest code"""
    print("🔍 TESTING SERVER CODE VERSION")
    print("=" * 40)
    
    # Test 1: Check if the health endpoint shows the expected response
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check response: {data}")
            
            # Check if it has the expected fields from our code
            expected_fields = ["status", "timestamp", "version", "database", "environment"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                print("✅ All expected fields present in health response")
            else:
                print(f"❌ Missing fields: {missing_fields}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Check root endpoint message
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=30)
        if response.status_code == 200:
            data = response.json()
            expected_message = "Budget Planner API is running"
            actual_message = data.get("message", "")
            
            if expected_message in actual_message:
                print(f"✅ Root endpoint message correct: {actual_message}")
            else:
                print(f"❌ Unexpected root message: {actual_message}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: Test a simple registration with detailed error capture
    print("\n3. Testing registration with detailed error capture...")
    try:
        test_data = {
            "email": f"servertest{int(time.time())}@test.com",
            "password": "TestPass123!",
            "username": f"servertest{int(time.time())}"
        }
        
        print(f"📧 Testing with: {test_data['email']}")
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        
        # Try to get response content
        try:
            response_data = response.json()
            print(f"📝 Response JSON: {response_data}")
        except:
            print(f"📝 Raw Response: {response.text[:500]}")
        
        # Check if it's a server error vs client error
        if response.status_code >= 500:
            print("🚨 SERVER ERROR: This indicates an issue on the server side")
        elif response.status_code >= 400:
            print("⚠️  CLIENT ERROR: This indicates a request validation issue")
        else:
            print("✅ SUCCESS: Registration worked!")
            
    except Exception as e:
        print(f"❌ Registration test error: {e}")
    
    # Test 4: Check if email-related endpoints are properly disabled
    print("\n4. Testing email service status...")
    try:
        response = requests.post(f"{BASE_URL}/notifications/test-email", timeout=30)
        if response.status_code == 401:
            print("ℹ️  Email test endpoint requires authentication (expected)")
        elif response.status_code == 200:
            data = response.json()
            if not data.get("success", True):
                print("✅ Email service properly disabled")
            else:
                print("❌ Email service appears to be enabled")
        else:
            print(f"ℹ️  Email test endpoint status: {response.status_code}")
    except Exception as e:
        print(f"❌ Email test error: {e}")

def test_direct_server_logs():
    """Try to get more information about server behavior"""
    print("\n5. Testing server behavior patterns...")
    
    # Test multiple rapid requests to see if there's a pattern
    print("   📊 Testing multiple rapid requests...")
    for i in range(3):
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            end_time = time.time()
            
            print(f"   Request {i+1}: {response.status_code} in {end_time-start_time:.2f}s")
        except Exception as e:
            print(f"   Request {i+1}: Error - {e}")
        
        time.sleep(1)
    
    # Test with different content types
    print("\n   📋 Testing different content types...")
    test_data = {
        "email": f"contenttest{int(time.time())}@test.com",
        "password": "TestPass123!",
        "username": f"contenttest{int(time.time())}"
    }
    
    # Test with application/json
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"   JSON Content-Type: {response.status_code}")
    except Exception as e:
        print(f"   JSON Content-Type: Error - {e}")
    
    # Test with form data
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            data=json.dumps(test_data),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        print(f"   Form Content-Type: {response.status_code}")
    except Exception as e:
        print(f"   Form Content-Type: Error - {e}")

if __name__ == "__main__":
    test_server_version()
    test_direct_server_logs()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION")
    print("=" * 60)
    print("If all components work locally but registration fails on the server,")
    print("the issue is likely one of the following:")
    print("1. 🔄 Server not running the latest deployed code")
    print("2. 🌐 Environment variables missing or incorrect on server")
    print("3. 🗄️  Database connection issues specific to production")
    print("4. 🔧 Server configuration or middleware issues")
    print("5. 📦 Missing dependencies on the production server")