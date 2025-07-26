import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services.email_templates import EmailTemplates
from services.notification_service import NotificationPreferencesService
from services.user_service import UserService
from services.transaction_service import TransactionService
from services.sms_service import SMSService
from models.user import User
from models.notification import NotificationType, NotificationFrequency

logger = logging.getLogger(__name__)

class EmailScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.email_service = EmailTemplates()
        self.is_running = False
        
    def start(self):
        """Start the email scheduler"""
        if not self.is_running:
            self._setup_jobs()
            self.scheduler.start()
            self.is_running = True
            logger.info("Email scheduler started successfully")
    
    def stop(self):
        """Stop the email scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Email scheduler stopped")
    
    def _setup_jobs(self):
        """Setup all scheduled email jobs"""
        
        # Daily budget checks (runs at 9 AM every day)
        self.scheduler.add_job(
            self.send_budget_alerts,
            CronTrigger(hour=9, minute=0),
            id='daily_budget_alerts',
            replace_existing=True,
            max_instances=1
        )
        
        # Weekly summary emails (runs on Monday at 10 AM)
        self.scheduler.add_job(
            self.send_weekly_summaries,
            CronTrigger(day_of_week=0, hour=10, minute=0),  # Monday = 0
            id='weekly_summaries',
            replace_existing=True,
            max_instances=1
        )
        
        # Monthly summary emails (runs on 1st of each month at 10 AM)
        self.scheduler.add_job(
            self.send_monthly_summaries,
            CronTrigger(day=1, hour=10, minute=0),
            id='monthly_summaries',
            replace_existing=True,
            max_instances=1
        )
        
        # Daily SMS processing summaries (runs at 8 PM every day)
        self.scheduler.add_job(
            self.send_daily_sms_summaries,
            CronTrigger(hour=20, minute=0),
            id='daily_sms_summaries',
            replace_existing=True,
            max_instances=1
        )
        
        # System health check (runs every hour)
        self.scheduler.add_job(
            self.system_health_check,
            IntervalTrigger(hours=1),
            id='system_health_check',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info("Email scheduler jobs configured successfully")
    
    async def send_budget_alerts(self):
        """Send budget alert emails to users who exceed thresholds"""
        try:
            logger.info("Starting daily budget alert check")
            alert_count = 0
            
            # Get all active users
            users = await UserService.get_all_users()
            
            for user_response in users:
                try:
                    # Get full user object
                    user = await UserService.get_user_by_id(user_response.id)
                    if not user:
                        continue
                    
                    # Check if user wants budget alerts
                    should_send, prefs = await NotificationPreferencesService.should_send_notification(
                        user.id, "budget_alert"
                    )
                    
                    if not should_send:
                        continue
                    
                    # Get current month's budget status
                    current_date = datetime.now()
                    budget_status = await self._check_user_budget_status(
                        user.id, current_date.month, current_date.year, prefs.budget_alert_threshold
                    )
                    
                    # Send alerts for categories exceeding threshold
                    for category_alert in budget_status:
                        await self.email_service.send_budget_alert(
                            user=user,
                            category_name=category_alert['category_name'],
                            spent_amount=category_alert['spent_amount'],
                            budget_limit=category_alert['budget_limit'],
                            percentage_spent=category_alert['percentage_spent']
                        )
                        alert_count += 1
                        
                except Exception as e:
                    logger.error(f"Error sending budget alert to user {user_response.id}: {e}")
                    continue
            
            logger.info(f"Daily budget alert check completed. Sent {alert_count} alerts.")
            
        except Exception as e:
            logger.error(f"Error in daily budget alert job: {e}")
    
    async def send_weekly_summaries(self):
        """Send weekly summary emails to subscribed users"""
        try:
            logger.info("Starting weekly summary email send")
            summary_count = 0
            
            users = await UserService.get_all_users()
            current_date = datetime.now()
            
            for user_response in users:
                try:
                    user = await UserService.get_user_by_id(user_response.id)
                    if not user:
                        continue
                    
                    # Check if user wants weekly summaries and if today matches their preferred day
                    should_send, prefs = await NotificationPreferencesService.should_send_notification(
                        user.id, "weekly_summary"
                    )
                    
                    if not should_send:
                        continue
                    
                    # Check if today matches user's preferred day (Monday = 1, Sunday = 7)
                    current_weekday = current_date.isoweekday()  # Monday = 1, Sunday = 7
                    if current_weekday != prefs.weekly_summary_day:
                        continue
                    
                    # Get week's data (last 7 days)
                    start_date = current_date - timedelta(days=7)
                    weekly_data = await self._get_weekly_summary_data(user.id, start_date, current_date)
                    
                    # Send weekly summary (reuse monthly template with week data)
                    await self.email_service.send_monthly_summary(
                        user=user,
                        month=current_date.month,
                        year=current_date.year,
                        total_income=weekly_data['total_income'],
                        total_expenses=weekly_data['total_expenses'],
                        balance=weekly_data['balance'],
                        top_categories=weekly_data['top_categories'],
                        transaction_count=weekly_data['transaction_count']
                    )
                    summary_count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending weekly summary to user {user_response.id}: {e}")
                    continue
            
            logger.info(f"Weekly summary email send completed. Sent {summary_count} summaries.")
            
        except Exception as e:
            logger.error(f"Error in weekly summary job: {e}")
    
    async def send_monthly_summaries(self):
        """Send monthly summary emails to subscribed users"""
        try:
            logger.info("Starting monthly summary email send")
            summary_count = 0
            
            users = await UserService.get_all_users()
            current_date = datetime.now()
            
            # Get previous month data
            if current_date.month == 1:
                prev_month = 12
                prev_year = current_date.year - 1
            else:
                prev_month = current_date.month - 1
                prev_year = current_date.year
            
            for user_response in users:
                try:
                    user = await UserService.get_user_by_id(user_response.id)
                    if not user:
                        continue
                    
                    # Check if user wants monthly summaries and if today matches their preferred day
                    should_send, prefs = await NotificationPreferencesService.should_send_notification(
                        user.id, "monthly_summary"
                    )
                    
                    if not should_send:
                        continue
                    
                    # Check if today matches user's preferred day of month
                    if current_date.day != prefs.monthly_summary_day:
                        continue
                    
                    # Get monthly summary data
                    monthly_data = await TransactionService().get_monthly_summary(prev_month, prev_year, user.id)
                    
                    # Get top categories
                    top_categories = await self._get_top_categories(user.id, prev_month, prev_year)
                    
                    # Get transaction count
                    transactions = await TransactionService().get_transactions(prev_month, prev_year, user.id)
                    transaction_count = len(transactions)
                    
                    await self.email_service.send_monthly_summary(
                        user=user,
                        month=prev_month,
                        year=prev_year,
                        total_income=monthly_data.get('total_income', 0),
                        total_expenses=monthly_data.get('total_expenses', 0),
                        balance=monthly_data.get('balance', 0),
                        top_categories=top_categories,
                        transaction_count=transaction_count
                    )
                    summary_count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending monthly summary to user {user_response.id}: {e}")
                    continue
            
            logger.info(f"Monthly summary email send completed. Sent {summary_count} summaries.")
            
        except Exception as e:
            logger.error(f"Error in monthly summary job: {e}")
    
    async def send_daily_sms_summaries(self):
        """Send daily SMS processing summaries to subscribed users"""
        try:
            logger.info("Starting daily SMS summary email send")
            summary_count = 0
            
            users = await UserService.get_all_users()
            current_date = datetime.now()
            yesterday = current_date - timedelta(days=1)
            
            for user_response in users:
                try:
                    user = await UserService.get_user_by_id(user_response.id)
                    if not user:
                        continue
                    
                    # Check if user wants SMS processing summaries with daily frequency
                    should_send, prefs = await NotificationPreferencesService.should_send_notification(
                        user.id, "sms_processing"
                    )
                    
                    if not should_send or prefs.sms_processing_frequency != NotificationFrequency.DAILY:
                        continue
                    
                    # Get SMS processing stats for yesterday
                    sms_stats = await self._get_sms_processing_stats(user.id, yesterday, current_date)
                    
                    # Only send if there was SMS activity
                    if sms_stats['processed_count'] > 0:
                        await self.email_service.send_sms_processing_summary(
                            user=user,
                            processed_count=sms_stats['processed_count'],
                            successful_count=sms_stats['successful_count'],
                            failed_count=sms_stats['failed_count'],
                            date_range=f"{yesterday.strftime('%d %B %Y')}"
                        )
                        summary_count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending SMS summary to user {user_response.id}: {e}")
                    continue
            
            logger.info(f"Daily SMS summary email send completed. Sent {summary_count} summaries.")
            
        except Exception as e:
            logger.error(f"Error in daily SMS summary job: {e}")
    
    async def system_health_check(self):
        """Perform system health checks and send alerts if needed"""
        try:
            # Log scheduler status
            if self.scheduler.running:
                logger.info("Email scheduler health check: System running normally")
            else:
                logger.warning("Email scheduler health check: Scheduler not running!")
                
        except Exception as e:
            logger.error(f"Error in system health check: {e}")
    
    # Helper methods
    async def _check_user_budget_status(self, user_id: str, month: int, year: int, threshold: float) -> List[Dict]:
        """Check user's budget status and return categories exceeding threshold"""
        try:
            from database import budget_limits_collection
            
            alerts = []
            
            # Get user's budget limits for the month
            async for budget_limit in budget_limits_collection.find({
                "user_id": user_id,
                "month": month,
                "year": year
            }):
                percentage_spent = (budget_limit['spent'] / budget_limit['limit']) if budget_limit['limit'] > 0 else 0
                
                if percentage_spent >= threshold:
                    # Get category name (you might want to implement category lookup)
                    category_name = f"Category {budget_limit['category_id']}"
                    
                    alerts.append({
                        'category_name': category_name,
                        'spent_amount': budget_limit['spent'],
                        'budget_limit': budget_limit['limit'],
                        'percentage_spent': percentage_spent * 100
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking budget status for user {user_id}: {e}")
            return []
    
    async def _get_weekly_summary_data(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get weekly summary data for a user"""
        try:
            # This would typically use your transaction service
            # For now, return mock data structure
            return {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'balance': 0.0,
                'top_categories': [],
                'transaction_count': 0
            }
        except Exception as e:
            logger.error(f"Error getting weekly summary data for user {user_id}: {e}")
            return {
                'total_income': 0.0,
                'total_expenses': 0.0,
                'balance': 0.0,
                'top_categories': [],
                'transaction_count': 0
            }
    
    async def _get_top_categories(self, user_id: str, month: int, year: int) -> List[Dict]:
        """Get top spending categories for a user"""
        try:
            # Implementation would analyze transactions by category
            return []
        except Exception as e:
            logger.error(f"Error getting top categories for user {user_id}: {e}")
            return []
    
    async def _get_sms_processing_stats(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get SMS processing statistics for a user"""
        try:
            from database import sms_collection
            
            # Count SMS processed in date range
            total_sms = await sms_collection.count_documents({
                "user_id": user_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lt": end_date
                }
            })
            
            successful_sms = await sms_collection.count_documents({
                "user_id": user_id,
                "processed": True,
                "timestamp": {
                    "$gte": start_date,
                    "$lt": end_date
                }
            })
            
            failed_sms = total_sms - successful_sms
            
            return {
                'processed_count': total_sms,
                'successful_count': successful_sms,
                'failed_count': failed_sms
            }
            
        except Exception as e:
            logger.error(f"Error getting SMS processing stats for user {user_id}: {e}")
            return {
                'processed_count': 0,
                'successful_count': 0,
                'failed_count': 0
            }

# Global scheduler instance
email_scheduler = EmailScheduler()