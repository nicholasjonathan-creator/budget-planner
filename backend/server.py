from fastapi import FastAPI, APIRouter, HTTPException, Depends, Body, status, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
import re
from bson import ObjectId

# Import our models and services
from models.transaction import (
    Transaction, TransactionCreate, BudgetLimit, BudgetLimitCreate, 
    Category, TransactionType, SMSTransaction
)
from models.user import User, UserCreate, UserLogin, UserResponse, Token
from models.notification import UserNotificationPreferences, NotificationPreferencesUpdate
from models.analytics import (
    SpendingTrend, FinancialHealthScore, SpendingPattern, BudgetRecommendation,
    SpendingAlert, AnalyticsSummary, AnalyticsTimeframe, AlertSeverity
)
from services.transaction_service import TransactionService
from services.sms_service import SMSService
from services.user_service import UserService
from services.auth import create_user_token
from services.email_templates import EmailTemplates
from services.notification_service import NotificationPreferencesService
from services.email_scheduler import email_scheduler
from services.production_email_config import production_email_config
from services.analytics_service import AnalyticsService
from services.analytics_email_service import AnalyticsEmailService
from services.whatsapp_service import whatsapp_processor
from dependencies.auth import get_current_user, get_current_active_user, get_admin_user, get_optional_user
from database import init_db, db

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Budget Planner API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
transaction_service = TransactionService()
sms_service = SMSService()
email_service = EmailTemplates()
analytics_service = AnalyticsService()
analytics_email_service = AnalyticsEmailService()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "Budget Planner API is running", "version": "1.0.0", "status": "healthy"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint for production monitoring"""
    try:
        # Check database connection
        await db.command("ping")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": "connected",
            "environment": os.environ.get("ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@api_router.get("/metrics")
async def get_metrics():
    """Basic metrics endpoint for monitoring"""
    try:
        # Get basic stats
        total_transactions = await db.transactions.count_documents({})
        total_sms = await db.sms_transactions.count_documents({})
        processed_sms = await db.sms_transactions.count_documents({"processed": True})
        
        return {
            "total_transactions": total_transactions,
            "total_sms": total_sms,
            "processed_sms": processed_sms,
            "success_rate": (processed_sms / total_sms * 100) if total_sms > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

# ==================== AUTHENTICATION ENDPOINTS ====================

@api_router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Create the user
        user = await UserService.create_user(user_data)
        
        # Create access token
        access_token, expires_at = create_user_token(user.id, user.email)
        
        # Send welcome email (in background)
        try:
            # Get full user object for email
            full_user = await UserService.get_user_by_id(user.id)
            if full_user:
                await email_service.send_welcome_email(full_user)
        except Exception as e:
            logger.warning(f"Failed to send welcome email to {user.email}: {e}")
            # Don't fail registration if email fails
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_at=expires_at,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@api_router.post("/auth/login", response_model=Token)
async def login_user(user_data: UserLogin):
    """Login a user"""
    try:
        # Authenticate user
        user = await UserService.authenticate_user(user_data.email, user_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token, expires_at = create_user_token(user.id, user.email)
        
        # Convert user to response format
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_at=expires_at,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@api_router.post("/auth/logout")
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should delete the token)"""
    return {"message": "Successfully logged out"}

@api_router.get("/auth/users", response_model=List[UserResponse])
async def get_all_users(admin_user: User = Depends(get_admin_user)):
    """Get all users (admin only)"""
    return await UserService.get_all_users()

# ==================== NOTIFICATION ENDPOINTS ====================

