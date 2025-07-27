# Email scheduler disabled for production deployment  
# All insights available in dashboard - no scheduled emails needed
class EmailScheduler:
    def __init__(self):
        self.enabled = False
        print("📅📧 Email scheduler disabled - dashboard-only mode")
    
    async def start(self):
        """Email scheduler disabled - no scheduled emails"""
        print("📅 Email scheduler start requested - disabled for dashboard-only mode")
        
    async def stop(self):
        """Email scheduler disabled - no scheduled emails"""
        print("📅 Email scheduler stop requested - disabled for dashboard-only mode")

# Global scheduler instance
email_scheduler = EmailScheduler()