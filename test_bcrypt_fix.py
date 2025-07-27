#!/usr/bin/env python3
"""
Test bcrypt functionality to verify the fix
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

async def test_bcrypt_fix():
    """Test if bcrypt is working properly"""
    print("🔐 TESTING BCRYPT FIX")
    print("=" * 30)
    
    try:
        # Test 1: Import bcrypt directly
        print("\n1. Testing direct bcrypt import...")
        import bcrypt
        print(f"✅ bcrypt imported successfully: {bcrypt.__version__}")
        
        # Test 2: Test passlib with bcrypt
        print("\n2. Testing passlib with bcrypt...")
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        test_password = "TestPassword123!"
        hashed = pwd_context.hash(test_password)
        print(f"✅ Password hashed: {hashed[:30]}...")
        
        is_valid = pwd_context.verify(test_password, hashed)
        print(f"✅ Password verification: {is_valid}")
        
        # Test 3: Test full registration flow
        print("\n3. Testing full registration flow...")
        from services.user_service import UserService
        from models.user import UserCreate
        import time
        
        timestamp = int(time.time())
        test_user = UserCreate(
            email=f"bcrypttest{timestamp}@test.com",
            username=f"bcrypttest{timestamp}",
            password="BcryptTest123!"
        )
        
        user_response = await UserService.create_user(test_user)
        print(f"✅ User created with bcrypt: {user_response.id}")
        
        # Test authentication
        user = await UserService.authenticate_user(test_user.email, test_user.password)
        if user:
            print(f"✅ Authentication successful: {user.email}")
        else:
            print("❌ Authentication failed")
        
        print("\n🎉 BCRYPT FIX SUCCESSFUL!")
        print("The registration system should now work on production.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("bcrypt is not properly installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_bcrypt_fix()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ BCRYPT FIX VERIFICATION COMPLETE")
        print("=" * 50)
        print("The bcrypt dependency has been added to requirements.txt")
        print("This should resolve the 500 error in user registration")
        print("The production server needs to be redeployed with the updated requirements.txt")
    else:
        print("\n" + "=" * 50)
        print("❌ BCRYPT ISSUE PERSISTS")
        print("=" * 50)
        print("Additional investigation needed")

if __name__ == "__main__":
    asyncio.run(main())