import os
import logging
from typing import Dict, Any, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

class ProductionEmailConfig:
    """Production email configuration and sender verification management"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL', 'noreply@budgetplanner.app')
        self.sender_name = os.getenv('SENDER_NAME', 'Budget Planner')
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
        
        # Production settings
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.enable_email_sending = os.getenv('ENABLE_EMAIL_SENDING', 'true').lower() == 'true'
        
    async def verify_sender_configuration(self) -> Dict[str, Any]:
        """Verify sender email configuration and domain status"""
        if not self.client:
            return {
                'status': 'error',
                'message': 'SendGrid API key not configured',
                'is_production_ready': False
            }
        
        try:
            # Check API key status
            response = self.client.client.user.get()
            api_status = response.status_code == 200
            
            # Check sender verification status
            sender_status = await self._check_sender_verification()
            
            # Check domain authentication
            domain_status = await self._check_domain_authentication()
            
            is_production_ready = (
                api_status and 
                sender_status.get('verified', False) and
                domain_status.get('authenticated', False)
            )
            
            return {
                'status': 'success',
                'api_key_valid': api_status,
                'sender_verification': sender_status,
                'domain_authentication': domain_status,
                'is_production_ready': is_production_ready,
                'sender_email': self.sender_email,
                'environment': self.environment
            }
            
        except Exception as e:
            logger.error(f"Error verifying sender configuration: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'is_production_ready': False
            }
    
    async def _check_sender_verification(self) -> Dict[str, Any]:
        """Check if sender email is verified"""
        try:
            # For now, return mock verification status
            # In production, this would check SendGrid's verified senders
            return {
                'verified': False,
                'message': f'Sender email {self.sender_email} needs verification',
                'action_required': 'Verify sender email in SendGrid dashboard'
            }
                
        except Exception as e:
            logger.error(f"Error checking sender verification: {e}")
            return {
                'verified': False,
                'message': f'Error checking verification: {str(e)}'
            }
    
    async def _check_domain_authentication(self) -> Dict[str, Any]:
        """Check domain authentication status"""
        try:
            # Extract domain from sender email
            domain = self.sender_email.split('@')[1] if '@' in self.sender_email else None
            
            if not domain:
                return {
                    'authenticated': False,
                    'message': 'Invalid sender email format'
                }
            
            # For now, return mock domain status
            # In production, this would check SendGrid's domain authentication
            return {
                'authenticated': False,
                'domain': domain,
                'message': f'Domain {domain} needs authentication setup',
                'action_required': 'Set up domain authentication in SendGrid dashboard'
            }
                
        except Exception as e:
            logger.error(f"Error checking domain authentication: {e}")
            return {
                'authenticated': False,
                'message': f'Error checking domain: {str(e)}'
            }
    
    async def get_production_checklist(self) -> Dict[str, Any]:
        """Get production readiness checklist"""
        config_status = await self.verify_sender_configuration()
        
        checklist = {
            'api_configuration': {
                'status': 'complete' if config_status.get('api_key_valid') else 'pending',
                'description': 'SendGrid API key configured',
                'action': 'Add SENDGRID_API_KEY to environment variables' if not config_status.get('api_key_valid') else None
            },
            'sender_verification': {
                'status': 'complete' if config_status.get('sender_verification', {}).get('verified') else 'pending',
                'description': 'Sender email verified',
                'action': 'Verify sender email in SendGrid dashboard' if not config_status.get('sender_verification', {}).get('verified') else None
            },
            'domain_authentication': {
                'status': 'complete' if config_status.get('domain_authentication', {}).get('authenticated') else 'pending',
                'description': 'Domain authentication configured',
                'action': 'Set up domain authentication in SendGrid' if not config_status.get('domain_authentication', {}).get('authenticated') else None
            },
            'environment_variables': {
                'status': 'complete' if all([
                    self.sender_email,
                    self.sender_name,
                    self.api_key
                ]) else 'pending',
                'description': 'All required environment variables set',
                'action': 'Set SENDER_EMAIL, SENDER_NAME, SENDGRID_API_KEY'
            },
            'production_settings': {
                'status': 'complete' if self.environment == 'production' else 'pending',
                'description': 'Environment set to production',
                'action': 'Set ENVIRONMENT=production'
            }
        }
        
        completed_tasks = sum(1 for task in checklist.values() if task['status'] == 'complete')
        total_tasks = len(checklist)
        
        return {
            'checklist': checklist,
            'completion_percentage': (completed_tasks / total_tasks) * 100,
            'is_production_ready': completed_tasks == total_tasks,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks
        }
    
    def get_production_smtp_config(self) -> Dict[str, Any]:
        """Get production SMTP configuration for alternative email services"""
        return {
            'smtp_settings': {
                'sendgrid': {
                    'host': 'smtp.sendgrid.net',
                    'port': '587',
                    'username': 'apikey',
                    'password': self.api_key,
                    'use_tls': True
                },
                # Example for other services:
                'gmail': {
                    'host': 'smtp.gmail.com',
                    'port': '587',
                    'username': 'your-email@gmail.com',
                    'password': 'your-app-password',
                    'use_tls': True
                },
                'outlook': {
                    'host': 'smtp-mail.outlook.com',
                    'port': '587',
                    'username': 'your-email@outlook.com',
                    'password': 'your-password',
                    'use_tls': True
                }
            },
            'recommended': 'sendgrid',
            'fallback_options': ['gmail', 'outlook', 'amazon_ses']
        }

# Global production config instance
production_email_config = ProductionEmailConfig()