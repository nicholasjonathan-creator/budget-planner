"""
Password Reset Service
Handles password reset tokens and email notifications
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from database import db
from services.auth import get_password_hash
from services.user_service import UserService
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class PasswordResetService:
    def __init__(self):
        self.db = db
        self.reset_tokens_collection = db.password_reset_tokens
        self.token_expiry_hours = int(os.getenv('PASSWORD_RESET_EXPIRY_HOURS', 24))
        
    def generate_reset_token(self) -> str:
        """Generate a secure reset token"""
        return secrets.token_urlsafe(32)
    
    async def initiate_password_reset(self, email: str) -> Dict[str, Any]:
        """Initiate password reset process"""
        try:
            # Check if user exists
            user = await UserService.get_user_by_email(email)
            if not user:
                # Don't reveal if email exists or not for security
                return {
                    "success": True,
                    "message": "If this email exists, you will receive a password reset link"
                }
            
            # Generate reset token
            reset_token = self.generate_reset_token()
            expires_at = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
            
            # Store reset token in database
            token_doc = {
                "user_id": user.id,
                "email": user.email,
                "token": reset_token,
                "expires_at": expires_at,
                "used": False,
                "created_at": datetime.utcnow()
            }
            
            await self.reset_tokens_collection.insert_one(token_doc)
            
            # TODO: Send email with reset link
            # For now, we'll return the token for testing
            logger.info(f"Password reset token generated for user {user.id}: {reset_token}")
            
            return {
                "success": True,
                "message": "Password reset link sent to your email",
                "reset_token": reset_token,  # Remove this in production
                "expires_in_hours": self.token_expiry_hours
            }
            
        except Exception as e:
            logger.error(f"Error initiating password reset: {str(e)}")
            return {
                "success": False,
                "error": "Failed to initiate password reset"
            }
    
    async def validate_reset_token(self, token: str) -> Dict[str, Any]:
        """Validate a password reset token"""
        try:
            token_doc = await self.reset_tokens_collection.find_one({
                "token": token,
                "used": False,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not token_doc:
                return {
                    "valid": False,
                    "error": "Invalid or expired reset token"
                }
            
            return {
                "valid": True,
                "user_id": token_doc["user_id"],
                "email": token_doc["email"]
            }
            
        except Exception as e:
            logger.error(f"Error validating reset token: {str(e)}")
            return {
                "valid": False,
                "error": "Failed to validate reset token"
            }
    
    async def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Reset user password using token"""
        try:
            # Validate token
            validation_result = await self.validate_reset_token(token)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            user_id = validation_result["user_id"]
            
            # Update user password
            from bson import ObjectId
            password_hash = get_password_hash(new_password)
            
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "password_hash": password_hash,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            # Mark token as used
            await self.reset_tokens_collection.update_one(
                {"token": token},
                {"$set": {"used": True, "used_at": datetime.utcnow()}}
            )
            
            logger.info(f"Password reset successful for user {user_id}")
            
            return {
                "success": True,
                "message": "Password reset successful"
            }
            
        except Exception as e:
            logger.error(f"Error resetting password: {str(e)}")
            return {
                "success": False,
                "error": "Failed to reset password"
            }
    
    async def cleanup_expired_tokens(self):
        """Clean up expired reset tokens"""
        try:
            result = await self.reset_tokens_collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} expired reset tokens")
                
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")

# Global instance
password_reset_service = PasswordResetService()