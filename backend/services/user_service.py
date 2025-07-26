import os
from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from models.user import User, UserCreate, UserResponse, UserRole
from services.auth import get_password_hash, verify_password
from fastapi import HTTPException, status

# MongoDB connection
client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client[os.getenv("DB_NAME", "budget_planner")]
users_collection = db.users

class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if user already exists
        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_username = await users_collection.find_one({"username": user_data.username})
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user document
        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "password_hash": get_password_hash(user_data.password),
            "role": UserRole.USER,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        try:
            result = await users_collection.insert_one(user_dict)
            user_dict["_id"] = str(result.inserted_id)
            
            return UserResponse(
                id=str(result.inserted_id),
                email=user_dict["email"],
                username=user_dict["username"],
                role=user_dict["role"],
                is_active=user_dict["is_active"],
                created_at=user_dict["created_at"]
            )
            
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        user_doc = await users_collection.find_one({"email": email, "is_active": True})
        if not user_doc:
            return None
        
        if not verify_password(password, user_doc["password_hash"]):
            return None
        
        user_doc["id"] = str(user_doc["_id"])
        user_doc.pop("_id", None)  # Remove _id to avoid conflicts
        return User(**user_doc)
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            from bson import ObjectId
            user_doc = await users_collection.find_one({"_id": ObjectId(user_id), "is_active": True})
            if user_doc:
                user_doc["id"] = str(user_doc["_id"])
                user_doc.pop("_id", None)  # Remove _id to avoid conflicts
                return User(**user_doc)
            return None
        except Exception:
            return None
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        user_doc = await users_collection.find_one({"email": email, "is_active": True})
        if user_doc:
            user_doc["id"] = str(user_doc["_id"])
            user_doc.pop("_id", None)  # Remove _id to avoid conflicts
            return User(**user_doc)
        return None
    
    @staticmethod
    async def update_user_activity(user_id: str):
        """Update user's last activity timestamp"""
        try:
            from bson import ObjectId
            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"updated_at": datetime.utcnow()}}
            )
        except Exception:
            pass
    
    @staticmethod
    async def get_all_users() -> list[UserResponse]:
        """Get all users (admin only)"""
        users = []
        async for user_doc in users_collection.find({"is_active": True}):
            users.append(UserResponse(
                id=str(user_doc["_id"]),
                email=user_doc["email"],
                username=user_doc["username"],
                role=user_doc["role"],
                is_active=user_doc["is_active"],
                created_at=user_doc["created_at"]
            ))
        return users