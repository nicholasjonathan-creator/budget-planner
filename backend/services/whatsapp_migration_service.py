"""
WhatsApp Feature Migration Service
Handles onboarding existing users to the new WhatsApp SMS integration feature
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from database import db
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class WhatsAppMigrationService:
    def __init__(self):
        self.db = db
        self.email_service = EmailService()
    
    async def get_users_without_phone_verification(self) -> List[Dict[str, Any]]:
        """Get all active users who haven't verified their phone numbers yet"""
        try:
            users = await self.db.users.find({
                "is_active": True,
                "$or": [
                    {"phone_verified": {"$exists": False}},
                    {"phone_verified": False},
                    {"phone_number": {"$exists": False}}
                ]
            }).to_list(None)
            
            logger.info(f"Found {len(users)} users without phone verification")
            return users
            
        except Exception as e:
            logger.error(f"Error getting users without phone verification: {e}")
            return []
    
    async def send_whatsapp_feature_email(self, user: Dict[str, Any]) -> bool:
        """Send WhatsApp feature announcement email to a user"""
        try:
            email_subject = "🚀 NEW: WhatsApp SMS Integration - Auto-Track Your Transactions!"
            
            email_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10B981, #3B82F6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #fff; padding: 30px; border: 1px solid #e5e7eb; }}
                    .feature-box {{ background: #F0FDF4; border: 2px solid #10B981; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                    .steps {{ background: #FEF3C7; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                    .cta-button {{ display: inline-block; background: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 0; }}
                    .footer {{ background: #F9FAFB; padding: 20px; text-align: center; color: #6B7280; border-radius: 0 0 10px 10px; }}
                    .highlight {{ color: #10B981; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Exciting News, {user.get('username', 'User')}!</h1>
                        <p style="font-size: 18px; margin: 10px 0;">WhatsApp SMS Integration is Here!</p>
                    </div>
                    
                    <div class="content">
                        <div class="feature-box">
                            <h2 style="color: #10B981; margin-top: 0;">📱 Forward Bank SMS → Automatic Tracking</h2>
                            <p><strong>No more manual entry!</strong> Simply forward your bank SMS messages to our WhatsApp number and transactions appear in your dashboard instantly.</p>
                            
                            <p><strong>✅ What's included:</strong></p>
                            <ul>
                                <li>🏦 <strong>All Major Banks:</strong> HDFC, ICICI, SBI, Axis, Scapia, Federal</li>
                                <li>⚡ <strong>Instant Processing:</strong> Real-time transaction creation</li>
                                <li>🔐 <strong>100% Secure:</strong> Phone verification ensures your privacy</li>
                                <li>💰 <strong>Completely FREE:</strong> No charges for WhatsApp forwarding</li>
                                <li>🇮🇳 <strong>Built for India:</strong> Supports Indian banking SMS formats</li>
                            </ul>
                        </div>
                        
                        <div class="steps">
                            <h3 style="color: #D97706; margin-top: 0;">🎯 Get Started in 2 Minutes:</h3>
                            <ol>
                                <li><strong>Verify Your Phone:</strong> Add your WhatsApp number securely</li>
                                <li><strong>Get OTP:</strong> Receive verification code on WhatsApp</li>
                                <li><strong>Start Forwarding:</strong> Send bank SMS to our number</li>
                                <li><strong>Auto-Magic:</strong> Transactions appear instantly! ✨</li>
                            </ol>
                        </div>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="https://57d97870-0a22-4961-80d4-f1bd4b737cc9.preview.emergentagent.com" class="cta-button">
                                🚀 Set Up WhatsApp Integration Now
                            </a>
                        </div>
                        
                        <div style="background: #EFF6FF; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h4 style="color: #1E40AF; margin-top: 0;">🔒 Your Security is Our Priority</h4>
                            <p style="margin-bottom: 0;">We use bank-level security with phone verification to ensure only YOU can process your SMS messages. Your data stays private and secure.</p>
                        </div>
                        
                        <p>Ready to experience the <span class="highlight">easiest way to track expenses</span> in India? Set up WhatsApp integration today!</p>
                        
                        <p style="margin-bottom: 0;">
                            Best regards,<br>
                            <strong>Budget Planner Team</strong><br>
                            <em>Built for India 🇮🇳</em>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>Budget Planner - Your Smart Financial Companion</p>
                        <p style="font-size: 12px;">You received this email because you have an account with Budget Planner. This is a one-time feature announcement.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            await self.email_service.send_email(
                to_email=user['email'],
                subject=email_subject,
                html_content=email_content
            )
            
            logger.info(f"WhatsApp feature email sent to {user['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp feature email to {user.get('email')}: {e}")
            return False
    
    async def notify_all_existing_users(self) -> Dict[str, Any]:
        """Send WhatsApp feature announcement to all users without phone verification"""
        try:
            # Get users who need to be notified
            users = await self.get_users_without_phone_verification()
            
            if not users:
                return {
                    "success": True,
                    "message": "No users need to be notified",
                    "users_notified": 0,
                    "emails_sent": 0,
                    "errors": 0
                }
            
            # Send emails
            emails_sent = 0
            errors = 0
            
            for user in users:
                try:
                    success = await self.send_whatsapp_feature_email(user)
                    if success:
                        emails_sent += 1
                    else:
                        errors += 1
                        
                except Exception as e:
                    logger.error(f"Error processing user {user.get('email')}: {e}")
                    errors += 1
            
            # Log migration stats
            await self.log_migration_stats({
                "total_users": len(users),
                "emails_sent": emails_sent,
                "errors": errors,
                "timestamp": datetime.utcnow()
            })
            
            return {
                "success": True,
                "message": f"WhatsApp feature notification completed",
                "users_notified": len(users),
                "emails_sent": emails_sent,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error in notify_all_existing_users: {e}")
            return {
                "success": False,
                "error": str(e),
                "users_notified": 0,
                "emails_sent": 0,
                "errors": 0
            }
    
    async def log_migration_stats(self, stats: Dict[str, Any]):
        """Log migration statistics for tracking"""
        try:
            await self.db.whatsapp_migration_logs.insert_one({
                "event": "feature_announcement",
                "stats": stats,
                "created_at": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error logging migration stats: {e}")
    
    async def get_migration_stats(self) -> Dict[str, Any]:
        """Get migration statistics"""
        try:
            # Get total users
            total_users = await self.db.users.count_documents({"is_active": True})
            
            # Get users with phone verification
            verified_users = await self.db.users.count_documents({
                "is_active": True,
                "phone_verified": True
            })
            
            # Get users without phone verification
            unverified_users = total_users - verified_users
            
            # Get migration logs
            migration_logs = await self.db.whatsapp_migration_logs.find({}).sort("created_at", -1).limit(5).to_list(5)
            
            return {
                "total_users": total_users,
                "verified_users": verified_users,
                "unverified_users": unverified_users,
                "verification_rate": round((verified_users / total_users) * 100, 2) if total_users > 0 else 0,
                "recent_migrations": migration_logs
            }
            
        except Exception as e:
            logger.error(f"Error getting migration stats: {e}")
            return {
                "total_users": 0,
                "verified_users": 0,
                "unverified_users": 0,
                "verification_rate": 0,
                "recent_migrations": []
            }


# Initialize the service
whatsapp_migration_service = WhatsAppMigrationService()