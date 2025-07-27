#!/usr/bin/env python3
"""
Focused Registration Testing for Budget Planner
Tests the registration system that should now work without email functionality
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Production backend URL
BASE_URL = "https://budget-planner-backendjuly.onrender.com/api"

def test_registration_system():
    """Test user registration with detailed debugging"""
    print("🔍 FOCUSED REGISTRATION TESTING")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed - DB: {data.get('database')}")
        else:
            print(f"❌ Health check failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Multiple registration attempts with different users
    print("\n2. Testing user registration (multiple attempts)...")
    
    for attempt in range(3):
        print(f"\n   Attempt {attempt + 1}:")
        
        # Generate unique test user
        timestamp = int(time.time()) + attempt
        test_email = f"user{timestamp}@example.com"
        test_password = "SecurePass123!"
        test_username = f"user{timestamp}"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "username": test_username
        }
        
        print(f"   📧 Email: {test_email}")
        print(f"   👤 Username: {test_username}")
        
        try:
            print("   🔄 Sending registration request...")
            response = requests.post(
                f"{BASE_URL}/auth/register", 
                json=registration_data,
                headers={"Content-Type": "application/json"},
                timeout=60  # Increased timeout
            )
            
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   ⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Registration successful!")
                print(f"   🔑 Token received: {bool(data.get('access_token'))}")
                print(f"   👤 User ID: {data.get('user', {}).get('id')}")
                
                # Test login with the same credentials
                print("\n   🔐 Testing login with same credentials...")
                login_data = {
                    "email": test_email,
                    "password": test_password
                }
                
                login_response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    print(f"   ✅ Login successful!")
                    
                    # Test protected route
                    token = login_data.get('access_token')
                    if token:
                        print("\n   🔒 Testing protected route access...")
                        me_response = requests.get(
                            f"{BASE_URL}/auth/me",
                            headers={"Authorization": f"Bearer {token}"},
                            timeout=30
                        )
                        
                        if me_response.status_code == 200:
                            user_info = me_response.json()
                            print(f"   ✅ Protected route access successful!")
                            print(f"   📧 User email: {user_info.get('email')}")
                            
                            # Test categories with authentication
                            print("\n   📂 Testing categories with authentication...")
                            categories_response = requests.get(
                                f"{BASE_URL}/categories",
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=30
                            )
                            
                            if categories_response.status_code == 200:
                                categories = categories_response.json()
                                print(f"   ✅ Categories retrieved: {len(categories)} categories")
                            else:
                                print(f"   ❌ Categories failed: {categories_response.status_code}")
                                try:
                                    error_data = categories_response.json()
                                    print(f"   📝 Error: {error_data}")
                                except:
                                    print(f"   📝 Raw response: {categories_response.text[:200]}")
                            
                            return True
                        else:
                            print(f"   ❌ Protected route failed: {me_response.status_code}")
                else:
                    print(f"   ❌ Login failed: {login_response.status_code}")
                    try:
                        error_data = login_response.json()
                        print(f"   📝 Login error: {error_data}")
                    except:
                        print(f"   📝 Raw login response: {login_response.text[:200]}")
                
            else:
                print(f"   ❌ Registration failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📝 Error details: {error_data}")
                except:
                    print(f"   📝 Raw response: {response.text[:200]}")
                
                # Check if it's a duplicate email error
                if response.status_code == 400:
                    print("   ℹ️  Might be duplicate email, trying next attempt...")
                    continue
                    
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timed out after 60 seconds")
        except requests.exceptions.ConnectionError as e:
            print(f"   🔌 Connection error: {e}")
        except Exception as e:
            print(f"   💥 Unexpected error: {e}")
        
        # Wait between attempts
        if attempt < 2:
            print("   ⏳ Waiting 2 seconds before next attempt...")
            time.sleep(2)
    
    return False

def test_categories_without_auth():
    """Test categories endpoint without authentication"""
    print("\n3. Testing categories without authentication...")
    
    try:
        response = requests.get(f"{BASE_URL}/categories", timeout=30)
        print(f"   📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            categories = response.json()
            print(f"   ✅ Categories retrieved without auth: {len(categories)} categories")
            return True
        elif response.status_code == 401 or response.status_code == 403:
            print(f"   ℹ️  Categories require authentication (expected)")
            return True
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   📝 Error: {error_data}")
            except:
                print(f"   📝 Raw response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   💥 Error: {e}")
        return False

def test_server_logs_simulation():
    """Test what might be happening on the server side"""
    print("\n4. Testing server-side behavior simulation...")
    
    # Test with minimal data
    print("   📝 Testing with minimal registration data...")
    minimal_data = {
        "email": f"minimal{int(time.time())}@test.com",
        "password": "Test123!",
        "username": f"minimal{int(time.time())}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=minimal_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"   📊 Minimal data status: {response.status_code}")
        if response.status_code != 201:
            try:
                error_data = response.json()
                print(f"   📝 Minimal data error: {error_data}")
            except:
                print(f"   📝 Raw response: {response.text[:200]}")
    except Exception as e:
        print(f"   💥 Minimal data error: {e}")
    
    # Test with different email formats
    print("   📧 Testing with different email formats...")
    email_formats = [
        f"test{int(time.time())}@gmail.com",
        f"user{int(time.time())}@yahoo.com",
        f"simple{int(time.time())}@test.co"
    ]
    
    for email in email_formats:
        try:
            test_data = {
                "email": email,
                "password": "TestPass123!",
                "username": email.split('@')[0]
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"   📧 {email}: {response.status_code}")
            if response.status_code == 201:
                print(f"   ✅ Success with {email}!")
                return True
                
        except Exception as e:
            print(f"   💥 Error with {email}: {e}")
    
    return False

def main():
    """Main test execution"""
    print("🚀 FOCUSED REGISTRATION SYSTEM TESTING")
    print("🎯 Testing registration without email functionality")
    print("🔗 Backend URL: https://budget-planner-backendjuly.onrender.com")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run focused tests
    registration_success = test_registration_system()
    categories_working = test_categories_without_auth()
    server_simulation = test_server_logs_simulation()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print("📊 FOCUSED TEST RESULTS")
    print("=" * 60)
    print(f"⏱️  Total Duration: {duration:.2f} seconds")
    print(f"🔐 Registration System: {'✅ WORKING' if registration_success else '❌ FAILING'}")
    print(f"📂 Categories Endpoint: {'✅ WORKING' if categories_working else '❌ FAILING'}")
    print(f"🔍 Server Behavior: {'✅ RESPONSIVE' if server_simulation else '❌ ISSUES'}")
    
    if registration_success:
        print("\n🎉 SUCCESS: User registration is working without email functionality!")
        print("✅ Complete authentication flow tested successfully")
        print("✅ JWT token generation and validation working")
        print("✅ Protected routes accessible after registration")
        return True
    else:
        print("\n⚠️  ISSUE: User registration is still not working")
        print("❌ Registration requests are failing or timing out")
        print("❌ Authentication system cannot be fully tested")
        
        print("\n🔍 POSSIBLE CAUSES:")
        print("• Server-side errors in user creation logic")
        print("• Database connection issues during user insertion")
        print("• Password hashing or validation errors")
        print("• JWT token generation failures")
        print("• MongoDB ObjectId or UUID conflicts")
        print("• Missing environment variables or configuration")
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)