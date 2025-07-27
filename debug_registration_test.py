#!/usr/bin/env python3
"""
Debug Registration Test - Step by step testing of registration components
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

def test_individual_components():
    """Test individual components that registration depends on"""
    print("🔍 DEBUGGING REGISTRATION COMPONENTS")
    print("=" * 60)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed - DB: {data.get('database')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Database connectivity via metrics
    print("\n2. Testing database connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Database accessible - Transactions: {data.get('total_transactions', 0)}")
        else:
            print(f"   ❌ Database metrics failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Database metrics error: {e}")
    
    # Test 3: Test with minimal registration data
    print("\n3. Testing minimal registration data...")
    timestamp = int(time.time())
    minimal_data = {
        "email": f"minimal{timestamp}@test.com",
        "username": f"minimal{timestamp}",
        "password": "Test123!"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=minimal_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            print("   ✅ Minimal registration succeeded!")
            data = response.json()
            print(f"   User ID: {data.get('user', {}).get('id')}")
            return True
        else:
            print(f"   ❌ Minimal registration failed")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=4)}")
            except:
                print(f"   Raw response: {response.text}")
    except Exception as e:
        print(f"   ❌ Minimal registration error: {e}")
    
    # Test 4: Test with different email formats
    print("\n4. Testing different email formats...")
    test_emails = [
        f"simple{timestamp}@gmail.com",
        f"test.user{timestamp}@example.org",
        f"user+tag{timestamp}@domain.co.uk"
    ]
    
    for email in test_emails:
        try:
            test_data = {
                "email": email,
                "username": f"user{timestamp}",
                "password": "Test123!"
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 201:
                print(f"   ✅ {email} - Registration succeeded!")
                return True
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    if "already registered" in error_data.get("detail", "").lower():
                        print(f"   ⚠️  {email} - User already exists (expected)")
                    else:
                        print(f"   ❌ {email} - Validation error: {error_data.get('detail')}")
                except:
                    print(f"   ❌ {email} - Status 400, raw: {response.text}")
            else:
                print(f"   ❌ {email} - Status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {email} - Error: {e}")
    
    # Test 5: Test authentication endpoints without registration
    print("\n5. Testing auth endpoints structure...")
    
    # Test login with non-existent user
    try:
        login_data = {
            "email": f"nonexistent{timestamp}@test.com",
            "password": "Test123!"
        }
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 401:
            print("   ✅ Login endpoint working (correctly rejected non-existent user)")
        else:
            print(f"   ⚠️  Login endpoint returned unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Login test error: {e}")
    
    # Test 6: Test protected endpoint without auth
    print("\n6. Testing protected endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", timeout=30)
        if response.status_code == 401:
            print("   ✅ Protected endpoint correctly requires authentication")
        else:
            print(f"   ⚠️  Protected endpoint unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Protected endpoint test error: {e}")
    
    return False

def test_registration_with_curl():
    """Test registration using curl-like approach"""
    print("\n🌐 TESTING WITH CURL-LIKE APPROACH")
    print("=" * 60)
    
    timestamp = int(time.time())
    test_data = {
        "email": f"curltest{timestamp}@example.com",
        "username": f"curltest{timestamp}",
        "password": "CurlTest123!"
    }
    
    # Prepare the request exactly like curl would
    url = f"{BASE_URL}/auth/register"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Budget-Planner-Test/1.0"
    }
    
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Make request with detailed logging
        session = requests.Session()
        req = requests.Request('POST', url, json=test_data, headers=headers)
        prepared = session.prepare_request(req)
        
        print(f"\nPrepared request:")
        print(f"Method: {prepared.method}")
        print(f"URL: {prepared.url}")
        print(f"Headers: {dict(prepared.headers)}")
        print(f"Body: {prepared.body}")
        
        response = session.send(prepared, timeout=60)
        
        print(f"\nResponse:")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text}")
        
        if response.status_code == 201:
            print("✅ CURL-style registration succeeded!")
            return True
        else:
            print("❌ CURL-style registration failed")
            
    except Exception as e:
        print(f"❌ CURL-style test error: {e}")
    
    return False

def main():
    """Main debug execution"""
    print("🚀 REGISTRATION DEBUG TESTING")
    print(f"🎯 Target: {BASE_URL}")
    print("=" * 60)
    
    # Test individual components
    success = test_individual_components()
    
    if not success:
        # Try curl-like approach
        success = test_registration_with_curl()
    
    if success:
        print("\n🎉 REGISTRATION IS WORKING!")
    else:
        print("\n❌ REGISTRATION STILL FAILING")
        print("\nPossible causes:")
        print("1. Server-side validation errors")
        print("2. Database connection issues during user creation")
        print("3. Password hashing problems")
        print("4. Email service errors (even though disabled)")
        print("5. JWT token creation issues")
        print("6. MongoDB ObjectId/UUID conflicts")

if __name__ == "__main__":
    main()