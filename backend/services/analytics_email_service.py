# Analytics email service disabled for production deployment
# Users access all analytics insights directly from dashboard
class AnalyticsEmailService:
    def __init__(self):
        self.enabled = False
        print("📊📧 Analytics email service disabled - using dashboard-only mode")
    
    async def process_and_send_spending_alerts(self, *args, **kwargs):
        """Spending alerts disabled - available in analytics dashboard"""
        return {"success": False, "message": "Spending alerts available in analytics dashboard"}
    
    async def send_monthly_financial_health_report(self, *args, **kwargs):
        """Financial health reports disabled - available in analytics dashboard"""
        return {"success": False, "message": "Financial health reports available in analytics dashboard"}
    
    async def send_budget_recommendations(self, *args, **kwargs):
        """Budget recommendations disabled - available in analytics dashboard"""
        return {"success": False, "message": "Budget recommendations available in analytics dashboard"}
    
    async def send_weekly_analytics_digest(self, *args, **kwargs):
        """Weekly digest disabled - available in analytics dashboard"""
        return {"success": False, "message": "Weekly analytics digest available in analytics dashboard"}
    
    async def process_all_analytics_notifications(self, *args, **kwargs):
        """All analytics notifications disabled - available in dashboard"""
        return {"success": False, "message": "All analytics insights available in dashboard"}
    
    async def trigger_immediate_analytics_alerts(self, *args, **kwargs):
        """Analytics alerts disabled - available in dashboard"""
        return {"success": False, "message": "Analytics alerts available in dashboard"}