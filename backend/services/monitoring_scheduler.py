"""
Scheduled Monitoring Service
Runs monitoring checks every 10 minutes and sends alerts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import os
from typing import Dict, Any

from services.monitoring_service import monitoring_service
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class MonitoringScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.email_service = EmailService()
        self.is_running = False
        
    async def start(self):
        """Start the monitoring scheduler"""
        if not self.is_running:
            # Schedule monitoring cycle every 10 minutes
            self.scheduler.add_job(
                self.run_monitoring_cycle,
                trigger=IntervalTrigger(minutes=10),
                id='monitoring_cycle',
                replace_existing=True
            )
            
            # Schedule health check every 5 minutes
            self.scheduler.add_job(
                self.run_health_check,
                trigger=IntervalTrigger(minutes=5),
                id='health_check',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Monitoring scheduler started")
    
    async def stop(self):
        """Stop the monitoring scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Monitoring scheduler stopped")
    
    async def run_monitoring_cycle(self):
        """Run the monitoring cycle and send alerts if needed"""
        try:
            logger.info("Starting scheduled monitoring cycle")
            
            # Run monitoring cycle
            results = await monitoring_service.run_monitoring_cycle(time_window_minutes=10)
            
            # Store results
            await monitoring_service.store_monitoring_results(results)
            
            # Send alerts if there are critical or error alerts
            if results['summary']['critical_alerts'] > 0 or results['summary']['error_alerts'] > 0:
                await self.send_monitoring_alerts(results)
            
            logger.info(f"Monitoring cycle completed. Alerts: {results['summary']['total_alerts']}")
            
        except Exception as e:
            logger.error(f"Error in scheduled monitoring cycle: {e}")
    
    async def run_health_check(self):
        """Run health check and log status"""
        try:
            health_status = await monitoring_service.check_system_health()
            
            if health_status['status'] != 'healthy':
                logger.warning(f"System health check: {health_status['status']} - Issues: {health_status['issues']}")
                
                # Send alert for unhealthy system
                if health_status['status'] == 'unhealthy':
                    await self.send_health_alert(health_status)
            else:
                logger.info("System health check: healthy")
                
        except Exception as e:
            logger.error(f"Error in health check: {e}")
    
    async def send_monitoring_alerts(self, results: Dict[str, Any]):
        """Send email alerts for monitoring issues"""
        try:
            # Get admin email from environment
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            
            # Prepare alert email
            critical_alerts = [a for a in results['alerts'] if a['level'] == 'critical']
            error_alerts = [a for a in results['alerts'] if a['level'] == 'error']
            
            subject = f"🚨 Budget Planner Monitoring Alert - {len(critical_alerts)} Critical, {len(error_alerts)} Errors"
            
            email_body = f"""
            <h2>Budget Planner Monitoring Alert</h2>
            <p><strong>Timestamp:</strong> {results['timestamp']}</p>
            <p><strong>System Status:</strong> {results['health_status'].get('status', 'unknown')}</p>
            
            <h3>Alert Summary</h3>
            <ul>
                <li>Critical Alerts: {results['summary']['critical_alerts']}</li>
                <li>Error Alerts: {results['summary']['error_alerts']}</li>
                <li>Warning Alerts: {results['summary']['warning_alerts']}</li>
                <li>Total Alerts: {results['summary']['total_alerts']}</li>
            </ul>
            
            <h3>Critical Alerts</h3>
            """
            
            for alert in critical_alerts:
                email_body += f"""
                <div style="border: 2px solid red; padding: 10px; margin: 10px 0; background: #ffebee;">
                    <strong>🚨 CRITICAL:</strong> {alert['message']}<br>
                    <strong>Time:</strong> {alert['timestamp']}<br>
                    <strong>Details:</strong> {alert['details']}<br>
                </div>
                """
            
            email_body += "<h3>Error Alerts</h3>"
            
            for alert in error_alerts:
                email_body += f"""
                <div style="border: 2px solid orange; padding: 10px; margin: 10px 0; background: #fff3e0;">
                    <strong>❌ ERROR:</strong> {alert['message']}<br>
                    <strong>Time:</strong> {alert['timestamp']}<br>
                    <strong>Details:</strong> {alert['details']}<br>
                </div>
                """
            
            email_body += f"""
            <h3>System Health</h3>
            <p><strong>Status:</strong> {results['health_status'].get('status', 'unknown')}</p>
            <p><strong>Metrics:</strong></p>
            <ul>
            """
            
            for metric, value in results['health_status'].get('metrics', {}).items():
                email_body += f"<li>{metric}: {value}</li>"
            
            email_body += "</ul>"
            
            if results['health_status'].get('issues'):
                email_body += "<p><strong>Issues:</strong></p><ul>"
                for issue in results['health_status']['issues']:
                    email_body += f"<li>{issue}</li>"
                email_body += "</ul>"
            
            email_body += """
            <hr>
            <p>This is an automated alert from the Budget Planner monitoring system.</p>
            """
            
            # Send email
            await self.email_service.send_email(
                to_email=admin_email,
                subject=subject,
                body=email_body
            )
            
            logger.info(f"Monitoring alert email sent to {admin_email}")
            
        except Exception as e:
            logger.error(f"Error sending monitoring alert email: {e}")
    
    async def send_health_alert(self, health_status: Dict[str, Any]):
        """Send email alert for unhealthy system status"""
        try:
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
            
            subject = f"🚨 Budget Planner System Health Alert - {health_status['status'].upper()}"
            
            email_body = f"""
            <h2>Budget Planner System Health Alert</h2>
            <p><strong>Status:</strong> {health_status['status']}</p>
            <p><strong>Timestamp:</strong> {health_status['timestamp']}</p>
            
            <h3>System Metrics</h3>
            <ul>
            """
            
            for metric, value in health_status.get('metrics', {}).items():
                email_body += f"<li>{metric}: {value}</li>"
            
            email_body += "</ul>"
            
            if health_status.get('issues'):
                email_body += "<h3>Issues Detected</h3><ul>"
                for issue in health_status['issues']:
                    email_body += f"<li>{issue}</li>"
                email_body += "</ul>"
            
            email_body += """
            <hr>
            <p>Please check the system immediately.</p>
            """
            
            await self.email_service.send_email(
                to_email=admin_email,
                subject=subject,
                body=email_body
            )
            
            logger.info(f"Health alert email sent to {admin_email}")
            
        except Exception as e:
            logger.error(f"Error sending health alert email: {e}")

# Global monitoring scheduler instance
monitoring_scheduler = MonitoringScheduler()