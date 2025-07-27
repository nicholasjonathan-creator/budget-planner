"""
Phone Verification Service for WhatsApp Integration
Implements secure phone number registration and OTP verification
"""

import os
import logging
import random
import string
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from database import db
import hashlib

logger = logging.getLogger(__name__)

class PhoneVerificationService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        self.otp_expiry_minutes = int(os.getenv('OTP_EXPIRY_MINUTES', 10))
        
        # Make Twilio optional - enable fallback mode if credentials not provided
        self.twilio_enabled = all([self.account_sid, self.auth_token, self.whatsapp_number])
        
        if self.twilio_enabled:
            self.client = Client(self.account_sid, self.auth_token)
            print("📱 Twilio WhatsApp service enabled")
        else:
            self.client = None
            print("📱 Twilio WhatsApp service disabled - running in fallback mode")
        
        self.db = db
    
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
    
    async def is_phone_already_registered(self, phone_number: str, exclude_user_id: str = None) -> bool:
        """Check if phone number is already registered by another user"""
        try:
            normalized_phone = self.normalize_phone_number(phone_number)
            
            query = {
                "phone_number": normalized_phone,
                "phone_verified": True
            }
            
            if exclude_user_id:
                query["_id"] = {"$ne": exclude_user_id}
            
            existing_user = await self.db.users.find_one(query)
            return existing_user is not None
            
        except Exception as e:
            logger.error(f"Error checking phone registration: {e}")
            return False
    
    async def send_verification_otp(self, user_id: str, phone_number: str) -> Dict[str, Any]:
        """Send OTP verification message via WhatsApp"""
        try:
            # Normalize phone number
            normalized_phone = self.normalize_phone_number(phone_number)
            
            # Check if phone is already registered by another user
            if await self.is_phone_already_registered(normalized_phone, user_id):
                return {
                    "success": False,
                    "error": "This phone number is already registered with another account"
                }
            
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
                "attempts": 0
            }
            
            # Remove any existing OTP for this user
            await self.db.phone_verifications.delete_many({"user_id": user_id})
            
            # Insert new OTP record
            await self.db.phone_verifications.insert_one(verification_data)
            
            # Check if Twilio is enabled
            if not self.twilio_enabled:
                logger.info(f"Twilio disabled - OTP for {normalized_phone}: {otp}")
                return {
                    "success": True,
                    "message": "Twilio disabled - check console for OTP",
                    "phone_number": normalized_phone,
                    "expires_in_minutes": self.otp_expiry_minutes,
                    "fallback_otp": otp  # Only for development/testing
                }
            
            # Send OTP via WhatsApp
            message_body = f"""🔐 Budget Planner Verification

Your verification code is: *{otp}*

This code will expire in {self.otp_expiry_minutes} minutes.

Please enter this code in the Budget Planner app to verify your phone number.

Do not share this code with anyone! 🛡️"""

            message = self.client.messages.create(
                body=message_body,
                from_=f'whatsapp:{self.whatsapp_number}',
                to=f'whatsapp:{normalized_phone}'
            )
            
            logger.info(f"OTP sent to {normalized_phone}: {message.sid}")
            
            return {
                "success": True,
                "message": "Verification code sent to your WhatsApp",
                "phone_number": normalized_phone,
                "expires_in_minutes": self.otp_expiry_minutes
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending OTP: {e}")
            return {
                "success": False,
                "error": "Failed to send verification code. Please check your phone number."
            }
        except Exception as e:
            logger.error(f"Error sending verification OTP: {e}")
            return {
                "success": False,
                "error": "Internal error occurred while sending verification code"
            }
    
    async def verify_otp(self, user_id: str, otp: str) -> Dict[str, Any]:
        """Verify the OTP entered by user"""
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
                            "phone_verified_at": datetime.utcnow()
                        }
                    }
                )
                
                # Send confirmation message
                await self.send_verification_success_message(verification_record['phone_number'])
                
                logger.info(f"Phone verified successfully for user {user_id}: {verification_record['phone_number']}")
                
                return {
                    "success": True,
                    "message": "Phone number verified successfully!",
                    "phone_number": verification_record['phone_number']
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
            logger.error(f"Error verifying OTP: {e}")
            return {
                "success": False,
                "error": "Internal error occurred during verification"
            }
    
    async def send_verification_success_message(self, phone_number: str):
        """Send success confirmation message"""
        try:
            success_message = """✅ Phone Verification Successful!

Your WhatsApp number is now linked to your Budget Planner account.

You can now:
📱 Forward bank SMS messages to this number
💰 Get automatic transaction tracking
📊 View transactions in your dashboard instantly

Start forwarding your bank SMS messages now!

Budget Planner - Built for India 🇮🇳"""

            message = self.client.messages.create(
                body=success_message,
                from_=f'whatsapp:{self.whatsapp_number}',
                to=f'whatsapp:{phone_number}'
            )
            
            logger.info(f"Verification success message sent to {phone_number}: {message.sid}")
            
        except Exception as e:
            logger.error(f"Error sending verification success message: {e}")
    
    async def resend_otp(self, user_id: str) -> Dict[str, Any]:
        """Resend OTP for existing verification"""
        try:
            # Find existing verification record
            verification_record = await self.db.phone_verifications.find_one({
                "user_id": user_id,
                "verified": False
            })
            
            if not verification_record:
                return {
                    "success": False,
                    "error": "No pending verification found. Please start the verification process again."
                }
            
            # Check if we can resend (rate limiting)
            time_since_created = datetime.utcnow() - verification_record['created_at']
            if time_since_created.total_seconds() < 60:  # 1 minute cooldown
                return {
                    "success": False,
                    "error": "Please wait at least 1 minute before requesting a new code"
                }
            
            # Send new OTP to the same phone number
            return await self.send_verification_otp(user_id, verification_record['phone_number'])
            
        except Exception as e:
            logger.error(f"Error resending OTP: {e}")
            return {
                "success": False,
                "error": "Internal error occurred while resending verification code"
            }
    
    async def get_user_by_verified_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get user by verified phone number - for WhatsApp message processing"""
        try:
            normalized_phone = self.normalize_phone_number(phone_number)
            
            user = await self.db.users.find_one({
                "phone_number": normalized_phone,
                "phone_verified": True
            })
            
            return user
            
        except Exception as e:
            logger.error(f"Error finding user by verified phone: {e}")
            return None
    
    async def remove_phone_verification(self, user_id: str) -> Dict[str, Any]:
        """Remove phone verification for user (unlink phone)"""
        try:
            from bson import ObjectId
            # Update user to remove phone verification
            await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$unset": {
                        "phone_number": "",
                        "phone_verified": "",
                        "phone_verified_at": ""
                    }
                }
            )
            
            # Remove any pending verifications
            await self.db.phone_verifications.delete_many({"user_id": user_id})
            
            return {
                "success": True,
                "message": "Phone number unlinked successfully"
            }
            
        except Exception as e:
            logger.error(f"Error removing phone verification: {e}")
            return {
                "success": False,
                "error": "Failed to unlink phone number"
            }


# Initialize the service
phone_verification_service = PhoneVerificationService()