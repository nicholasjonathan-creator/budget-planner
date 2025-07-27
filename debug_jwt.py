#!/usr/bin/env python3
"""
Debug JWT token creation issue
"""
import requests
import json

def test_jwt_debug():
    """Test JWT creation on production server"""
    BASE_URL = 'https://budget-planner-backendjuly.onrender.com/api'
    
    # Create a test user with unique credentials
    import time
    timestamp = int(time.time())
    test_data = {
        'email': f'debuguser{timestamp}@budgetplanner.com',
        'password': 'DebugPass123!',
        'username': f'debuguser{timestamp}'
    }
    
    print("🔍 Testing JWT Debug on Production Server")
    print(f"URL: {BASE_URL}/auth/register")
    print(f"Test Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f'{BASE_URL}/auth/register',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"\n📊 Response Details:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 201:
            print("\n✅ Registration successful!")
            data = response.json()
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Token: {data.get('access_token', '')[:30]}...")
            return True
        else:
            print(f"\n❌ Registration failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("Could not parse error response as JSON")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"\n🔌 Connection error: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_jwt_debug()
    exit(0 if success else 1)