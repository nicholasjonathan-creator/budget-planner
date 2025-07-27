#!/usr/bin/env python3
"""
Focused Registration Testing for Budget Planner Production Deployment
Specifically tests the user registration issue that was reported as fixed
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Production backend URL
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

def test_registration_with_detailed_logging():
    """Test user registration with detailed error logging"""
    print("🔍 FOCUSED REGISTRATION TESTING")
    print(f"🎯 Target: {BASE_URL}")
    print("=" * 60)
    
    # Generate unique test user
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@budgetplanner.com"
    test_password = "SecurePass123!"
    test_username = f"testuser{timestamp}"
    
    registration_data = {
        "email": test_email,
        "password": test_password,
        "username": test_username
    }
    
    print(f"📝 Test User Data:")
    print(f"   Email: {test_email}")
    print(f"   Username: {test_username}")
    print(f"   Password: [HIDDEN]")
    print()
    
    # Test registration with extended timeout and detailed error handling
    url = f"{BASE_URL}/auth/register"
    headers = {"Content-Type": "application/json"}
    
    print(f"🚀 Making registration request to: {url}")
    print(f"📤 Request headers: {headers}")
    print(f"📤 Request data: {json.dumps(registration_data, indent=2)}")
    print()
    
    try:
        start_time = time.time()
        response = requests.post(
            url, 
            json=registration_data, 
            headers=headers, 
            timeout=120  # Extended timeout
        )
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📥 Status code: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 201:
            data = response.json()
            print("✅ REGISTRATION SUCCESSFUL!")
            print(f"📄 Response data: {json.dumps(data, indent=2)}")
            
            # Test login with the same credentials
            print("\n🔐 Testing login with registered user...")
            login_data = {
                "email": test_email,
                "password": test_password
            }
            
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json=login_data,
                headers=headers,
                timeout=60
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                print("✅ LOGIN SUCCESSFUL!")
                access_token = login_data.get("access_token")
                
                # Test protected route
                print("\n🔒 Testing protected route access...")
                auth_headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                }
                
                me_response = requests.get(
                    f"{BASE_URL}/auth/me",
                    headers=auth_headers,
                    timeout=60
                )
                
                if me_response.status_code == 200:
                    user_data = me_response.json()
                    print("✅ PROTECTED ROUTE ACCESS SUCCESSFUL!")
                    print(f"📄 User data: {json.dumps(user_data, indent=2)}")
                    
                    # Test categories endpoint with authentication
                    print("\n📂 Testing categories endpoint with authentication...")
                    categories_response = requests.get(
                        f"{BASE_URL}/categories",
                        headers=auth_headers,
                        timeout=60
                    )
                    
                    if categories_response.status_code == 200:
                        categories = categories_response.json()
                        print(f"✅ CATEGORIES ACCESS SUCCESSFUL! Retrieved {len(categories)} categories")
                    else:
                        print(f"❌ Categories access failed: {categories_response.status_code}")
                        try:
                            error_data = categories_response.json()
                            print(f"📄 Error response: {json.dumps(error_data, indent=2)}")
                        except:
                            print(f"📄 Raw response: {categories_response.text}")
                    
                else:
                    print(f"❌ Protected route access failed: {me_response.status_code}")
                    try:
                        error_data = me_response.json()
                        print(f"📄 Error response: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"📄 Raw response: {me_response.text}")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                try:
                    error_data = login_response.json()
                    print(f"📄 Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📄 Raw response: {login_response.text}")
            
        else:
            print(f"❌ REGISTRATION FAILED!")
            print(f"📄 Status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Raw response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("❌ REGISTRATION FAILED: Request timed out after 120 seconds")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ REGISTRATION FAILED: Connection error - {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ REGISTRATION FAILED: Request error - {e}")
    except Exception as e:
        print(f"❌ REGISTRATION FAILED: Unexpected error - {e}")

def test_categories_without_auth():
    """Test categories endpoint without authentication to see if it requires auth"""
    print("\n📂 Testing categories endpoint without authentication...")
    
    try:
        response = requests.get(f"{BASE_URL}/categories", timeout=60)
        print(f"📥 Status code: {response.status_code}")
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories accessible without auth! Retrieved {len(categories)} categories")
        elif response.status_code == 401 or response.status_code == 403:
            print("✅ Categories properly require authentication")
            try:
                error_data = response.json()
                print(f"📄 Auth error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Raw response: {response.text}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📄 Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Categories test failed: {e}")

def main():
    """Main test execution"""
    test_categories_without_auth()
    test_registration_with_detailed_logging()

if __name__ == "__main__":
    main()