import os
from datetime import datetime
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from models.notification import UserNotificationPreferences, NotificationPreferencesUpdate
from models.user import User

# MongoDB connection
client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client[os.getenv("DB_NAME", "budget_planner")]
notification_preferences_collection = db.notification_preferences

class NotificationPreferencesService:
    @staticmethod
    async def get_user_preferences(user_id: str) -> UserNotificationPreferences:
        """Get user notification preferences, create default if not exists"""
        prefs_doc = await notification_preferences_collection.find_one({"user_id": user_id})
        
        if not prefs_doc:
            # Create default preferences
            default_prefs = UserNotificationPreferences(user_id=user_id)
            prefs_dict = default_prefs.dict(by_alias=True, exclude={"id"})
            result = await notification_preferences_collection.insert_one(prefs_dict)
            prefs_doc = prefs_dict
            prefs_doc["_id"] = result.inserted_id
        else:
            prefs_doc["_id"] = str(prefs_doc["_id"])
        
        return UserNotificationPreferences(**prefs_doc)
    
    @staticmethod
    async def update_user_preferences(
        user_id: str, 
        updates: NotificationPreferencesUpdate
    ) -> UserNotificationPreferences:
        """Update user notification preferences"""
        # Get current preferences
        current_prefs = await NotificationPreferencesService.get_user_preferences(user_id)
        
        # Apply updates
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Update in database
        await notification_preferences_collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        # Return updated preferences
        return await NotificationPreferencesService.get_user_preferences(user_id)
    
    @staticmethod
    async def should_send_notification(
        user_id: str, 
        notification_type: str
    ) -> tuple[bool, Optional[UserNotificationPreferences]]:
        """Check if a notification should be sent to user"""
        prefs = await NotificationPreferencesService.get_user_preferences(user_id)
        
        if not prefs.email_enabled:
            return False, prefs
        
        # Check specific notification type preferences
        if notification_type == "budget_alert" and not prefs.budget_alerts_enabled:
            return False, prefs
        elif notification_type == "weekly_summary" and not prefs.weekly_summary_enabled:
            return False, prefs
        elif notification_type == "monthly_summary" and not prefs.monthly_summary_enabled:
            return False, prefs
        elif notification_type == "transaction_confirmation" and not prefs.transaction_confirmation_enabled:
            return False, prefs
        elif notification_type == "sms_processing" and not prefs.sms_processing_enabled:
            return False, prefs
        elif notification_type == "account_updates" and not prefs.account_updates_enabled:
            return False, prefs
        
        return True, prefs
    
    @staticmethod
    async def get_budget_alert_threshold(user_id: str) -> float:
        """Get user's budget alert threshold"""
        prefs = await NotificationPreferencesService.get_user_preferences(user_id)
        return prefs.budget_alert_threshold
    
    @staticmethod
    async def get_transaction_confirmation_threshold(user_id: str) -> float:
        """Get user's transaction confirmation threshold"""
        prefs = await NotificationPreferencesService.get_user_preferences(user_id)
        return prefs.transaction_confirmation_threshold
    
    @staticmethod
    async def get_effective_email_address(user: User) -> str:
        """Get the effective email address for notifications"""
        prefs = await NotificationPreferencesService.get_user_preferences(user.id)
        return prefs.email_address or user.email