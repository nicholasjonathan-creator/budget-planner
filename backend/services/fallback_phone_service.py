"""
Temporary Phone Verification Fallback
This provides a backup phone verification system when Twilio is unavailable
"""

import os
import logging
import random
import string
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from database import db

logger = logging.getLogger(__name__)

class FallbackPhoneVerificationService:
    def __init__(self):
        self.db = db
        self.otp_expiry_minutes = int(os.getenv('OTP_EXPIRY_MINUTES', 10))
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def normalize_phone_number(self, phone_number: str) -> str:
        """Normalize phone number to consistent format"""
        # Remove all non-digit characters except +
        clean_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Ensure it starts with +
        if not clean_number.startswith('+'):
            # Assume Indian number if no country code
            if len(clean_number) == 10:
                clean_number = '+91' + clean_number
            elif len(clean_number) == 11 and clean_number.startswith('91'):
                clean_number = '+' + clean_number
            else:
                clean_number = '+' + clean_number
        
        return clean_number
    
    async def send_fallback_verification_otp(self, user_id: str, phone_number: str) -> Dict[str, Any]:
        """Send fallback verification (demo mode)"""
        try:
            # Normalize phone number
            normalized_phone = self.normalize_phone_number(phone_number)
            
            # Generate OTP
            otp = self.generate_otp()
            expiry_time = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)
            
            # Store OTP in database
            verification_data = {
                "user_id": user_id,
                "phone_number": normalized_phone,
                "otp": otp,
                "created_at": datetime.utcnow(),
                "expires_at": expiry_time,
                "verified": False,
                "attempts": 0,
                "method": "fallback_demo"
            }
            
            # Remove any existing OTP for this user
            await self.db.phone_verifications.delete_many({"user_id": user_id})
            
            # Insert new OTP record
            await self.db.phone_verifications.insert_one(verification_data)
            
            logger.info(f"Fallback OTP generated for {normalized_phone}: {otp}")
            
            return {
                "success": True,
                "message": f"Demo Mode: Your verification code is {otp}. In production, this would be sent via WhatsApp.",
                "phone_number": normalized_phone,
                "expires_in_minutes": self.otp_expiry_minutes,
                "demo_otp": otp,  # For demo purposes only
                "fallback_mode": True
            }
            
        except Exception as e:
            logger.error(f"Error in fallback verification: {e}")
            return {
                "success": False,
                "error": "Internal error occurred while setting up verification"
            }
    
    async def verify_fallback_otp(self, user_id: str, otp: str) -> Dict[str, Any]:
        """Verify the OTP for fallback mode"""
        try:
            # Find the OTP record
            verification_record = await self.db.phone_verifications.find_one({
                "user_id": user_id,
                "otp": otp,
                "verified": False
            })
            
            if not verification_record:
                # Increment attempt count for rate limiting
                await self.db.phone_verifications.update_one(
                    {"user_id": user_id, "verified": False},
                    {"$inc": {"attempts": 1}}
                )
                
                return {
                    "success": False,
                    "error": "Invalid verification code"
                }
            
            # Check if OTP has expired
            if datetime.utcnow() > verification_record['expires_at']:
                await self.db.phone_verifications.delete_one({"_id": verification_record["_id"]})
                return {
                    "success": False,
                    "error": "Verification code has expired. Please request a new one."
                }
            
            # Check attempts limit
            if verification_record.get('attempts', 0) >= 5:
                await self.db.phone_verifications.delete_one({"_id": verification_record["_id"]})
                return {
                    "success": False,
                    "error": "Too many invalid attempts. Please request a new verification code."
                }
            
            # Verify OTP is correct
            if verification_record['otp'] == otp:
                # Mark as verified
                await self.db.phone_verifications.update_one(
                    {"_id": verification_record["_id"]},
                    {"$set": {"verified": True, "verified_at": datetime.utcnow()}}
                )
                
                # Update user profile with verified phone number
                from bson import ObjectId
                await self.db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {
                        "$set": {
                            "phone_number": verification_record['phone_number'],
                            "phone_verified": True,
                            "phone_verified_at": datetime.utcnow(),
                            "verification_method": "fallback_demo"
                        }
                    }
                )
                
                logger.info(f"Fallback phone verified successfully for user {user_id}: {verification_record['phone_number']}")
                
                return {
                    "success": True,
                    "message": "Phone number verified successfully! (Demo Mode)",
                    "phone_number": verification_record['phone_number'],
                    "fallback_mode": True
                }
            else:
                # Increment attempt count
                await self.db.phone_verifications.update_one(
                    {"_id": verification_record["_id"]},
                    {"$inc": {"attempts": 1}}
                )
                
                return {
                    "success": False,
                    "error": "Invalid verification code"
                }
                
        except Exception as e:
            logger.error(f"Error verifying fallback OTP: {e}")
            return {
                "success": False,
                "error": "Internal error occurred during verification"
            }


# Initialize the fallback service
fallback_phone_service = FallbackPhoneVerificationService()