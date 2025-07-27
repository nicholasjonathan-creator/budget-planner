from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from services.analytics_service import AnalyticsService
from services.email_templates import EmailTemplates
from services.notification_service import NotificationPreferencesService
from models.user import User
from models.analytics import SpendingAlert, FinancialHealthScore, BudgetRecommendation, AlertSeverity
from database import db

logger = logging.getLogger(__name__)

class AnalyticsEmailService:
    """Service for handling analytics-related email notifications"""
    
    def __init__(self):
        self.analytics_service = AnalyticsService()
        self.email_templates = EmailTemplates()
        self.notification_service = NotificationPreferencesService()
    
    async def process_and_send_spending_alerts(self, user_id: str) -> Dict[str, Any]:
        """Process spending anomalies and send email alerts"""
        try:
            # Get user preferences
            preferences = await self.notification_service.get_user_preferences(user_id)
            if not preferences or not preferences.spending_alerts_enabled:
                return {"success": False, "reason": "Spending alerts disabled"}
            
            # Get user info
            user_doc = await db.users.find_one({"_id": user_id})
            if not user_doc:
                return {"success": False, "reason": "User not found"}
            
            user = User(**{**user_doc, "id": str(user_doc["_id"])})
            
            # Get spending alerts
            alerts = await self.analytics_service.detect_spending_anomalies(user_id)
            
            # Filter alerts by severity threshold
            severity_levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            min_severity = severity_levels.get(preferences.spending_alert_severity_threshold, 1)
            
            filtered_alerts = []
            for alert in alerts:
                alert_severity_level = severity_levels.get(alert.severity, 1)
                if alert_severity_level >= min_severity and not alert.is_read:
                    filtered_alerts.append(alert)
            
            # Send emails for each alert
            sent_count = 0
            for alert in filtered_alerts:
                try:
                    success = await self.email_templates.send_spending_alert_email(user, alert)
                    if success:
                        sent_count += 1
                        # Mark alert as notified
                        await db.spending_alerts.update_one(
                            {"_id": alert.id},
                            {"$set": {"email_sent": True, "email_sent_at": datetime.utcnow()}}
                        )
                except Exception as e:
                    logger.error(f"Failed to send spending alert email: {e}")
            
            return {
                "success": True,
                "alerts_found": len(alerts),
                "alerts_sent": sent_count,
                "filtered_out": len(alerts) - len(filtered_alerts)
            }
            
        except Exception as e:
            logger.error(f"Error processing spending alerts for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_monthly_financial_health_report(self, user_id: str) -> Dict[str, Any]:
        """Generate and send monthly financial health report"""
        try:
            # Get user preferences
            preferences = await self.notification_service.get_user_preferences(user_id)
            if not preferences or not preferences.financial_health_reports_enabled:
                return {"success": False, "reason": "Financial health reports disabled"}
            
            # Get user info
            user_doc = await db.users.find_one({"_id": user_id})
            if not user_doc:
                return {"success": False, "reason": "User not found"}
            
            user = User(**{**user_doc, "id": str(user_doc["_id"])})
            
            # Calculate current financial health score
            current_health = await self.analytics_service.calculate_financial_health_score(user_id)
            
            # Try to get previous month's score for comparison
            previous_score = None
            try:
                # Look for cached health score from previous month
                last_month = datetime.now() - timedelta(days=30)
                previous_health_doc = await db.analytics_cache.find_one({
                    "user_id": user_id,
                    "type": "financial_health",
                    "generated_at": {"$gte": last_month, "$lt": datetime.now() - timedelta(days=20)}
                })
                if previous_health_doc:
                    previous_score = previous_health_doc.get("score")
            except Exception as e:
                logger.warning(f"Could not get previous health score: {e}")
            
            # Send the email
            success = await self.email_templates.send_financial_health_report(
                user, current_health, previous_score
            )
            
            # Cache current score for future comparisons
            if success:
                await db.analytics_cache.insert_one({
                    "user_id": user_id,
                    "type": "financial_health",
                    "score": current_health.score,
                    "grade": current_health.grade,
                    "data": current_health.dict(),
                    "generated_at": datetime.utcnow()
                })
            
            return {
                "success": success,
                "current_score": current_health.score,
                "previous_score": previous_score,
                "improvement": current_health.score - previous_score if previous_score else None
            }
            
        except Exception as e:
            logger.error(f"Error sending financial health report for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_budget_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Generate and send AI-powered budget recommendations"""
        try:
            # Get user preferences
            preferences = await self.notification_service.get_user_preferences(user_id)
            if not preferences or not preferences.budget_recommendations_enabled:
                return {"success": False, "reason": "Budget recommendations disabled"}
            
            # Get user info
            user_doc = await db.users.find_one({"_id": user_id})
            if not user_doc:
                return {"success": False, "reason": "User not found"}
            
            user = User(**{**user_doc, "id": str(user_doc["_id"])})
            
            # Generate recommendations
            recommendations = await self.analytics_service.generate_budget_recommendations(user_id)
            
            if not recommendations:
                return {"success": False, "reason": "No recommendations generated"}
            
            # Send the email
            success = await self.email_templates.send_budget_recommendations_email(
                user, recommendations
            )
            
            return {
                "success": success,
                "recommendations_count": len(recommendations),
                "total_potential_savings": sum(rec.potential_savings for rec in recommendations),
                "high_confidence_count": len([r for r in recommendations if r.confidence_score > 0.8])
            }
            
        except Exception as e:
            logger.error(f"Error sending budget recommendations for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_weekly_analytics_digest(self, user_id: str) -> Dict[str, Any]:
        """Generate and send weekly analytics digest"""
        try:
            # Get user preferences  
            preferences = await self.notification_service.get_user_preferences(user_id)
            if not preferences or not preferences.weekly_analytics_digest_enabled:
                return {"success": False, "reason": "Weekly analytics digest disabled"}
            
            # Get user info
            user_doc = await db.users.find_one({"_id": user_id})
            if not user_doc:
                return {"success": False, "reason": "User not found"}
            
            user = User(**{**user_doc, "id": str(user_doc["_id"])})
            
            # Calculate week date range
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())  # Monday
            week_end = week_start + timedelta(days=6)  # Sunday
            
            # Get week's transactions
            transactions = await self.analytics_service._get_transactions_between_dates(
                user_id, week_start, week_end
            )
            
            # Calculate summary statistics
            income_transactions = [t for t in transactions if t.type.value == "income"]
            expense_transactions = [t for t in transactions if t.type.value == "expense"]
            
            total_income = sum(t.amount for t in income_transactions)
            total_spent = sum(t.amount for t in expense_transactions)
            
            # Get category breakdown
            category_totals = {}
            for t in expense_transactions:
                if t.category_id not in category_totals:
                    category_totals[t.category_id] = 0
                category_totals[t.category_id] += t.amount
            
            # Sort categories by spending
            top_categories = [
                {"id": cat_id, "name": f"Category {cat_id}", "amount": amount}
                for cat_id, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            ]
            
            # Get alerts count for the week
            alerts = await self.analytics_service.detect_spending_anomalies(user_id)
            week_alerts = [
                a for a in alerts 
                if a.date_detected >= week_start and a.date_detected <= week_end
            ]
            
            # Prepare summary data
            week_summary = {
                "total_income": total_income,
                "total_spent": total_spent,
                "transaction_count": len(transactions),
                "top_categories": top_categories,
                "alerts_count": len(week_alerts),
                "week_range": f"{week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}"
            }
            
            # Send the email
            success = await self.email_templates.send_weekly_analytics_digest(user, week_summary)
            
            return {
                "success": success,
                "total_spent": total_spent,
                "total_income": total_income,
                "transaction_count": len(transactions),
                "alerts_count": len(week_alerts)
            }
            
        except Exception as e:
            logger.error(f"Error sending weekly analytics digest for user {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def process_all_analytics_notifications(self, user_id: str) -> Dict[str, Any]:
        """Process all analytics notifications for a user"""
        results = {}
        
        # Process spending alerts
        results["spending_alerts"] = await self.process_and_send_spending_alerts(user_id)
        
        # Check if it's time for financial health report (monthly)
        today = datetime.now()
        if today.day == 1:  # First day of month
            results["financial_health_report"] = await self.send_monthly_financial_health_report(user_id)
        
        # Check if it's time for budget recommendations (bi-weekly)
        if today.day in [1, 15]:  # 1st and 15th of month
            results["budget_recommendations"] = await self.send_budget_recommendations(user_id)
        
        # Check if it's Monday for weekly digest
        if today.weekday() == 0:  # Monday
            results["weekly_digest"] = await self.send_weekly_analytics_digest(user_id)
        
        return results
    
    async def trigger_immediate_analytics_alerts(self, user_id: str) -> Dict[str, Any]:
        """Trigger immediate analytics alerts for testing or manual triggers"""
        results = {}
        
        results["spending_alerts"] = await self.process_and_send_spending_alerts(user_id)
        results["financial_health_report"] = await self.send_monthly_financial_health_report(user_id)
        results["budget_recommendations"] = await self.send_budget_recommendations(user_id)
        results["weekly_digest"] = await self.send_weekly_analytics_digest(user_id)
        
        return results