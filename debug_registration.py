#!/usr/bin/env python3
"""
Debug Registration Components
Test individual components of the registration system
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

async def test_password_hashing():
    """Test password hashing functionality"""
    print("🔐 Testing password hashing...")
    try:
        from services.auth import get_password_hash, verify_password
        
        test_password = "TestPassword123!"
        hashed = get_password_hash(test_password)
        print(f"✅ Password hashed successfully: {hashed[:20]}...")
        
        # Test verification
        is_valid = verify_password(test_password, hashed)
        print(f"✅ Password verification: {is_valid}")
        
        return True
    except Exception as e:
        print(f"❌ Password hashing error: {e}")
        return False

async def test_jwt_token():
    """Test JWT token creation"""
    print("\n🎫 Testing JWT token creation...")
    try:
        from services.auth import create_user_token
        
        test_user_id = "test_user_123"
        test_email = "test@example.com"
        
        token, expires_at = create_user_token(test_user_id, test_email)
        print(f"✅ JWT token created successfully: {token[:20]}...")
        print(f"✅ Token expires at: {expires_at}")
        
        return True
    except Exception as e:
        print(f"❌ JWT token error: {e}")
        return False

async def test_database_connection():
    """Test database connection"""
    print("\n🗄️  Testing database connection...")
    try:
        from database import db
        
        # Test ping
        result = await db.command("ping")
        print(f"✅ Database ping successful: {result}")
        
        # Test users collection
        count = await db.users.count_documents({})
        print(f"✅ Users collection accessible: {count} users")
        
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

async def test_user_model():
    """Test user model creation"""
    print("\n👤 Testing user model...")
    try:
        from models.user import UserCreate, UserResponse, User
        from datetime import datetime
        
        # Test UserCreate
        user_create = UserCreate(
            email="test@example.com",
            username="testuser",
            password="TestPass123!"
        )
        print(f"✅ UserCreate model: {user_create.email}")
        
        # Test UserResponse
        user_response = UserResponse(
            id="test_id_123",
            email="test@example.com",
            username="testuser",
            role="user",
            is_active=True,
            created_at=datetime.utcnow()
        )
        print(f"✅ UserResponse model: {user_response.id}")
        
        return True
    except Exception as e:
        print(f"❌ User model error: {e}")
        return False

async def test_user_service():
    """Test user service functionality"""
    print("\n🔧 Testing user service...")
    try:
        from services.user_service import UserService
        from models.user import UserCreate
        import time
        
        # Create a test user
        timestamp = int(time.time())
        test_user = UserCreate(
            email=f"debug{timestamp}@test.com",
            username=f"debug{timestamp}",
            password="DebugPass123!"
        )
        
        print(f"📧 Creating test user: {test_user.email}")
        
        # This is where the error might be occurring
        user_response = await UserService.create_user(test_user)
        print(f"✅ User created successfully: {user_response.id}")
        
        # Test authentication
        user = await UserService.authenticate_user(test_user.email, test_user.password)
        if user:
            print(f"✅ User authentication successful: {user.email}")
        else:
            print("❌ User authentication failed")
        
        return True
    except Exception as e:
        print(f"❌ User service error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_imports():
    """Test all required imports"""
    print("\n📦 Testing imports...")
    try:
        # Test core imports
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
        
        import motor
        print(f"✅ Motor: {motor.version}")
        
        import pymongo
        print(f"✅ PyMongo: {pymongo.version}")
        
        import jose
        print(f"✅ Jose: Available")
        
        import passlib
        print(f"✅ Passlib: {passlib.__version__}")
        
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        print(f"✅ Bcrypt context: Available")
        
        import pydantic
        print(f"✅ Pydantic: {pydantic.__version__}")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def main():
    """Run all debug tests"""
    print("🐛 REGISTRATION DEBUG TESTING")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Password Hashing", test_password_hashing),
        ("JWT Token", test_jwt_token),
        ("Database Connection", test_database_connection),
        ("User Model", test_user_model),
        ("User Service", test_user_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 DEBUG TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    failed_tests = [name for name, result in results if not result]
    if failed_tests:
        print(f"\n🔍 FAILED COMPONENTS: {', '.join(failed_tests)}")
        print("These components need to be fixed for registration to work.")
    else:
        print("\n🎉 All components working! Registration should be functional.")

if __name__ == "__main__":
    asyncio.run(main())