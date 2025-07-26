import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models.user import User
from models.notification import NotificationType, NotificationLog

logger = logging.getLogger(__name__)

class EmailDeliveryError(Exception):
    """Custom exception for email delivery failures"""
    pass

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL', 'noreply@budgetplanner.app')
        
        if not self.api_key:
            raise ValueError("SendGrid API key not found in environment variables")
        
        self.client = SendGridAPIClient(self.api_key)
        
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        plain_text_content: Optional[str] = None,
        user_id: Optional[str] = None,
        notification_type: Optional[NotificationType] = None
    ) -> bool:
        """
        Send an email using SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            plain_text_content: Plain text version (optional)
            user_id: User ID for logging purposes
            notification_type: Type of notification for logging
            
        Returns:
            bool: True if email was sent successfully
        """
        try:
            message = Mail(
                from_email=self.sender_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_text_content
            )
            
            response = self.client.send(message)
            
            # Log the notification
            if user_id and notification_type:
                await self._log_notification(
                    user_id=user_id,
                    notification_type=notification_type,
                    email_address=to_email,
                    subject=subject,
                    delivery_status="sent" if response.status_code == 202 else "failed"
                )
            
            logger.info(f"Email sent successfully to {to_email}. Status: {response.status_code}")
            return response.status_code == 202
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            
            # Log the failure
            if user_id and notification_type:
                await self._log_notification(
                    user_id=user_id,
                    notification_type=notification_type,
                    email_address=to_email,
                    subject=subject,
                    delivery_status="failed",
                    error_message=str(e)
                )
            
            raise EmailDeliveryError(f"Failed to send email: {str(e)}")
    
    async def _log_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        email_address: str,
        subject: str,
        delivery_status: str = "sent",
        error_message: Optional[str] = None
    ):
        """Log notification to database"""
        try:
            from database import db
            
            log_entry = NotificationLog(
                user_id=user_id,
                notification_type=notification_type,
                email_address=email_address,
                subject=subject,
                delivery_status=delivery_status,
                error_message=error_message
            )
            
            await db.notification_logs.insert_one(log_entry.dict(by_alias=True))
            
        except Exception as e:
            logger.error(f"Failed to log notification: {str(e)}")
    
    def _get_base_template(self, title: str, content: str, user_name: str = "") -> str:
        """
        Get base HTML email template
        
        Args:
            title: Email title
            content: Main email content (HTML)
            user_name: User's name for personalization
            
        Returns:
            str: Complete HTML email template
        """
        greeting = f"Hi {user_name}," if user_name else "Hello,"
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    line-height: 1.6; 
                    color: #333333; 
                    margin: 0; 
                    padding: 0; 
                    background-color: #f8f9fa;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background-color: #ffffff; 
                    border-radius: 8px; 
                    overflow: hidden; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px 20px; 
                    text-align: center; 
                }}
                .header h1 {{ 
                    margin: 0; 
                    font-size: 28px; 
                    font-weight: 600; 
                }}
                .content {{ 
                    padding: 30px 20px; 
                }}
                .greeting {{ 
                    font-size: 16px; 
                    margin-bottom: 20px; 
                }}
                .highlight {{ 
                    background-color: #f8f9fa; 
                    border-left: 4px solid #667eea; 
                    padding: 15px; 
                    margin: 20px 0; 
                    border-radius: 4px; 
                }}
                .button {{ 
                    display: inline-block; 
                    background-color: #667eea; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 6px; 
                    font-weight: 500; 
                    margin: 15px 0; 
                }}
                .footer {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    text-align: center; 
                    font-size: 12px; 
                    color: #666666; 
                }}
                .amount {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #667eea; 
                }}
                .warning {{ 
                    color: #dc3545; 
                    font-weight: 600; 
                }}
                .success {{ 
                    color: #28a745; 
                    font-weight: 600; 
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 15px 0; 
                }}
                th, td {{ 
                    padding: 10px; 
                    text-align: left; 
                    border-bottom: 1px solid #dee2e6; 
                }}
                th {{ 
                    background-color: #f8f9fa; 
                    font-weight: 600; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏦 Budget Planner</h1>
                </div>
                <div class="content">
                    <div class="greeting">{greeting}</div>
                    {content}
                </div>
                <div class="footer">
                    <p>This email was sent from your Budget Planner account.<br>
                    Built with ❤️ for India 🇮🇳</p>
                    <p>To manage your notification preferences, <a href="#" style="color: #667eea;">click here</a>.</p>
                </div>
            </div>
        </body>
        </html>
        """