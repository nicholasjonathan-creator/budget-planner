# Email service disabled for production deployment
# Users will access insights directly from dashboard
class EmailService:
    def __init__(self):
        self.enabled = False
        print("📧 Email service disabled - using dashboard-only mode")
    
    def _get_base_template(self, title: str, content: str, username: str = "User") -> str:
        """Base email template - disabled but returns empty string to prevent errors"""
        return ""
    
    async def send_email(self, *args, **kwargs):
        """Email sending disabled - users check dashboard for insights"""
        return {"success": False, "message": "Email service disabled - check dashboard for insights"}
    
    async def send_welcome_email(self, *args, **kwargs):
        """Welcome emails disabled"""
        return {"success": False, "message": "Welcome email disabled"}
    
    async def send_budget_alert_email(self, *args, **kwargs):
        """Budget alert emails disabled"""
        return {"success": False, "message": "Budget alerts available in dashboard"}
    
    async def send_monthly_summary_email(self, *args, **kwargs):
        """Monthly summary emails disabled"""
        return {"success": False, "message": "Monthly summaries available in dashboard"}
    
    async def send_transaction_confirmation_email(self, *args, **kwargs):
        """Transaction confirmation emails disabled"""
        return {"success": False, "message": "Transaction confirmations available in dashboard"}