@api_router.get("/notifications/preferences", response_model=UserNotificationPreferences)
async def get_notification_preferences(current_user: User = Depends(get_current_active_user)):
    """Get current user's notification preferences"""
    try:
        return await NotificationPreferencesService.get_user_preferences(current_user.id)
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/notifications/preferences", response_model=UserNotificationPreferences)
async def update_notification_preferences(
    updates: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's notification preferences"""
    try:
        return await NotificationPreferencesService.update_user_preferences(current_user.id, updates)
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/test-email")
async def send_test_email(current_user: User = Depends(get_current_active_user)):
    """Send a test email to verify email configuration"""
    try:
        success = await email_service.send_welcome_email(current_user)
        if success:
            return {"message": "Test email sent successfully!", "email": current_user.email}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notifications/logs")
async def get_notification_logs(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user)
):
    """Get notification logs for current user"""
    try:
        logs = []
        async for log in db.notification_logs.find(
            {"user_id": current_user.id}
        ).sort("sent_at", -1).limit(limit):
            log["id"] = str(log["_id"])
            del log["_id"]
            logs.append(log)
        
        return logs
    except Exception as e:
        logger.error(f"Error getting notification logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PRODUCTION EMAIL ENDPOINTS ====================

@api_router.get("/notifications/production/status")
async def get_production_email_status(admin_user: User = Depends(get_admin_user)):
    """Get production email system status (admin only)"""
    try:
        config_status = await production_email_config.verify_sender_configuration()
        checklist = await production_email_config.get_production_checklist()
        
        scheduler_status = {
            'running': email_scheduler.is_running,
            'jobs': len(email_scheduler.scheduler.get_jobs()) if email_scheduler.scheduler else 0
        }
        
        return {
            'configuration': config_status,
            'production_checklist': checklist,
            'scheduler': scheduler_status,
            'environment': production_email_config.environment
        }
    except Exception as e:
        logger.error(f"Error getting production email status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/production/start-scheduler")
async def start_email_scheduler(admin_user: User = Depends(get_admin_user)):
    """Start the email scheduler (admin only)"""
    try:
        if not email_scheduler.is_running:
            email_scheduler.start()
            return {"message": "Email scheduler started successfully", "status": "running"}
        else:
            return {"message": "Email scheduler is already running", "status": "running"}
    except Exception as e:
        logger.error(f"Error starting email scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/production/stop-scheduler")
async def stop_email_scheduler(admin_user: User = Depends(get_admin_user)):
    """Stop the email scheduler (admin only)"""
    try:
        if email_scheduler.is_running:
            email_scheduler.stop()
            return {"message": "Email scheduler stopped successfully", "status": "stopped"}
        else:
            return {"message": "Email scheduler is not running", "status": "stopped"}
    except Exception as e:
        logger.error(f"Error stopping email scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notifications/production/checklist")
async def get_production_checklist(admin_user: User = Depends(get_admin_user)):
    """Get production readiness checklist (admin only)"""
    try:
        return await production_email_config.get_production_checklist()
    except Exception as e:
        logger.error(f"Error getting production checklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notifications/production/smtp-config")
async def get_smtp_config(admin_user: User = Depends(get_admin_user)):
    """Get production SMTP configuration options (admin only)"""
    try:
        return production_email_config.get_production_smtp_config()
    except Exception as e:
        logger.error(f"Error getting SMTP config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/production/trigger-budget-alerts")
async def trigger_budget_alerts(admin_user: User = Depends(get_admin_user)):
    """Manually trigger budget alerts for testing (admin only)"""
    try:
        await email_scheduler.send_budget_alerts()
        return {"message": "Budget alerts triggered successfully"}
    except Exception as e:
        logger.error(f"Error triggering budget alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/production/trigger-monthly-summaries")
async def trigger_monthly_summaries(admin_user: User = Depends(get_admin_user)):
    """Manually trigger monthly summaries for testing (admin only)"""
    try:
        await email_scheduler.send_monthly_summaries()
        return {"message": "Monthly summaries triggered successfully"}
    except Exception as e:
        logger.error(f"Error triggering monthly summaries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== TRANSACTION ENDPOINTS ====================

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new transaction"""
    try:
        result = await transaction_service.create_transaction(transaction, current_user.id)
        # Update budget spent amounts
        await transaction_service.update_budget_spent(
            transaction.date.month if transaction.date else datetime.now().month,
            transaction.date.year if transaction.date else datetime.now().year,
            current_user.id
        )
        return result
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(month: Optional[int] = None, year: Optional[int] = None, current_user: User = Depends(get_current_active_user)):
    """Get transactions by month/year"""
    try:
        return await transaction_service.get_transactions(month, year, current_user.id)
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str, current_user: User = Depends(get_current_active_user)):
    """Get a specific transaction"""
    try:
        transaction = await transaction_service.get_transaction_by_id(transaction_id, current_user.id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, updates: dict = Body(...), current_user: User = Depends(get_current_active_user)):
    """Update a transaction"""
    try:
        result = await transaction_service.update_transaction(transaction_id, updates, current_user.id)
        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a transaction"""
    try:
        success = await transaction_service.delete_transaction(transaction_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@api_router.get("/analytics/monthly-summary")
async def get_monthly_summary(month: int, year: int, current_user: User = Depends(get_current_active_user)):
    """Get monthly summary of income, expenses, and balance"""
    try:
        return await transaction_service.get_monthly_summary(month, year, current_user.id)
    except Exception as e:
        logger.error(f"Error getting monthly summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/category-totals")
async def get_category_totals(month: int, year: int, current_user: User = Depends(get_current_active_user)):
    """Get transaction totals by category"""
    try:
        return await transaction_service.get_category_totals(month, year, current_user.id)
    except Exception as e:
        logger.error(f"Error getting category totals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENHANCED ANALYTICS ENDPOINTS ====================

@api_router.get("/analytics/spending-trends", response_model=List[SpendingTrend])
async def get_spending_trends(
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY,
    periods: int = 6,
    current_user: User = Depends(get_current_active_user)
):
    """Get spending trends analysis over multiple periods"""
    try:
        return await analytics_service.get_spending_trends(current_user.id, timeframe, periods)
    except Exception as e:
        logger.error(f"Error getting spending trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/financial-health", response_model=FinancialHealthScore)
async def get_financial_health_score(current_user: User = Depends(get_current_active_user)):
    """Get comprehensive financial health score and recommendations"""
    try:
        return await analytics_service.calculate_financial_health_score(current_user.id)
    except Exception as e:
        logger.error(f"Error calculating financial health score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/spending-patterns", response_model=List[SpendingPattern])
async def get_spending_patterns(
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY,
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed spending patterns by category"""
    try:
        return await analytics_service.analyze_spending_patterns(current_user.id, timeframe)
    except Exception as e:
        logger.error(f"Error analyzing spending patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/budget-recommendations", response_model=List[BudgetRecommendation])
async def get_budget_recommendations(current_user: User = Depends(get_current_active_user)):
    """Get AI-powered budget recommendations"""
    try:
        return await analytics_service.generate_budget_recommendations(current_user.id)
    except Exception as e:
        logger.error(f"Error generating budget recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/spending-alerts", response_model=List[SpendingAlert])
async def get_spending_alerts(current_user: User = Depends(get_current_active_user)):
    """Get spending anomaly alerts"""
    try:
        return await analytics_service.detect_spending_anomalies(current_user.id)
    except Exception as e:
        logger.error(f"Error detecting spending anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analytics/mark-alert-read/{alert_id}")
async def mark_alert_read(alert_id: str, current_user: User = Depends(get_current_active_user)):
    """Mark a spending alert as read"""
    try:
        result = await db.spending_alerts.update_one(
            {"_id": ObjectId(alert_id), "user_id": current_user.id},
            {"$set": {"is_read": True}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"message": "Alert marked as read"}
    except Exception as e:
        logger.error(f"Error marking alert as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY,
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive analytics summary"""
    try:
        # Get individual components
        spending_trends = await analytics_service.get_spending_trends(current_user.id, timeframe, 3)
        financial_health = await analytics_service.calculate_financial_health_score(current_user.id)
        spending_patterns = await analytics_service.analyze_spending_patterns(current_user.id, timeframe)
        budget_recommendations = await analytics_service.generate_budget_recommendations(current_user.id)
        alerts = await analytics_service.detect_spending_anomalies(current_user.id)
        
        # Get current period summary
        current_date = datetime.now()
        if timeframe == AnalyticsTimeframe.MONTHLY:
            month = current_date.month - 1
            year = current_date.year
            monthly_summary = await transaction_service.get_monthly_summary(month, year, current_user.id)
            period = f"{year}-{month+1:02d}"
        else:
            monthly_summary = {"income": 0, "expense": 0, "balance": 0}
            period = f"Week {current_date.strftime('%U')}-{current_date.year}"
        
        return AnalyticsSummary(
            timeframe=timeframe,
            period=period,
            total_income=monthly_summary["income"],
            total_expenses=monthly_summary["expense"],
            net_balance=monthly_summary["balance"],
            spending_trends=spending_trends,
            financial_health=financial_health,
            spending_patterns=spending_patterns,
            budget_recommendations=budget_recommendations,
            alerts=alerts
        )
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS EMAIL ENDPOINTS ====================

@api_router.post("/analytics/send-spending-alerts")
async def send_spending_alerts(current_user: User = Depends(get_current_active_user)):
    """Manually trigger spending alerts email"""
    try:
        result = await analytics_email_service.process_and_send_spending_alerts(current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error sending spending alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analytics/send-financial-health-report")
async def send_financial_health_report(current_user: User = Depends(get_current_active_user)):
    """Manually trigger financial health report email"""
    try:
        result = await analytics_email_service.send_monthly_financial_health_report(current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error sending financial health report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analytics/send-budget-recommendations")
async def send_budget_recommendations(current_user: User = Depends(get_current_active_user)):
    """Manually trigger budget recommendations email"""
    try:
        result = await analytics_email_service.send_budget_recommendations(current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error sending budget recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analytics/send-weekly-digest")
async def send_weekly_digest(current_user: User = Depends(get_current_active_user)):
    """Manually trigger weekly analytics digest email"""
    try:
        result = await analytics_email_service.send_weekly_analytics_digest(current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error sending weekly digest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analytics/send-all-notifications")
async def send_all_analytics_notifications(current_user: User = Depends(get_current_active_user)):
    """Manually trigger all analytics notifications"""
    try:
        result = await analytics_email_service.trigger_immediate_analytics_alerts(current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error sending all analytics notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analytics/process-scheduled-notifications")
async def process_scheduled_analytics_notifications(current_user: User = Depends(get_current_active_user)):
    """Process scheduled analytics notifications (for cron jobs)"""
    try:
        result = await analytics_email_service.process_all_analytics_notifications(current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error processing scheduled notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BUDGET LIMITS ENDPOINTS ====================

@api_router.post("/budget-limits", response_model=BudgetLimit)
async def create_budget_limit(budget_limit: BudgetLimitCreate, current_user: User = Depends(get_current_active_user)):
    """Create or update a budget limit"""
    try:
        result = await transaction_service.create_budget_limit(budget_limit, current_user.id)
        # Update spent amounts
        await transaction_service.update_budget_spent(budget_limit.month, budget_limit.year, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error creating budget limit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/budget-limits", response_model=List[BudgetLimit])
async def get_budget_limits(month: int, year: int, current_user: User = Depends(get_current_active_user)):
    """Get budget limits for a specific month/year"""
    try:
        return await transaction_service.get_budget_limits(month, year, current_user.id)
    except Exception as e:
        logger.error(f"Error getting budget limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CATEGORIES ENDPOINTS ====================

@api_router.get("/categories", response_model=List[Category])
async def get_categories(current_user: User = Depends(get_current_active_user)):
    """Get all categories"""
    try:
        cursor = db.categories.find({}).sort("id", 1)
        categories = []
        async for doc in cursor:
            doc.pop('_id', None)  # Remove MongoDB _id
            categories.append(Category(**doc))
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SMS ENDPOINTS ====================

@api_router.post("/sms/receive")
async def receive_sms(phone_number: str = Body(...), message: str = Body(...), current_user: User = Depends(get_current_active_user)):
    """Receive and process SMS transaction"""
    try:
        result = await sms_service.receive_sms(phone_number, message, current_user.id)
        return result
    except Exception as e:
        logger.error(f"Error receiving SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sms/unprocessed")
async def get_unprocessed_sms():
    """Get all unprocessed SMS messages"""
    try:
        return await sms_service.get_unprocessed_sms()
    except Exception as e:
        logger.error(f"Error getting unprocessed SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/sms/reprocess/{sms_id}")
async def reprocess_sms(sms_id: str):
    """Reprocess a specific SMS"""
    try:
        result = await sms_service.reprocess_sms(sms_id)
        return result
    except Exception as e:
        logger.error(f"Error reprocessing SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sms/stats")
async def get_sms_stats():
    """Get SMS processing statistics"""
    try:
        return await sms_service.get_sms_stats()
    except Exception as e:
        logger.error(f"Error getting SMS stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/sms/simulate")
async def simulate_bank_sms(bank_type: str = "hdfc"):
    """Simulate bank SMS for testing"""
    try:
        return await sms_service.simulate_bank_sms(bank_type)
    except Exception as e:
        logger.error(f"Error simulating SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sms/failed")
async def get_failed_sms(current_user: User = Depends(get_current_active_user)):
    """Get all failed SMS messages for manual classification"""
    try:
        failed_sms = []
        # Filter by user_id for data isolation
        async for doc in db.sms_transactions.find({"processed": False, "user_id": current_user.id}):
            failed_sms.append({
                "id": str(doc["_id"]),
                "message": doc["message"],
                "phone_number": doc.get("phone_number", ""),
                "timestamp": doc.get("timestamp", ""),
                "reason": "Could not determine transaction type automatically"
            })
        
        return {"success": True, "failed_sms": failed_sms}
    except Exception as e:
        logger.error(f"Error fetching failed SMS: {e}")
        return {"success": False, "error": str(e)}

@api_router.post("/sms/manual-classify")
async def manual_classify_sms(request: dict, current_user: User = Depends(get_current_active_user)):
    """Manually classify a failed SMS message"""
    try:
        sms_id = request.get("sms_id")
        transaction_type = request.get("transaction_type")  # 'debit' or 'credit'
        amount = request.get("amount")  # User-provided amount
        description = request.get("description", "")
        currency = request.get("currency", "INR")  # Default to INR
        
        if not sms_id or not transaction_type or not amount:
            return {"success": False, "error": "Missing required fields"}
        
        # Get the original SMS
        sms_doc = await db.sms_transactions.find_one({"_id": ObjectId(sms_id)})
        if not sms_doc:
            return {"success": False, "error": "SMS not found"}
        
        # Extract account number from SMS if possible
        sms_text = sms_doc.get("message", "")
        account_number = "Unknown"
        
        # Try to extract account number using regex
        account_patterns = [
            r'account\s*([a-zA-Z]*\d+)',
            r'a/c\s*([a-zA-Z]*\d+)',
            r'card\s*([a-zA-Z]*\d+)',
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                account_number = match.group(1)
                break
        
        # Create transaction
        transaction_data = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,  # Associate with current user
            "type": "expense" if transaction_type == "debit" else "income",
            "category_id": 12,  # Other/Miscellaneous category
            "amount": float(amount),
            "description": description or f"Manual classification - {transaction_type}",
            "date": datetime.now(),
            "source": "sms_manual",
            "merchant": "Manual Entry",
            "account_number": account_number,
            "currency": currency,  # Add currency field
            "raw_data": {
                "sms_text": sms_text,
                "phone_number": sms_doc.get("phone_number", ""),
                "manual_classification": True,
                "classified_as": transaction_type,
                "currency": currency,
                "parsed_at": datetime.now().isoformat()
            }
        }
        
        # Insert transaction
        result = await db.transactions.insert_one(transaction_data)
        
        # Mark SMS as processed
        await db.sms_transactions.update_one(
            {"_id": ObjectId(sms_id)},
            {"$set": {"processed": True, "manual_classification": True}}
        )
        
        logger.info(f"Manual classification completed for SMS {sms_id} with currency {currency}")
        
        return {
            "success": True,
            "message": "Transaction classified successfully",
            "transaction_id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error in manual classification: {e}")
        return {"success": False, "error": str(e)}

# Include the router in the main app
app.include_router(api_router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and start email scheduler on startup"""
    await init_db()
    
    # Start email scheduler if in production
    if production_email_config.environment == 'production':
        try:
            email_scheduler.start()
            logger.info("Email scheduler started for production environment")
        except Exception as e:
            logger.error(f"Failed to start email scheduler: {e}")
    else:
        logger.info("Email scheduler not started (development environment)")
    
    logger.info("Budget Planner API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Stop email scheduler
    try:
        if email_scheduler.is_running:
            email_scheduler.stop()
            logger.info("Email scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping email scheduler: {e}")
    
    logger.info("Budget Planner API shutting down")

# ==================== ADMIN ENDPOINTS
@app.post("/api/admin/clear-sms-data")
async def clear_sms_data():
    """Clear all SMS-related data for testing purposes"""
    try:
        # Clear failed SMS collection
        failed_sms_collection = db.failed_sms
        await failed_sms_collection.delete_many({})
        
        # Clear all SMS transactions (transactions with source = 'sms' or 'sms_manual')
        transactions_collection = db.transactions
        result = await transactions_collection.delete_many({
            "source": {"$in": ["sms", "sms_manual"]}
        })
        
        # Clear any other SMS-related collections if they exist
        # You can add more cleanup here if needed
        
        logger.info("All SMS data cleared successfully")
        return {
            "success": True,
            "message": "All SMS data cleared successfully",
            "deleted_transactions": result.deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing SMS data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/clear-all-data")
async def clear_all_data():
    """Clear ALL data for complete system reset"""
    try:
        # Clear all transactions
        transactions_collection = db.transactions
        trans_result = await transactions_collection.delete_many({})
        
        # Clear all budget limits
        budget_limits_collection = db.budget_limits
        budget_result = await budget_limits_collection.delete_many({})
        
        # Clear failed SMS collection
        failed_sms_collection = db.failed_sms
        failed_result = await failed_sms_collection.delete_many({})
        
        # Clear SMS transactions collection
        sms_transactions_collection = db.sms_transactions
        sms_result = await sms_transactions_collection.delete_many({})
        
        # Keep categories but you can clear them too if needed
        # categories_collection = db.categories
        # cat_result = await categories_collection.delete_many({})
        
        logger.info("ALL data cleared successfully")
        return {
            "success": True,
            "message": "ALL data cleared successfully - system completely reset",
            "deleted_transactions": trans_result.deleted_count,
            "deleted_budget_limits": budget_result.deleted_count,
            "deleted_failed_sms": failed_result.deleted_count,
            "deleted_sms_transactions": sms_result.deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WhatsApp Webhook Endpoints
@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Webhook endpoint for receiving WhatsApp messages from Twilio
    """
    try:
        # Get form data from Twilio webhook
        form_data = await request.form()
        webhook_data = dict(form_data)
        
        # Validate webhook signature (optional but recommended for production)
        # signature = request.headers.get('X-Twilio-Signature', '')
        # url = str(request.url)
        # if not whatsapp_processor.validate_webhook(url, webhook_data, signature):
        #     raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Process the WhatsApp message
        result = await whatsapp_processor.process_whatsapp_message(webhook_data)
        
        # Return TwiML response
        twiml_response = await whatsapp_processor.get_webhook_response()
        
        return Response(
            content=twiml_response,
            media_type="application/xml",
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}")
        # Return empty TwiML response even on error
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml",
            status_code=200
        )

@app.get("/api/whatsapp/status")
async def whatsapp_status(request: Request, current_user: User = Depends(get_current_active_user)):
    """
    Get WhatsApp integration status and setup instructions
    """
    try:
        return {
            "whatsapp_number": os.getenv('TWILIO_WHATSAPP_NUMBER'),
            "sandbox_code": "distance-living",
            "status": "active",
            "setup_instructions": [
                "1. Save +14155238886 to your contacts as 'Budget Planner'",
                "2. Send 'join distance-living' to +14155238886 on WhatsApp",
                "3. Wait for confirmation message",
                "4. Forward your bank SMS messages to this number",
                "5. Transactions will be processed automatically!"
            ],
            "supported_banks": ["HDFC", "ICICI", "SBI", "Axis", "Scapia", "Federal"],
            "webhook_url": f"{request.base_url}api/whatsapp/webhook"
        }
    except Exception as e:
        logger.error(f"WhatsApp status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get WhatsApp status")

@app.post("/api/whatsapp/test")
async def test_whatsapp_parsing(
    sms_text: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Test SMS parsing without actually sending WhatsApp message
    """
    try:
        # Test the SMS parsing logic
        result = await whatsapp_processor.parse_sms_content(sms_text, current_user.id)
        
        return {
            "success": result["success"],
            "transaction": result.get("transaction"),
            "error": result.get("error"),
            "parsing_method": result.get("parsing_method")
        }
        
    except Exception as e:
        logger.error(f"WhatsApp test parsing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to test SMS parsing")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
