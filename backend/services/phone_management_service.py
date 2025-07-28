"""
Phone Number Management Service
Handles phone number changes, updates, and management
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from database import db
from bson import ObjectId
from services.phone_verification_service import PhoneVerificationService

logger = logging.getLogger(__name__)

class PhoneManagementService:
    def __init__(self):
        self.db = db
        self.users_collection = db.users
        self.phone_verification_collection = db.phone_verification
        self.phone_history_collection = db.phone_number_history
        self.verification_service = PhoneVerificationService()
        
    async def get_phone_status(self, user_id: str) -> Dict[str, Any]:
        """Get current phone number status for user"""
        try:
            # Get current phone verification record
            phone_record = await self.phone_verification_collection.find_one({
                "user_id": user_id,
                "verified": True
            })
            
            if phone_record:
                return {
                    "has_phone": True,
                    "phone_number": phone_record.get("phone_number"),
                    "verified": phone_record.get("verified", False),
                    "verified_at": phone_record.get("verified_at"),
                    "can_change": True
                }
            else:
                return {
                    "has_phone": False,
                    "phone_number": None,
                    "verified": False,
                    "verified_at": None,
                    "can_change": False
                }
                
        except Exception as e:
            logger.error(f"Error getting phone status for user {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def initiate_phone_change(self, user_id: str, new_phone_number: str) -> Dict[str, Any]:
        """Initiate phone number change process"""
        try:
            # Get current phone number
            current_phone_record = await self.phone_verification_collection.find_one({
                "user_id": user_id,
                "verified": True
            })
            
            current_phone = current_phone_record.get("phone_number") if current_phone_record else None
            
            # Check if new number is same as current
            if current_phone == new_phone_number:
                return {
                    "success": False,
                    "error": "New phone number is the same as current phone number"
                }
            
            # Check if new phone number is already verified by another user
            existing_phone = await self.phone_verification_collection.find_one({
                "phone_number": new_phone_number,
                "verified": True,
                "user_id": {"$ne": user_id}
            })
            
            if existing_phone:
                return {
                    "success": False,
                    "error": "Phone number is already verified by another user",
                    "requires_consolidation": True,
                    "existing_user_id": existing_phone.get("user_id")
                }
            
            # Store change request in history
            change_request = {
                "user_id": user_id,
                "old_phone_number": current_phone,
                "new_phone_number": new_phone_number,
                "change_initiated_at": datetime.utcnow(),
                "change_status": "pending",
                "verification_required": True
            }
            
            await self.phone_history_collection.insert_one(change_request)
            
            # Initiate verification for new phone number
            verification_result = await self.verification_service.send_verification_otp(
                user_id, new_phone_number
            )
            
            if verification_result.get("success"):
                return {
                    "success": True,
                    "message": "Phone number change initiated. Please verify the new number.",
                    "verification_sent": True,
                    "new_phone_number": new_phone_number,
                    "old_phone_number": current_phone
                }
            else:
                return {
                    "success": False,
                    "error": verification_result.get("error", "Failed to send verification code")
                }
                
        except Exception as e:
            logger.error(f"Error initiating phone change for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def complete_phone_change(self, user_id: str, new_phone_number: str, verification_code: str) -> Dict[str, Any]:
        """Complete phone number change after verification"""
        try:
            # Verify the new phone number
            verification_result = await self.verification_service.verify_phone_number(
                user_id, new_phone_number, verification_code
            )
            
            if not verification_result.get("success"):
                return {
                    "success": False,
                    "error": verification_result.get("error", "Phone verification failed")
                }
            
            # Get current phone record
            current_phone_record = await self.phone_verification_collection.find_one({
                "user_id": user_id,
                "verified": True
            })
            
            old_phone = current_phone_record.get("phone_number") if current_phone_record else None
            
            # Update phone number history
            await self.phone_history_collection.update_one(
                {
                    "user_id": user_id,
                    "new_phone_number": new_phone_number,
                    "change_status": "pending"
                },
                {"$set": {
                    "change_status": "completed",
                    "change_completed_at": datetime.utcnow(),
                    "verification_success": True
                }}
            )
            
            # Deactivate old phone verification record
            if current_phone_record:
                await self.phone_verification_collection.update_one(
                    {"_id": current_phone_record["_id"]},
                    {"$set": {
                        "verified": False,
                        "deactivated_at": datetime.utcnow(),
                        "deactivation_reason": "Phone number changed"
                    }}
                )
            
            # Update user record
            await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "phone_number": new_phone_number,
                    "phone_verified": True,
                    "phone_verified_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            logger.info(f"Phone number successfully changed for user {user_id} from {old_phone} to {new_phone_number}")
            
            return {
                "success": True,
                "message": "Phone number successfully changed",
                "old_phone_number": old_phone,
                "new_phone_number": new_phone_number,
                "changed_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error completing phone change for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def remove_phone_number(self, user_id: str, reason: str = None) -> Dict[str, Any]:
        """Remove phone number from user account"""
        try:
            # Get current phone record
            current_phone_record = await self.phone_verification_collection.find_one({
                "user_id": user_id,
                "verified": True
            })
            
            if not current_phone_record:
                return {
                    "success": False,
                    "error": "No verified phone number found"
                }
            
            phone_number = current_phone_record.get("phone_number")
            
            # Add to history
            await self.phone_history_collection.insert_one({
                "user_id": user_id,
                "old_phone_number": phone_number,
                "new_phone_number": None,
                "action": "removed",
                "reason": reason or "User requested phone number removal",
                "removed_at": datetime.utcnow()
            })
            
            # Deactivate phone verification record
            await self.phone_verification_collection.update_one(
                {"_id": current_phone_record["_id"]},
                {"$set": {
                    "verified": False,
                    "deactivated_at": datetime.utcnow(),
                    "deactivation_reason": reason or "Phone number removed by user"
                }}
            )
            
            # Update user record
            await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$unset": {
                    "phone_number": "",
                    "phone_verified": "",
                    "phone_verified_at": ""
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }}
            )
            
            logger.info(f"Phone number {phone_number} removed from user {user_id}")
            
            return {
                "success": True,
                "message": "Phone number successfully removed",
                "removed_phone_number": phone_number,
                "removed_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error removing phone number for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_phone_history(self, user_id: str) -> Dict[str, Any]:
        """Get phone number change history for user"""
        try:
            cursor = self.phone_history_collection.find(
                {"user_id": user_id}
            ).sort("change_initiated_at", -1)
            
            history = []
            async for record in cursor:
                history.append({
                    "id": str(record["_id"]),
                    "old_phone_number": record.get("old_phone_number"),
                    "new_phone_number": record.get("new_phone_number"),
                    "action": record.get("action", "change"),
                    "change_status": record.get("change_status"),
                    "change_initiated_at": record.get("change_initiated_at"),
                    "change_completed_at": record.get("change_completed_at"),
                    "reason": record.get("reason")
                })
            
            return {
                "success": True,
                "history": history
            }
            
        except Exception as e:
            logger.error(f"Error getting phone history for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def cancel_phone_change(self, user_id: str, new_phone_number: str) -> Dict[str, Any]:
        """Cancel pending phone number change"""
        try:
            # Update history record
            result = await self.phone_history_collection.update_one(
                {
                    "user_id": user_id,
                    "new_phone_number": new_phone_number,
                    "change_status": "pending"
                },
                {"$set": {
                    "change_status": "cancelled",
                    "change_cancelled_at": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                # Remove any pending verification records
                await self.phone_verification_collection.delete_many({
                    "user_id": user_id,
                    "phone_number": new_phone_number,
                    "verified": False
                })
                
                return {
                    "success": True,
                    "message": "Phone number change cancelled successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "No pending phone number change found"
                }
                
        except Exception as e:
            logger.error(f"Error cancelling phone change for user {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}

# Global instance
phone_management_service = PhoneManagementService()