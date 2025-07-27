# Email service disabled for production deployment - using dashboard-only mode
# No email configuration needed - all insights available in dashboard
class ProductionEmailConfig:
    def __init__(self):
        self.enabled = False
        print("📧 Production email service disabled - dashboard-only mode")
    
    def get_configuration_status(self):
        """Return disabled status for email configuration"""
        return {
            "enabled": False,
            "message": "Email service disabled - all insights available in dashboard"
        }
    
    def send_configuration_email(self, *args, **kwargs):
        """Email sending disabled"""
        return {"success": False, "message": "Email service disabled"}
    
    def validate_email_setup(self, *args, **kwargs):
        """Email validation disabled"""  
        return {"valid": False, "message": "Email service disabled"}