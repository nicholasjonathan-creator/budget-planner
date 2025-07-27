#!/usr/bin/env python3
"""
Minimal test to isolate the registration issue
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

async def test_registration_components():
    """Test each component of the registration process"""
    print("🔍 Testing Registration Components")
    
    # Test 1: Import all required modules
    try:
        from models.user import UserCreate, UserResponse
        from services.user_service import UserService
        from services.auth import create_user_token, get_password_hash
        from services.email_templates import EmailTemplates
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Create test user data
    try:
        import time
        timestamp = int(time.time())
        user_data = UserCreate(
            email=f'testuser{timestamp}@budgetplanner.com',
            password='SecurePass123!',
            username=f'testuser{timestamp}'
        )
        print("✅ User data creation successful")
    except Exception as e:
        print(f"❌ User data creation failed: {e}")
        return False
    
    # Test 3: Test password hashing
    try:
        password_hash = get_password_hash(user_data.password)
        print("✅ Password hashing successful")
    except Exception as e:
        print(f"❌ Password hashing failed: {e}")
        return False
    
    # Test 4: Test user creation
    try:
        user = await UserService.create_user(user_data)
        print(f"✅ User creation successful: {user.id}")
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Test token creation
    try:
        access_token, expires_at = create_user_token(user.id, user.email)
        print(f"✅ Token creation successful: {access_token[:20]}...")
    except Exception as e:
        print(f"❌ Token creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 6: Test email service
    try:
        email_service = EmailTemplates()
        full_user = await UserService.get_user_by_id(user.id)
        if full_user:
            result = await email_service.send_welcome_email(full_user)
            print(f"✅ Email service test successful: {result}")
        else:
            print("❌ Could not get full user for email test")
    except Exception as e:
        print(f"❌ Email service failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("🎉 All registration components working!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_registration_components())
    exit(0 if success else 1)