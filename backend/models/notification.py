from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class NotificationType(str, Enum):
    BUDGET_ALERT = "budget_alert"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_SUMMARY = "monthly_summary"
    TRANSACTION_CONFIRMATION = "transaction_confirmation"
    SMS_PROCESSING = "sms_processing"
    ACCOUNT_UPDATES = "account_updates"
    # Analytics notification types
    SPENDING_ALERT = "spending_alert"
    FINANCIAL_HEALTH_REPORT = "financial_health_report"
    BUDGET_RECOMMENDATIONS = "budget_recommendations"
    WEEKLY_ANALYTICS_DIGEST = "weekly_analytics_digest"

class NotificationFrequency(str, Enum):
    INSTANT = "instant"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    DISABLED = "disabled"

class UserNotificationPreferences(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    
    # Budget alerts
    budget_alerts_enabled: bool = True
    budget_alert_threshold: float = 0.8  # Alert when 80% of budget is spent
    
    # Summary emails
    weekly_summary_enabled: bool = True
    weekly_summary_day: int = 1  # Monday = 1, Sunday = 7
    monthly_summary_enabled: bool = True
    monthly_summary_day: int = 1  # 1st of each month
    
    # Transaction notifications
    transaction_confirmation_enabled: bool = False  # Disabled by default to avoid spam
    transaction_confirmation_threshold: float = 1000.0  # Only for transactions > 1000
    
    # SMS processing notifications
    sms_processing_enabled: bool = True
    sms_processing_frequency: NotificationFrequency = NotificationFrequency.DAILY
    
    # Account updates
    account_updates_enabled: bool = True
    
    # Analytics alerts preferences
    spending_alerts_enabled: bool = True
    spending_alert_severity_threshold: str = "medium"  # low, medium, high, critical
    financial_health_reports_enabled: bool = True
    budget_recommendations_enabled: bool = True
    weekly_analytics_digest_enabled: bool = True
    
    # Email preferences
    email_enabled: bool = True
    email_address: Optional[EmailStr] = None  # If different from user's main email
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True

class NotificationPreferencesUpdate(BaseModel):
    budget_alerts_enabled: Optional[bool] = None
    budget_alert_threshold: Optional[float] = None
    weekly_summary_enabled: Optional[bool] = None
    weekly_summary_day: Optional[int] = None
    monthly_summary_enabled: Optional[bool] = None
    monthly_summary_day: Optional[int] = None
    transaction_confirmation_enabled: Optional[bool] = None
    transaction_confirmation_threshold: Optional[float] = None
    sms_processing_enabled: Optional[bool] = None
    sms_processing_frequency: Optional[NotificationFrequency] = None
    account_updates_enabled: Optional[bool] = None
    # Analytics preferences
    spending_alerts_enabled: Optional[bool] = None
    spending_alert_severity_threshold: Optional[str] = None
    financial_health_reports_enabled: Optional[bool] = None
    budget_recommendations_enabled: Optional[bool] = None
    weekly_analytics_digest_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    email_address: Optional[EmailStr] = None

class NotificationLog(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    notification_type: NotificationType
    email_address: str
    subject: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivery_status: str = "sent"  # sent, delivered, failed, bounced
    error_message: Optional[str] = None
    
    class Config:
        populate_by_name = True