"""
Account Deletion Service
Handles both soft delete (deactivate) and hard delete (complete removal) of user accounts
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from database import db
from bson import ObjectId
from services.user_service import UserService

logger = logging.getLogger(__name__)

class AccountDeletionService:
    def __init__(self):
        self.db = db
        self.users_collection = db.users
        self.transactions_collection = db.transactions
        self.sms_collection = db.sms_transactions
        self.phone_verification_collection = db.phone_verification
        self.budget_limits_collection = db.budget_limits
        self.password_reset_tokens_collection = db.password_reset_tokens
        self.deletion_logs_collection = db.account_deletion_logs
        
    async def get_account_data_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of user's data before deletion"""
        try:
            user_obj_id = ObjectId(user_id)
            
            # Get user info
            user = await self.users_collection.find_one({"_id": user_obj_id})
            if not user:
                return {"error": "User not found"}
            
            # Count all user-related data
            transactions_count = await self.transactions_collection.count_documents({"user_id": user_id})
            sms_count = await self.sms_collection.count_documents({"user_id": user_id})
            budget_limits_count = await self.budget_limits_collection.count_documents({"user_id": user_id})
            phone_records_count = await self.phone_verification_collection.count_documents({"user_id": user_id})
            reset_tokens_count = await self.password_reset_tokens_collection.count_documents({"user_id": user_id})
            
            # Get recent activity
            recent_transactions = await self.transactions_collection.find(
                {"user_id": user_id}
            ).sort("date", -1).limit(5).to_list(length=5)
            
            recent_sms = await self.sms_collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(5).to_list(length=5)
            
            return {
                "user_id": user_id,
                "email": user.get("email"),
                "username": user.get("username"),
                "created_at": user.get("created_at"),
                "is_active": user.get("is_active", True),
                "data_summary": {
                    "transactions_count": transactions_count,
                    "sms_count": sms_count,
                    "budget_limits_count": budget_limits_count,
                    "phone_records_count": phone_records_count,
                    "reset_tokens_count": reset_tokens_count
                },
                "recent_activity": {
                    "transactions": [
                        {
                            "id": str(t.get("_id")),
                            "amount": t.get("amount"),
                            "description": t.get("description"),
                            "date": t.get("date")
                        } for t in recent_transactions
                    ],
                    "sms": [
                        {
                            "id": str(s.get("_id")),
                            "phone_number": s.get("phone_number"),
                            "timestamp": s.get("timestamp"),
                            "processed": s.get("processed", False)
                        } for s in recent_sms
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting account data summary for {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def soft_delete_account(self, user_id: str, reason: str = None) -> Dict[str, Any]:
        """Soft delete: Deactivate account but preserve data"""
        try:
            user_obj_id = ObjectId(user_id)
            
            # Get user info before deletion
            user = await self.users_collection.find_one({"_id": user_obj_id})
            if not user:
                return {"success": False, "error": "User not found"}
            
            if not user.get("is_active", True):
                return {"success": False, "error": "Account is already deactivated"}
            
            # Soft delete: Mark as inactive
            await self.users_collection.update_one(
                {"_id": user_obj_id},
                {"$set": {
                    "is_active": False,
                    "deleted_at": datetime.utcnow(),
                    "deletion_type": "soft",
                    "deletion_reason": reason or "User requested account deactivation",
                    "updated_at": datetime.utcnow()
                }}
            )
            
            # Log the deletion
            await self.deletion_logs_collection.insert_one({
                "user_id": user_id,
                "email": user.get("email"),
                "username": user.get("username"),
                "deletion_type": "soft",
                "reason": reason or "User requested account deactivation",
                "deleted_at": datetime.utcnow(),
                "data_preserved": True
            })
            
            logger.info(f"Account soft deleted for user {user_id}")
            
            return {
                "success": True,
                "message": "Account has been deactivated successfully",
                "deletion_type": "soft",
                "data_preserved": True,
                "can_be_restored": True
            }
            
        except Exception as e:
            logger.error(f"Error soft deleting account for {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def hard_delete_account(self, user_id: str, reason: str = None) -> Dict[str, Any]:
        """Hard delete: Complete removal of account and all associated data"""
        try:
            user_obj_id = ObjectId(user_id)
            
            # Get user info and data summary before deletion
            user = await self.users_collection.find_one({"_id": user_obj_id})
            if not user:
                return {"success": False, "error": "User not found"}
            
            data_summary = await self.get_account_data_summary(user_id)
            
            # Log the deletion before performing it
            deletion_log = {
                "user_id": user_id,
                "email": user.get("email"),
                "username": user.get("username"),
                "deletion_type": "hard",
                "reason": reason or "User requested complete account deletion",
                "deleted_at": datetime.utcnow(),
                "data_preserved": False,
                "data_summary": data_summary.get("data_summary", {}),
                "final_data_export": data_summary
            }
            
            await self.deletion_logs_collection.insert_one(deletion_log)
            
            # Delete all associated data
            deletion_results = {}
            
            # Delete transactions
            result = await self.transactions_collection.delete_many({"user_id": user_id})
            deletion_results["transactions_deleted"] = result.deleted_count
            
            # Delete SMS records
            result = await self.sms_collection.delete_many({"user_id": user_id})
            deletion_results["sms_deleted"] = result.deleted_count
            
            # Delete budget limits
            result = await self.budget_limits_collection.delete_many({"user_id": user_id})
            deletion_results["budget_limits_deleted"] = result.deleted_count
            
            # Delete phone verification records
            result = await self.phone_verification_collection.delete_many({"user_id": user_id})
            deletion_results["phone_records_deleted"] = result.deleted_count
            
            # Delete password reset tokens
            result = await self.password_reset_tokens_collection.delete_many({"user_id": user_id})
            deletion_results["reset_tokens_deleted"] = result.deleted_count
            
            # Finally, delete the user record
            result = await self.users_collection.delete_one({"_id": user_obj_id})
            deletion_results["user_deleted"] = result.deleted_count > 0
            
            if deletion_results["user_deleted"]:
                logger.info(f"Account hard deleted for user {user_id}")
                
                return {
                    "success": True,
                    "message": "Account and all associated data have been permanently deleted",
                    "deletion_type": "hard",
                    "data_preserved": False,
                    "can_be_restored": False,
                    "deletion_results": deletion_results
                }
            else:
                return {"success": False, "error": "Failed to delete user account"}
            
        except Exception as e:
            logger.error(f"Error hard deleting account for {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def restore_soft_deleted_account(self, user_id: str) -> Dict[str, Any]:
        """Restore a soft-deleted account"""
        try:
            user_obj_id = ObjectId(user_id)
            
            # Get user info
            user = await self.users_collection.find_one({"_id": user_obj_id})
            if not user:
                return {"success": False, "error": "User not found"}
            
            if user.get("is_active", True):
                return {"success": False, "error": "Account is already active"}
            
            if user.get("deletion_type") == "hard":
                return {"success": False, "error": "Cannot restore hard-deleted account"}
            
            # Restore account
            await self.users_collection.update_one(
                {"_id": user_obj_id},
                {"$set": {
                    "is_active": True,
                    "restored_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                },
                "$unset": {
                    "deleted_at": "",
                    "deletion_type": "",
                    "deletion_reason": ""
                }}
            )
            
            # Log the restoration
            await self.deletion_logs_collection.insert_one({
                "user_id": user_id,
                "email": user.get("email"),
                "username": user.get("username"),
                "action": "restored",
                "restored_at": datetime.utcnow(),
                "previous_deletion_type": "soft"
            })
            
            logger.info(f"Account restored for user {user_id}")
            
            return {
                "success": True,
                "message": "Account has been restored successfully",
                "restored_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error restoring account for {user_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        try:
            user_obj_id = ObjectId(user_id)
            
            # Get user info
            user = await self.users_collection.find_one({"_id": user_obj_id})
            if not user:
                return {"error": "User not found"}
            
            # Get all user data
            transactions = await self.transactions_collection.find({"user_id": user_id}).to_list(length=None)
            sms_records = await self.sms_collection.find({"user_id": user_id}).to_list(length=None)
            budget_limits = await self.budget_limits_collection.find({"user_id": user_id}).to_list(length=None)
            phone_records = await self.phone_verification_collection.find({"user_id": user_id}).to_list(length=None)
            
            # Convert ObjectIds to strings for JSON serialization
            def clean_data(data_list):
                for item in data_list:
                    if "_id" in item:
                        item["_id"] = str(item["_id"])
                return data_list
            
            export_data = {
                "user_profile": {
                    "id": str(user["_id"]),
                    "email": user.get("email"),
                    "username": user.get("username"),
                    "created_at": user.get("created_at"),
                    "is_active": user.get("is_active"),
                    "role": user.get("role")
                },
                "transactions": clean_data(transactions),
                "sms_records": clean_data(sms_records),
                "budget_limits": clean_data(budget_limits),
                "phone_records": clean_data(phone_records),
                "export_metadata": {
                    "exported_at": datetime.utcnow(),
                    "total_transactions": len(transactions),
                    "total_sms": len(sms_records),
                    "total_budget_limits": len(budget_limits),
                    "total_phone_records": len(phone_records)
                }
            }
            
            return {
                "success": True,
                "data": export_data
            }
            
        except Exception as e:
            logger.error(f"Error exporting user data for {user_id}: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup_old_deletion_logs(self, days_old: int = 90):
        """Clean up old deletion logs"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            result = await self.deletion_logs_collection.delete_many({
                "deleted_at": {"$lt": cutoff_date}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old deletion logs")
                
        except Exception as e:
            logger.error(f"Error cleaning up deletion logs: {str(e)}")

# Global instance
account_deletion_service = AccountDeletionService()