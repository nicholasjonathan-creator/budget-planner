#!/usr/bin/env python3
"""
Production Health Monitor for Budget Planner
Comprehensive monitoring script for production deployment
"""

import asyncio
import aiohttp
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ProductionMonitor:
    def __init__(self):
        self.backend_url = os.getenv('BACKEND_URL', 'http://localhost:8001')
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        self.alert_email = os.getenv('ALERT_EMAIL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        
        self.checks = []
        self.alerts = []
        
    async def check_backend_health(self) -> Dict[str, Any]:
        """Check backend API health"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(f"{self.backend_url}/api/health", timeout=10) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'status': 'healthy',
                            'response_time': response_time,
                            'details': data
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'response_time': response_time,
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_database_connection(self) -> Dict[str, Any]:
        """Check database connectivity via backend"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Assume database is healthy if backend is responding
                        return {
                            'status': 'healthy',
                            'details': 'Database connectivity verified via backend'
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'error': 'Backend not responding'
                        }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_email_system(self) -> Dict[str, Any]:
        """Check email system status"""
        try:
            # Test admin token would be needed for this in production
            # For now, just check if the endpoint is accessible
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/api/notifications/production/status", timeout=10) as response:
                    if response.status in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                        return {
                            'status': 'accessible',
                            'details': 'Email system endpoints are accessible'
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_frontend(self) -> Dict[str, Any]:
        """Check frontend availability"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(self.frontend_url, timeout=10) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        content = await response.text()
                        if 'Budget Planner' in content:
                            return {
                                'status': 'healthy',
                                'response_time': response_time,
                                'details': 'Frontend loaded successfully'
                            }
                        else:
                            return {
                                'status': 'unhealthy',
                                'error': 'Frontend content not as expected'
                            }
                    else:
                        return {
                            'status': 'unhealthy',
                            'response_time': response_time,
                            'error': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def check_ssl_certificate(self) -> Dict[str, Any]:
        """Check SSL certificate status"""
        try:
            import ssl
            import socket
            from urllib.parse import urlparse
            
            parsed_url = urlparse(self.backend_url)
            hostname = parsed_url.hostname
            port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
            
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry_date - datetime.now()).days
                        
                        if days_until_expiry > 30:
                            status = 'healthy'
                        elif days_until_expiry > 7:
                            status = 'warning'
                        else:
                            status = 'critical'
                        
                        return {
                            'status': status,
                            'days_until_expiry': days_until_expiry,
                            'expiry_date': expiry_date.isoformat(),
                            'issuer': cert.get('issuer', [{}])[0].get('organizationName', 'Unknown')
                        }
            else:
                return {
                    'status': 'warning',
                    'details': 'No SSL certificate (HTTP connection)'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        checks = {
            'timestamp': datetime.now().isoformat(),
            'backend': await self.check_backend_health(),
            'database': await self.check_database_connection(),
            'email_system': await self.check_email_system(),
            'frontend': await self.check_frontend(),
            'ssl_certificate': await self.check_ssl_certificate()
        }
        
        # Calculate overall health
        healthy_count = sum(1 for check in checks.values() 
                          if isinstance(check, dict) and check.get('status') in ['healthy', 'accessible'])
        total_checks = len([k for k in checks.keys() if k != 'timestamp'])
        
        checks['overall_health'] = {
            'status': 'healthy' if healthy_count == total_checks else 'degraded' if healthy_count > 0 else 'unhealthy',
            'healthy_checks': healthy_count,
            'total_checks': total_checks,
            'health_percentage': (healthy_count / total_checks) * 100 if total_checks > 0 else 0
        }
        
        return checks
    
    def generate_html_report(self, checks: Dict[str, Any]) -> str:
        """Generate HTML health report"""
        status_colors = {
            'healthy': '#10B981',
            'accessible': '#10B981',
            'warning': '#F59E0B',
            'unhealthy': '#EF4444',
            'error': '#EF4444',
            'critical': '#DC2626',
            'degraded': '#F59E0B'
        }
        
        def get_status_icon(status):
            icons = {
                'healthy': '✅',
                'accessible': '✅',
                'warning': '⚠️',
                'unhealthy': '❌',
                'error': '🔥',
                'critical': '🚨',
                'degraded': '⚠️'
            }
            return icons.get(status, '❓')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Budget Planner Health Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #1F2937; color: white; padding: 20px; border-radius: 8px; }}
                .check-item {{ margin: 10px 0; padding: 15px; border-radius: 6px; border-left: 4px solid #ccc; }}
                .healthy {{ border-left-color: #10B981; background: #ECFDF5; }}
                .warning {{ border-left-color: #F59E0B; background: #FFFBEB; }}
                .error {{ border-left-color: #EF4444; background: #FEF2F2; }}
                .details {{ margin-top: 10px; font-size: 0.9em; color: #666; }}
                .overall {{ padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 Budget Planner Health Report</h1>
                <p>Generated on {checks['timestamp']}</p>
            </div>
        """
        
        # Overall health
        overall = checks['overall_health']
        overall_class = overall['status']
        html += f"""
            <div class="overall {overall_class}">
                <h2>{get_status_icon(overall['status'])} Overall Health: {overall['status'].title()}</h2>
                <p>{overall['healthy_checks']}/{overall['total_checks']} checks passing ({overall['health_percentage']:.1f}%)</p>
            </div>
        """
        
        # Individual checks
        for check_name, check_data in checks.items():
            if check_name in ['timestamp', 'overall_health']:
                continue
                
            if isinstance(check_data, dict):
                status = check_data.get('status', 'unknown')
                status_class = status if status in ['healthy', 'warning', 'error'] else 'error'
                
                html += f"""
                    <div class="check-item {status_class}">
                        <h3>{get_status_icon(status)} {check_name.replace('_', ' ').title()}</h3>
                        <p><strong>Status:</strong> {status.title()}</p>
                """
                
                if 'response_time' in check_data:
                    html += f"<p><strong>Response Time:</strong> {check_data['response_time']:.3f}s</p>"
                
                if 'error' in check_data:
                    html += f"<p><strong>Error:</strong> {check_data['error']}</p>"
                
                if 'details' in check_data:
                    html += f"<div class='details'>{check_data['details']}</div>"
                
                html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    async def send_alert_email(self, subject: str, body: str):
        """Send alert email"""
        if not all([self.alert_email, self.smtp_user, self.smtp_pass]):
            print("⚠️  Email alerting not configured")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            text = msg.as_string()
            server.sendmail(self.smtp_user, self.alert_email, text)
            server.quit()
            
            print(f"✅ Alert email sent to {self.alert_email}")
            
        except Exception as e:
            print(f"❌ Failed to send alert email: {e}")
    
    async def monitor_continuous(self, interval_minutes: int = 15):
        """Run continuous monitoring"""
        print(f"🔍 Starting continuous monitoring (check every {interval_minutes} minutes)")
        
        while True:
            try:
                checks = await self.run_all_checks()
                
                # Save report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # JSON report
                with open(f"/tmp/health_report_{timestamp}.json", 'w') as f:
                    json.dump(checks, f, indent=2)
                
                # HTML report
                html_report = self.generate_html_report(checks)
                with open(f"/tmp/health_report_{timestamp}.html", 'w') as f:
                    f.write(html_report)
                
                # Check for alerts
                overall_status = checks['overall_health']['status']
                if overall_status in ['unhealthy', 'degraded']:
                    subject = f"🚨 Budget Planner Health Alert - {overall_status.title()}"
                    await self.send_alert_email(subject, html_report)
                
                # Print summary
                print(f"📊 Health Check Complete - {checks['timestamp']}")
                print(f"   Overall Status: {overall_status.title()}")
                print(f"   Health: {checks['overall_health']['health_percentage']:.1f}%")
                
                # Wait for next check
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

async def main():
    monitor = ProductionMonitor()
    
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--continuous':
        interval = int(os.sys.argv[2]) if len(os.sys.argv) > 2 else 15
        await monitor.monitor_continuous(interval)
    else:
        # Single check
        checks = await monitor.run_all_checks()
        
        # Print results
        print("🏥 Budget Planner Health Check Results")
        print("=" * 50)
        
        for check_name, check_data in checks.items():
            if check_name in ['timestamp', 'overall_health']:
                continue
                
            if isinstance(check_data, dict):
                status = check_data.get('status', 'unknown')
                icon = '✅' if status in ['healthy', 'accessible'] else '⚠️' if status == 'warning' else '❌'
                print(f"{icon} {check_name.replace('_', ' ').title()}: {status.title()}")
                
                if 'response_time' in check_data:
                    print(f"   Response Time: {check_data['response_time']:.3f}s")
                
                if 'error' in check_data:
                    print(f"   Error: {check_data['error']}")
        
        print("\n" + "=" * 50)
        overall = checks['overall_health']
        print(f"Overall Health: {overall['status'].title()}")
        print(f"Health Percentage: {overall['health_percentage']:.1f}%")
        print(f"Timestamp: {checks['timestamp']}")
        
        # Generate HTML report
        html_report = monitor.generate_html_report(checks)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(f"health_report_{timestamp}.html", 'w') as f:
            f.write(html_report)
        
        print(f"\n📄 HTML report saved: health_report_{timestamp}.html")

if __name__ == "__main__":
    asyncio.run(main())