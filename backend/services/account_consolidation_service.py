"""
Account Consolidation Service
Handles merging of user accounts and data consolidation for WhatsApp integration
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from database import db
from bson import ObjectId
from services.user_service import UserService

logger = logging.getLogger(__name__)

class AccountConsolidationService:
    def __init__(self):
        self.db = db
        self.users_collection = db.users
        self.transactions_collection = db.transactions
        self.sms_collection = db.sms_messages
        self.phone_verification_collection = db.phone_verification
        self.budget_limits_collection = db.budget_limits
        
    async def find_user_by_phone_number(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Find user associated with a phone number"""
        try:
            # Check phone verification collection
            phone_record = await self.phone_verification_collection.find_one(
                {"phone_number": phone_number, "verified": True}
            )
            
            if phone_record:
                user_id = phone_record.get("user_id")
                if user_id:
                    user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
                    if user:
                        user["id"] = str(user["_id"])
                        return user
            
            # Also check users collection for direct phone number field
            user = await self.users_collection.find_one({"phone_number": phone_number})
            if user:
                user["id"] = str(user["_id"])
                return user
                
            return None
            
        except Exception as e:
            logger.error(f"Error finding user by phone number {phone_number}: {str(e)}")
            return None
    
    async def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of user's data"""
        try:
            user_obj_id = ObjectId(user_id)
            
            # Get user info
            user = await self.users_collection.find_one({"_id": user_obj_id})
            if not user:
                return {"error": "User not found"}
            
            # Count transactions
            transaction_count = await self.transactions_collection.count_documents({"user_id": user_id})
            
            # Get recent transactions
            recent_transactions = await self.transactions_collection.find(
                {"user_id": user_id}
            ).sort("date", -1).limit(5).to_list(length=5)
            
            # Count SMS messages
            sms_count = await self.sms_collection.count_documents({"user_id": user_id})
            
            # Get phone verification info
            phone_verification = await self.phone_verification_collection.find_one(
                {"user_id": user_id, "verified": True}
            )
            
            # Count budget limits
            budget_limits_count = await self.budget_limits_collection.count_documents({"user_id": user_id})
            
            return {
                "user_id": user_id,
                "email": user.get("email"),
                "username": user.get("username"),
                "created_at": user.get("created_at"),
                "phone_number": phone_verification.get("phone_number") if phone_verification else None,
                "phone_verified": phone_verification.get("verified", False) if phone_verification else False,
                "transaction_count": transaction_count,
                "sms_count": sms_count,
                "budget_limits_count": budget_limits_count,
                "recent_transactions": [
                    {
                        "id": str(t.get("_id")),
                        "amount": t.get("amount"),
                        "description": t.get("description"),
                        "date": t.get("date"),
                        "type": t.get("type"),
                        "source": t.get("source")
                    }
                    for t in recent_transactions
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user data summary for {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def transfer_phone_number_association(self, phone_number: str, target_user_id: str) -> Dict[str, Any]:
        """Transfer phone number association to target user"""
        try:
            # First, find the current user with this phone number
            current_user = await self.find_user_by_phone_number(phone_number)
            if not current_user:
                return {"success": False, "error": "Phone number not found in any account"}
            
            current_user_id = current_user["id"]
            
            # Don't transfer if it's already associated with the target user
            if current_user_id == target_user_id:
                return {"success": True, "message": "Phone number already associated with target user"}
            
            # Update phone verification record to point to target user
            phone_update_result = await self.phone_verification_collection.update_one(
                {"phone_number": phone_number, "verified": True},
                {"$set": {"user_id": target_user_id, "updated_at": datetime.utcnow()}}
            )
            
            # Remove phone number from current user's record if it exists
            await self.users_collection.update_one(
                {"_id": ObjectId(current_user_id)},
                {"$unset": {"phone_number": "", "phone_verified": "", "phone_verified_at": ""}}
            )
            
            # Update target user's record with phone number
            await self.users_collection.update_one(
                {"_id": ObjectId(target_user_id)},
                {"$set": {
                    "phone_number": phone_number,
                    "phone_verified": True,
                    "phone_verified_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "success": True,
                "message": f"Phone number {phone_number} transferred to target user",
                "previous_user_id": current_user_id,
                "new_user_id": target_user_id,
                "phone_records_updated": phone_update_result.modified_count
            }
            
        except Exception as e:
            logger.error(f"Error transferring phone number {phone_number} to user {target_user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def consolidate_user_data(self, source_user_id: str, target_user_id: str) -> Dict[str, Any]:
        """Consolidate all data from source user to target user"""
        try:
            source_obj_id = ObjectId(source_user_id)
            target_obj_id = ObjectId(target_user_id)
            
            # Verify both users exist
            source_user = await self.users_collection.find_one({"_id": source_obj_id})
            target_user = await self.users_collection.find_one({"_id": target_obj_id})
            
            if not source_user or not target_user:
                return {"success": False, "error": "Source or target user not found"}
            
            consolidation_results = {}
            
            # Transfer transactions
            transaction_result = await self.transactions_collection.update_many(
                {"user_id": source_user_id},
                {"$set": {"user_id": target_user_id, "updated_at": datetime.utcnow()}}
            )
            consolidation_results["transactions_transferred"] = transaction_result.modified_count
            
            # Transfer SMS messages
            sms_result = await self.sms_collection.update_many(
                {"user_id": source_user_id},
                {"$set": {"user_id": target_user_id, "updated_at": datetime.utcnow()}}
            )
            consolidation_results["sms_messages_transferred"] = sms_result.modified_count
            
            # Transfer phone verification records
            phone_result = await self.phone_verification_collection.update_many(
                {"user_id": source_user_id},
                {"$set": {"user_id": target_user_id, "updated_at": datetime.utcnow()}}
            )
            consolidation_results["phone_records_transferred"] = phone_result.modified_count
            
            # Transfer budget limits
            budget_result = await self.budget_limits_collection.update_many(
                {"user_id": source_user_id},
                {"$set": {"user_id": target_user_id, "updated_at": datetime.utcnow()}}
            )
            consolidation_results["budget_limits_transferred"] = budget_result.modified_count
            
            # Mark source user as inactive (don't delete, keep for audit)
            await self.users_collection.update_one(
                {"_id": source_obj_id},
                {"$set": {
                    "is_active": False,
                    "consolidated_to": target_user_id,
                    "consolidated_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            
            return {
                "success": True,
                "message": f"Successfully consolidated data from user {source_user_id} to {target_user_id}",
                "source_user_email": source_user.get("email"),
                "target_user_email": target_user.get("email"),
                "consolidation_results": consolidation_results
            }
            
        except Exception as e:
            logger.error(f"Error consolidating data from {source_user_id} to {target_user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_consolidation_preview(self, phone_number: str, target_user_id: str) -> Dict[str, Any]:
        """Preview what data would be consolidated"""
        try:
            # Find user with phone number
            source_user = await self.find_user_by_phone_number(phone_number)
            if not source_user:
                return {"error": "No user found with this phone number"}
            
            source_user_id = source_user["id"]
            
            # Get data summaries
            source_data = await self.get_user_data_summary(source_user_id)
            target_data = await self.get_user_data_summary(target_user_id)
            
            return {
                "phone_number": phone_number,
                "source_account": source_data,
                "target_account": target_data,
                "consolidation_plan": {
                    "action": "transfer_phone_only" if source_user_id == target_user_id else "full_consolidation",
                    "data_to_transfer": {
                        "transactions": source_data.get("transaction_count", 0),
                        "sms_messages": source_data.get("sms_count", 0),
                        "budget_limits": source_data.get("budget_limits_count", 0),
                        "phone_verification": "Yes" if source_data.get("phone_verified") else "No"
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting consolidation preview: {str(e)}")
            return {"error": str(e)}

# Global instance
account_consolidation_service = AccountConsolidationService()