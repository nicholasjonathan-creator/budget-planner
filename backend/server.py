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
# Email templates removed - no email functionality needed
from services.notification_service import NotificationPreferencesService
# Email scheduler removed - no email functionality needed
# from services.email_scheduler import email_scheduler
email_scheduler = None  # Disabled
from services.production_email_config import production_email_config
from services.monitoring_service import monitoring_service
from services.monitoring_scheduler import monitoring_scheduler
from services.whatsapp_service import whatsapp_processor
from services.phone_verification_service import phone_verification_service
from services.whatsapp_migration_service import whatsapp_migration_service
from services.fallback_phone_service import fallback_phone_service
from services.analytics_service import AnalyticsService
# Phase 2 Service Imports
from services.account_deletion_service import account_deletion_service
from services.phone_management_service import phone_management_service
# Email services removed - no email functionality needed
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
# Email services removed - no email functionality needed
analytics_service = AnalyticsService()

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

# ==================== MONITORING ENDPOINTS ====================

@api_router.get("/monitoring/health")
async def get_system_health():
    """Get system health status"""
    try:
        health_status = await monitoring_service.check_system_health()
        return health_status
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return {"error": str(e)}, 500

@api_router.get("/monitoring/alerts")
async def get_recent_alerts(time_window: int = 60):
    """Get recent alerts from monitoring system"""
    try:
        alerts = await monitoring_service.check_failed_transactions(time_window)
        return {
            "alerts": [
                {
                    "level": alert.level.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "details": alert.details,
                    "user_id": alert.user_id
                } for alert in alerts
            ],
            "time_window_minutes": time_window
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        return {"error": str(e)}, 500

@api_router.post("/monitoring/user-sync-check")
async def check_user_sync_issues(current_user: User = Depends(get_current_active_user)):
    """
    User-triggered sync check - called when user reports missing transactions
    or does force refresh
    """
    try:
        alerts = await monitoring_service.check_transaction_sync_issues(current_user.id)
        
        # Also run a general failed transaction check
        failed_alerts = await monitoring_service.check_failed_transactions(60)
        
        all_alerts = alerts + failed_alerts
        
        return {
            "sync_alerts": [
                {
                    "level": alert.level.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "details": alert.details
                } for alert in all_alerts
            ],
            "user_id": current_user.id,
            "total_alerts": len(all_alerts)
        }
    except Exception as e:
        logger.error(f"Error checking user sync for {current_user.id}: {e}")
        return {"error": str(e)}, 500

@api_router.post("/monitoring/run-cycle")
async def run_monitoring_cycle(time_window: int = 10):
    """
    Run a complete monitoring cycle
    """
    try:
        results = await monitoring_service.run_monitoring_cycle(time_window)
        
        # Store results for historical analysis
        await monitoring_service.store_monitoring_results(results)
        
        return results
    except Exception as e:
        logger.error(f"Error running monitoring cycle: {e}")
        return {"error": str(e)}, 500

@api_router.get("/monitoring/whatsapp-status")
async def get_whatsapp_status():
    """Get WhatsApp service specific status"""
    try:
        whatsapp_health = await monitoring_service._check_whatsapp_health()
        return whatsapp_health
    except Exception as e:
        logger.error(f"Error getting WhatsApp status: {e}")
        return {"error": str(e)}, 500

# ==================== AUTHENTICATION ENDPOINTS ====================

@api_router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        # Create the user
        user = await UserService.create_user(user_data)
        
        # Create access token
        access_token, expires_at = create_user_token(user.id, user.email)
        
        # Email functionality removed - no welcome emails needed
        # Registration completes without email sending
        
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
# Email notification endpoints disabled for production deployment
# Users access all features directly through dashboard

@api_router.get("/notifications/preferences")
async def get_notification_preferences(current_user: User = Depends(get_current_active_user)):
    """Get user notification preferences (UI settings only - emails disabled)"""
    try:
        # Return minimal preferences for UI state management
        return {
            "user_id": current_user.id,
            "email_enabled": False,
            "email_notifications_disabled": True,
            "message": "Email notifications disabled - all insights available in dashboard"
        }
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/notifications/preferences")
async def update_notification_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Update notification preferences (UI only - emails disabled)"""
    try:
        # Just return success for UI compatibility
        return {
            "success": True,
            "message": "Settings saved (email notifications disabled)",
            "email_enabled": False
        }
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/test-email")
async def send_test_email(current_user: User = Depends(get_current_active_user)):
    """Test email endpoint (disabled for production)"""
    return {
        "success": False,
        "message": "Email service disabled for production - all insights available in dashboard"
    }

@api_router.get("/notifications/logs")
async def get_notification_logs(current_user: User = Depends(get_current_active_user)):
    """Get notification logs (disabled for production)"""
    return {
        "logs": [],
        "message": "Email notifications disabled - no logs to display"
    }

# ==================== PRODUCTION EMAIL ENDPOINTS ====================

@api_router.get("/notifications/production/status")
async def get_production_email_status(admin_user: User = Depends(get_admin_user)):
    """Get production email system status (admin only)"""
    try:
        config_status = await production_email_config.verify_sender_configuration()
        checklist = await production_email_config.get_production_checklist()
        
        scheduler_status = {
            'running': False,  # Email scheduler disabled
            'jobs': 0  # No jobs when disabled
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
    """Start the email scheduler (admin only) - DISABLED"""
    try:
        return {"message": "Email scheduler disabled - no email functionality needed", "status": "disabled"}
    except Exception as e:
        logger.error(f"Error starting email scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/production/stop-scheduler")
async def stop_email_scheduler(admin_user: User = Depends(get_admin_user)):
    """Stop the email scheduler (admin only) - DISABLED"""
    try:
        return {"message": "Email scheduler disabled - no email functionality needed", "status": "disabled"}
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
    """Manually trigger budget alerts for testing (admin only) - DISABLED"""
    try:
        return {"message": "Budget alerts disabled - no email functionality needed"}
    except Exception as e:
        logger.error(f"Error triggering budget alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/notifications/production/trigger-monthly-summaries")
async def trigger_monthly_summaries(admin_user: User = Depends(get_admin_user)):
    """Manually trigger monthly summaries for testing (admin only) - DISABLED"""
    try:
        return {"message": "Monthly summaries disabled - no email functionality needed"}
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

# Analytics email endpoints disabled for production deployment
# All analytics insights available directly in dashboard

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
async def get_sms_stats(current_user: User = Depends(get_current_active_user)):
    """Get SMS processing statistics for current user"""
    try:
        return await sms_service.get_user_sms_stats(current_user.id)
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
    """Initialize services on startup"""
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Email scheduler removed - no email functionality needed
        logger.info("Email scheduler disabled - no email functionality")
            
        # Start monitoring scheduler
        await monitoring_scheduler.start()
        logger.info("Monitoring scheduler started")
        
        logger.info("Budget Planner API started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        # Email scheduler removed - no email functionality needed
        logger.info("Email scheduler disabled - no email functionality")
        
        # Stop monitoring scheduler
        await monitoring_scheduler.stop()
        logger.info("Monitoring scheduler stopped")
        
        logger.info("Budget Planner API shutting down")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        raise

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

# Clear all data (admin only)
@app.delete("/api/admin/clear-all-data")
async def clear_all_data(admin_user: User = Depends(get_admin_user)):
    """Clear all data from the database (admin only)"""
    try:
        # Clear all collections
        await db.transactions.delete_many({})
        await db.budgets.delete_many({})
        await db.sms_messages.delete_many({})
        await db.categories.delete_many({})
        await db.notifications.delete_many({})
        await db.analytics_cache.delete_many({})
        
        logger.info(f"All data cleared by admin: {admin_user.email}")
        
        return {"message": "All data cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing all data: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear all data")

# WhatsApp Migration Admin Endpoints
@app.post("/api/admin/whatsapp/notify-existing-users")
async def notify_existing_users_whatsapp(admin_user: User = Depends(get_admin_user)):
    """Send WhatsApp feature announcement to all existing users without phone verification"""
    try:
        result = await whatsapp_migration_service.notify_all_existing_users()
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "stats": {
                    "users_notified": result["users_notified"],
                    "emails_sent": result["emails_sent"],
                    "errors": result["errors"]
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Migration notification failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in WhatsApp migration notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to notify existing users")

@app.get("/api/admin/whatsapp/migration-stats")
async def get_whatsapp_migration_stats(admin_user: User = Depends(get_admin_user)):
    """Get WhatsApp migration statistics"""
    try:
        stats = await whatsapp_migration_service.get_migration_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting migration stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get migration statistics")

@app.get("/api/admin/whatsapp/unverified-users")
async def get_unverified_users(admin_user: User = Depends(get_admin_user)):
    """Get list of users who haven't verified their phone numbers"""
    try:
        users = await whatsapp_migration_service.get_users_without_phone_verification()
        
        # Return only safe user info for admin view
        safe_users = []
        for user in users:
            safe_users.append({
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "created_at": user.get("created_at"),
                "phone_verified": user.get("phone_verified", False),
                "has_phone": bool(user.get("phone_number"))
            })
        
        return {
            "total_unverified": len(safe_users),
            "users": safe_users
        }
        
    except Exception as e:
        logger.error(f"Error getting unverified users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get unverified users")

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

# Phone Verification Endpoints
@app.post("/api/phone/send-verification")
async def send_phone_verification(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send OTP verification code to user's phone via WhatsApp (with fallback)
    """
    try:
        phone_number = request.get("phone_number")
        if not phone_number:
            raise HTTPException(status_code=400, detail="Phone number is required")
        
        # First, try the main Twilio service
        result = await phone_verification_service.send_verification_otp(
            user_id=str(current_user.id),
            phone_number=phone_number
        )
        
        # If Twilio fails, use fallback service
        if not result["success"] and "Failed to send verification code" in result.get("error", ""):
            logger.warning(f"Twilio failed for user {current_user.id}, using fallback service")
            result = await fallback_phone_service.send_fallback_verification_otp(
                user_id=str(current_user.id),
                phone_number=phone_number
            )
        
        if result["success"]:
            response = {
                "success": True,
                "message": result["message"],
                "phone_number": result["phone_number"],
                "expires_in_minutes": result["expires_in_minutes"]
            }
            
            # Add demo information if in fallback mode
            if result.get("fallback_mode"):
                response["demo_mode"] = True
                response["demo_note"] = "Demo Mode: Verification code shown above for testing"
                
            return response
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phone verification send error: {e}")
        # Final fallback
        try:
            result = await fallback_phone_service.send_fallback_verification_otp(
                user_id=str(current_user.id),
                phone_number=phone_number
            )
            if result["success"]:
                return {
                    "success": True,
                    "message": result["message"],
                    "phone_number": result["phone_number"],
                    "expires_in_minutes": result["expires_in_minutes"],
                    "demo_mode": True,
                    "demo_note": "Demo Mode: Verification code shown above for testing"
                }
        except:
            pass
        raise HTTPException(status_code=500, detail="Failed to send verification code")

@app.post("/api/phone/verify-otp")
async def verify_phone_otp(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify OTP code entered by user (supports both Twilio and fallback)
    """
    try:
        otp = request.get("otp")
        if not otp:
            raise HTTPException(status_code=400, detail="OTP code is required")
        
        # Try main verification service first
        result = await phone_verification_service.verify_otp(
            user_id=str(current_user.id),
            otp=otp
        )
        
        # If main service fails, try fallback
        if not result["success"]:
            result = await fallback_phone_service.verify_fallback_otp(
                user_id=str(current_user.id),
                otp=otp
            )
        
        if result["success"]:
            response = {
                "success": True,
                "message": result["message"],
                "phone_number": result["phone_number"]
            }
            
            # Add demo information if in fallback mode
            if result.get("fallback_mode"):
                response["demo_mode"] = True
                
            return response
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phone verification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify phone number")

@app.post("/api/phone/resend-otp")
async def resend_phone_otp(current_user: User = Depends(get_current_active_user)):
    """
    Resend OTP verification code
    """
    try:
        result = await phone_verification_service.resend_otp(str(current_user.id))
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phone OTP resend error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resend verification code")

@app.delete("/api/phone/unlink")
async def unlink_phone_number(current_user: User = Depends(get_current_active_user)):
    """
    Unlink phone number from user account
    """
    try:
        result = await phone_verification_service.remove_phone_verification(str(current_user.id))
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phone unlink error: {e}")
        raise HTTPException(status_code=500, detail="Failed to unlink phone number")

@app.get("/api/phone/status")
async def get_phone_verification_status(current_user: User = Depends(get_current_active_user)):
    """
    Get current phone verification status for user
    """
    try:
        from bson import ObjectId
        # Get user data including phone verification status
        user_data = await db.users.find_one({"_id": ObjectId(current_user.id)})
        
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "phone_number": user_data.get("phone_number"),
            "phone_verified": user_data.get("phone_verified", False),
            "phone_verified_at": user_data.get("phone_verified_at"),
            "can_receive_sms": user_data.get("phone_verified", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Phone status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get phone verification status")

# Account Consolidation Endpoints
@app.get("/api/account/consolidation/preview")
async def get_consolidation_preview(
    phone_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Preview what data would be consolidated for a phone number
    """
    try:
        from services.account_consolidation_service import account_consolidation_service
        
        preview = await account_consolidation_service.get_consolidation_preview(
            phone_number, current_user.id
        )
        
        return preview
        
    except Exception as e:
        logger.error(f"Consolidation preview error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get consolidation preview")

@app.post("/api/account/consolidation/transfer-phone")
async def transfer_phone_number(
    phone_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Transfer phone number association to current user
    """
    try:
        from services.account_consolidation_service import account_consolidation_service
        
        result = await account_consolidation_service.transfer_phone_number_association(
            phone_number, current_user.id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Phone transfer error: {e}")
        raise HTTPException(status_code=500, detail="Failed to transfer phone number")

@app.post("/api/account/consolidation/full-merge")
async def full_account_consolidation(
    phone_number: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform full account consolidation (merge all data)
    """
    try:
        from services.account_consolidation_service import account_consolidation_service
        
        # First find the source user
        source_user = await account_consolidation_service.find_user_by_phone_number(phone_number)
        if not source_user:
            return {"success": False, "error": "No user found with this phone number"}
        
        source_user_id = source_user["id"]
        
        # Don't merge if it's the same user
        if source_user_id == current_user.id:
            return {"success": False, "error": "Cannot merge account with itself"}
        
        # Perform full consolidation
        result = await account_consolidation_service.consolidate_user_data(
            source_user_id, current_user.id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Full consolidation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform full consolidation")

# Phase 2: Account Deletion Endpoints
@app.get("/api/account/deletion/preview")
async def get_account_deletion_preview(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get preview of account data before deletion
    """
    try:
        data_summary = await account_deletion_service.get_account_data_summary(current_user.id)
        
        return data_summary
        
    except Exception as e:
        logger.error(f"Account deletion preview error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get account deletion preview")

@app.post("/api/account/deletion/soft-delete")
async def soft_delete_account(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft delete account (deactivate but preserve data)
    """
    try:
        reason = request.get("reason", "User requested account deactivation")
        
        result = await account_deletion_service.soft_delete_account(current_user.id, reason)
        
        return result
        
    except Exception as e:
        logger.error(f"Soft delete account error: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate account")

@app.post("/api/account/deletion/hard-delete")
async def hard_delete_account(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Hard delete account (complete removal of all data)
    """
    try:
        reason = request.get("reason", "User requested complete account deletion")
        confirmation = request.get("confirmation")
        
        if confirmation != "PERMANENTLY DELETE MY ACCOUNT":
            raise HTTPException(
                status_code=400, 
                detail="Confirmation text required: 'PERMANENTLY DELETE MY ACCOUNT'"
            )
        
        result = await account_deletion_service.hard_delete_account(current_user.id, reason)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hard delete account error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete account")

@app.get("/api/account/export-data")
async def export_account_data(
    current_user: User = Depends(get_current_active_user)
):
    """
    Export all user data for GDPR compliance
    """
    try:
        export_result = await account_deletion_service.export_user_data(current_user.id)
        
        return export_result
        
    except Exception as e:
        logger.error(f"Export account data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to export account data")

# Phase 2: Phone Number Management Endpoints
@app.get("/api/phone/status")
async def get_phone_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current phone number status
    """
    try:
        status = await phone_management_service.get_phone_status(current_user.id)
        
        return status
        
    except Exception as e:
        logger.error(f"Get phone status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get phone status")

@app.post("/api/phone/initiate-change")
async def initiate_phone_change(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Initiate phone number change
    """
    try:
        new_phone_number = request.get("new_phone_number")
        if not new_phone_number:
            raise HTTPException(status_code=400, detail="New phone number is required")
        
        result = await phone_management_service.initiate_phone_change(
            current_user.id, new_phone_number
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Initiate phone change error: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate phone change")

@app.post("/api/phone/complete-change")
async def complete_phone_change(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Complete phone number change with verification
    """
    try:
        new_phone_number = request.get("new_phone_number")
        verification_code = request.get("verification_code")
        
        if not new_phone_number or not verification_code:
            raise HTTPException(
                status_code=400, 
                detail="New phone number and verification code are required"
            )
        
        result = await phone_management_service.complete_phone_change(
            current_user.id, new_phone_number, verification_code
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Complete phone change error: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete phone change")

@app.delete("/api/phone/remove")
async def remove_phone_number(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove phone number from account
    """
    try:
        reason = request.get("reason", "User requested phone number removal")
        
        result = await phone_management_service.remove_phone_number(current_user.id, reason)
        
        return result
        
    except Exception as e:
        logger.error(f"Remove phone number error: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove phone number")

@app.get("/api/phone/history")
async def get_phone_history(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get phone number change history
    """
    try:
        history = await phone_management_service.get_phone_history(current_user.id)
        
        return history
        
    except Exception as e:
        logger.error(f"Get phone history error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get phone history")

@app.post("/api/phone/cancel-change")
async def cancel_phone_change(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel pending phone number change
    """
    try:
        new_phone_number = request.get("new_phone_number")
        if not new_phone_number:
            raise HTTPException(status_code=400, detail="New phone number is required")
        
        result = await phone_management_service.cancel_phone_change(
            current_user.id, new_phone_number
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel phone change error: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel phone change")

# SMS Management Endpoints
@app.get("/api/sms/list")
async def get_user_sms_list(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's SMS messages with pagination
    """
    try:
        skip = (page - 1) * limit
        
        # Get SMS messages for the current user
        cursor = db.sms_transactions.find(
            {"user_id": current_user.id}
        ).sort("timestamp", -1).skip(skip).limit(limit)
        
        sms_list = []
        async for sms_doc in cursor:
            sms_list.append({
                "id": str(sms_doc["_id"]),
                "phone_number": sms_doc.get("phone_number"),
                "message": sms_doc.get("message"),
                "timestamp": sms_doc.get("timestamp"),
                "processed": sms_doc.get("processed", False),
                "transaction_id": sms_doc.get("transaction_id"),
                "sms_hash": sms_doc.get("sms_hash")
            })
        
        # Get total count
        total_count = await db.sms_transactions.count_documents({"user_id": current_user.id})
        
        return {
            "sms_list": sms_list,
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Get SMS list error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get SMS list")

@app.delete("/api/sms/{sms_id}")
async def delete_sms(
    sms_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a specific SMS message and its associated transaction
    """
    try:
        from bson import ObjectId
        
        # Get SMS record
        sms_doc = await db.sms_transactions.find_one({
            "_id": ObjectId(sms_id),
            "user_id": current_user.id
        })
        
        if not sms_doc:
            raise HTTPException(status_code=404, detail="SMS not found")
        
        # Delete associated transaction if exists
        transaction_id = sms_doc.get("transaction_id")
        if transaction_id:
            await db.transactions.delete_one({
                "_id": ObjectId(transaction_id),
                "user_id": current_user.id
            })
        
        # Delete SMS record
        await db.sms_transactions.delete_one({
            "_id": ObjectId(sms_id),
            "user_id": current_user.id
        })
        
        return {"success": True, "message": "SMS and associated transaction deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete SMS error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete SMS")

@app.post("/api/sms/find-duplicates")
async def find_duplicate_sms(
    current_user: User = Depends(get_current_active_user)
):
    """
    Find duplicate SMS messages for the current user
    """
    try:
        # Aggregate to find duplicates
        pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {
                "_id": "$sms_hash",
                "count": {"$sum": 1},
                "sms_ids": {"$push": "$_id"},
                "messages": {"$push": "$message"},
                "timestamps": {"$push": "$timestamp"}
            }},
            {"$match": {"count": {"$gt": 1}}}
        ]
        
        duplicates = []
        async for doc in db.sms_transactions.aggregate(pipeline):
            duplicates.append({
                "sms_hash": doc["_id"],
                "count": doc["count"],
                "sms_ids": [str(sms_id) for sms_id in doc["sms_ids"]],
                "message": doc["messages"][0],  # First message (they should be identical)
                "timestamps": doc["timestamps"]
            })
        
        return {
            "duplicate_groups": duplicates,
            "total_groups": len(duplicates)
        }
        
    except Exception as e:
        logger.error(f"Find duplicates error: {e}")
        raise HTTPException(status_code=500, detail="Failed to find duplicate SMS")

@app.post("/api/sms/resolve-duplicates")
async def resolve_duplicate_sms(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Resolve duplicate SMS messages by keeping one and deleting others
    """
    try:
        from bson import ObjectId
        
        sms_hash = request.get("sms_hash")
        keep_sms_id = request.get("keep_sms_id")
        
        if not sms_hash or not keep_sms_id:
            raise HTTPException(status_code=400, detail="SMS hash and keep_sms_id are required")
        
        # Get all SMS with this hash
        cursor = db.sms_transactions.find({
            "sms_hash": sms_hash,
            "user_id": current_user.id
        })
        
        sms_to_delete = []
        async for sms_doc in cursor:
            sms_id = str(sms_doc["_id"])
            if sms_id != keep_sms_id:
                sms_to_delete.append({
                    "sms_id": sms_id,
                    "transaction_id": sms_doc.get("transaction_id")
                })
        
        # Delete duplicate SMS and their transactions
        deleted_count = 0
        for sms_info in sms_to_delete:
            # Delete transaction if exists
            if sms_info["transaction_id"]:
                await db.transactions.delete_one({
                    "_id": ObjectId(sms_info["transaction_id"]),
                    "user_id": current_user.id
                })
            
            # Delete SMS
            result = await db.sms_transactions.delete_one({
                "_id": ObjectId(sms_info["sms_id"]),
                "user_id": current_user.id
            })
            
            if result.deleted_count > 0:
                deleted_count += 1
        
        return {
            "success": True,
            "message": f"Deleted {deleted_count} duplicate SMS messages",
            "kept_sms_id": keep_sms_id,
            "deleted_count": deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resolve duplicates error: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve duplicate SMS")

# Password Reset Endpoints
@app.post("/api/auth/forgot-password")
async def forgot_password(request: dict = Body(...)):
    """
    Initiate password reset process
    """
    try:
        from services.password_reset_service import password_reset_service
        
        email = request.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        result = await password_reset_service.initiate_password_reset(email)
        
        return result
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate password reset")

@app.post("/api/auth/validate-reset-token")
async def validate_reset_token(request: dict = Body(...)):
    """
    Validate password reset token
    """
    try:
        from services.password_reset_service import password_reset_service
        
        token = request.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Token is required")
        
        result = await password_reset_service.validate_reset_token(token)
        
        return result
        
    except Exception as e:
        logger.error(f"Validate reset token error: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate reset token")

@app.post("/api/auth/reset-password")
async def reset_password(request: dict = Body(...)):
    """
    Reset password using token
    """
    try:
        from services.password_reset_service import password_reset_service
        
        token = request.get("token")
        new_password = request.get("new_password")
        
        if not token or not new_password:
            raise HTTPException(status_code=400, detail="Token and new password are required")
        
        result = await password_reset_service.reset_password(token, new_password)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")

@app.post("/api/auth/change-password")
async def change_password(
    request: dict = Body(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Change password for authenticated user
    """
    try:
        from services.auth import verify_password, get_password_hash
        from bson import ObjectId
        
        current_password = request.get("current_password")
        new_password = request.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Current and new passwords are required")
        
        # Verify current password
        if not verify_password(current_password, current_user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        password_hash = get_password_hash(new_password)
        await db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {
                "password_hash": password_hash,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {"success": True, "message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
