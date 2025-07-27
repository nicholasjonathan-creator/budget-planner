"""
Production Monitoring and Error Detection System
Monitors WhatsApp transactions, failed processing, and system health
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import os
from database import db

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    level: AlertLevel
    message: str
    timestamp: datetime
    details: Dict[str, Any]
    user_id: Optional[str] = None
    resolved: bool = False

class MonitoringService:
    def __init__(self):
        self.alerts: List[Alert] = []
        self.last_check_time = datetime.utcnow()
        
    async def check_failed_transactions(self, time_window_minutes: int = 10) -> List[Alert]:
        """
        Check for failed WhatsApp transactions in the last X minutes
        """
        alerts = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        try:
            # Check for failed SMS in the database
            failed_sms = []
            async for sms in db.failed_sms.find({
                'created_at': {'$gte': cutoff_time}
            }).sort('created_at', -1):
                failed_sms.append(sms)
            
            if failed_sms:
                alert = Alert(
                    level=AlertLevel.ERROR,
                    message=f"Found {len(failed_sms)} failed SMS transactions in last {time_window_minutes} minutes",
                    timestamp=datetime.utcnow(),
                    details={
                        'failed_count': len(failed_sms),
                        'time_window': time_window_minutes,
                        'failed_sms': [
                            {
                                'sms_content': sms.get('sms_content', '')[:100],
                                'error': sms.get('error', ''),
                                'user_id': sms.get('user_id', ''),
                                'created_at': sms.get('created_at', '')
                            } for sms in failed_sms[:5]  # Show first 5
                        ]
                    }
                )
                alerts.append(alert)
            
            # Check for WhatsApp webhook errors by analyzing logs
            webhook_errors = await self._check_webhook_errors(time_window_minutes)
            if webhook_errors:
                alert = Alert(
                    level=AlertLevel.CRITICAL,
                    message=f"WhatsApp webhook errors detected: {len(webhook_errors)} failures",
                    timestamp=datetime.utcnow(),
                    details={
                        'webhook_errors': webhook_errors,
                        'time_window': time_window_minutes
                    }
                )
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error checking failed transactions: {e}")
            alert = Alert(
                level=AlertLevel.ERROR,
                message=f"Monitoring system error: {str(e)}",
                timestamp=datetime.utcnow(),
                details={'error': str(e)}
            )
            alerts.append(alert)
        
        return alerts
    
    async def _check_webhook_errors(self, time_window_minutes: int) -> List[Dict[str, Any]]:
        """
        Check for webhook processing errors by analyzing recent logs
        """
        webhook_errors = []
        
        try:
            # Read recent log files
            log_files = [
                '/var/log/supervisor/backend.err.log',
                '/var/log/supervisor/backend.out.log'
            ]
            
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        
                    # Look for WhatsApp-related errors
                    for line in lines[-1000:]:  # Check last 1000 lines
                        if 'whatsapp' in line.lower() and ('error' in line.lower() or 'failed' in line.lower()):
                            # Extract timestamp from log line
                            if '2025-' in line:
                                try:
                                    timestamp_str = line.split(' - ')[0]
                                    log_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                                    
                                    if log_time > cutoff_time:
                                        webhook_errors.append({
                                            'timestamp': log_time.isoformat(),
                                            'message': line.strip(),
                                            'log_file': log_file
                                        })
                                except:
                                    pass
                        
                        # Look for Twilio authentication errors
                        if 'HTTP 401' in line and 'twilio' in line.lower():
                            webhook_errors.append({
                                'timestamp': datetime.utcnow().isoformat(),
                                'message': line.strip(),
                                'log_file': log_file,
                                'error_type': 'twilio_auth_error'
                            })
                            
                except Exception as e:
                    logger.warning(f"Could not read log file {log_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking webhook errors: {e}")
            
        return webhook_errors
    
    async def check_transaction_sync_issues(self, user_id: str) -> List[Alert]:
        """
        Check for frontend-backend sync issues for a specific user
        Triggered when user does force refresh or reports missing transactions
        """
        alerts = []
        
        try:
            # Get recent transactions for user
            recent_transactions = []
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            async for transaction in db.transactions.find({
                'user_id': user_id,
                '_id': {'$gte': cutoff_time}
            }).sort('_id', -1):
                recent_transactions.append(transaction)
            
            # Check for transactions created but not in current month view
            current_month = datetime.utcnow().month - 1  # 0-indexed
            current_year = datetime.utcnow().year
            
            mismatched_transactions = []
            for transaction in recent_transactions:
                transaction_date = transaction.get('date')
                if transaction_date:
                    if isinstance(transaction_date, str):
                        try:
                            transaction_date = datetime.fromisoformat(transaction_date.replace('T', ' ').replace('Z', ''))
                        except:
                            continue
                    
                    if (transaction_date.month - 1) != current_month or transaction_date.year != current_year:
                        mismatched_transactions.append({
                            'id': str(transaction.get('_id')),
                            'amount': transaction.get('amount'),
                            'date': transaction_date.isoformat(),
                            'expected_month': current_month,
                            'actual_month': transaction_date.month - 1
                        })
            
            if mismatched_transactions:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    message=f"Found {len(mismatched_transactions)} transactions in different months than current view",
                    timestamp=datetime.utcnow(),
                    details={
                        'user_id': user_id,
                        'mismatched_transactions': mismatched_transactions,
                        'current_month_view': current_month,
                        'current_year_view': current_year
                    },
                    user_id=user_id
                )
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error checking transaction sync for user {user_id}: {e}")
            
        return alerts
    
    async def check_system_health(self) -> Dict[str, Any]:
        """
        Check overall system health metrics
        """
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'metrics': {},
            'issues': []
        }
        
        try:
            # Check database connectivity
            try:
                await db.users.count_documents({})
                health_status['metrics']['database'] = 'healthy'
            except Exception as e:
                health_status['metrics']['database'] = 'error'
                health_status['issues'].append(f"Database connectivity error: {str(e)}")
                health_status['status'] = 'unhealthy'
            
            # Check recent transaction processing rate
            last_hour = datetime.utcnow() - timedelta(hours=1)
            recent_transactions = await db.transactions.count_documents({
                '_id': {'$gte': last_hour}
            })
            
            health_status['metrics']['recent_transactions'] = recent_transactions
            
            # Check for failed transactions
            recent_failures = await db.failed_sms.count_documents({
                'created_at': {'$gte': last_hour}
            })
            
            health_status['metrics']['recent_failures'] = recent_failures
            
            if recent_failures > 0:
                health_status['issues'].append(f"Found {recent_failures} failed transactions in last hour")
                health_status['status'] = 'degraded'
            
            # Check WhatsApp service health
            whatsapp_health = await self._check_whatsapp_health()
            health_status['metrics']['whatsapp_service'] = whatsapp_health['status']
            
            if whatsapp_health['status'] != 'healthy':
                health_status['issues'].extend(whatsapp_health['issues'])
                health_status['status'] = 'degraded'
                
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
            health_status['status'] = 'error'
            health_status['issues'].append(f"Health check error: {str(e)}")
            
        return health_status
    
    async def _check_whatsapp_health(self) -> Dict[str, Any]:
        """
        Check WhatsApp service specific health
        """
        health = {
            'status': 'healthy',
            'issues': [],
            'last_successful_processing': None
        }
        
        try:
            # Check for recent successful WhatsApp transactions
            last_24h = datetime.utcnow() - timedelta(hours=24)
            
            recent_whatsapp = await db.transactions.find_one({
                'processing_method': 'whatsapp_auto',
                '_id': {'$gte': last_24h}
            }, sort=[('_id', -1)])
            
            if recent_whatsapp:
                health['last_successful_processing'] = recent_whatsapp['_id'].generation_time.isoformat()
            else:
                health['issues'].append("No successful WhatsApp transactions in last 24 hours")
                health['status'] = 'warning'
            
            # Check Twilio configuration
            twilio_config = {
                'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
                'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
                'whatsapp_number': os.getenv('TWILIO_WHATSAPP_NUMBER')
            }
            
            if not all(twilio_config.values()):
                health['issues'].append("Missing Twilio configuration")
                health['status'] = 'error'
                
        except Exception as e:
            logger.error(f"Error checking WhatsApp health: {e}")
            health['status'] = 'error'
            health['issues'].append(f"WhatsApp health check error: {str(e)}")
            
        return health
    
    async def run_monitoring_cycle(self, time_window_minutes: int = 10):
        """
        Run a complete monitoring cycle
        """
        monitoring_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'alerts': [],
            'health_status': {},
            'summary': {
                'total_alerts': 0,
                'critical_alerts': 0,
                'error_alerts': 0,
                'warning_alerts': 0
            }
        }
        
        try:
            # Check for failed transactions
            failed_transaction_alerts = await self.check_failed_transactions(time_window_minutes)
            monitoring_results['alerts'].extend(failed_transaction_alerts)
            
            # Check system health
            health_status = await self.check_system_health()
            monitoring_results['health_status'] = health_status
            
            # Count alerts by level
            for alert in monitoring_results['alerts']:
                monitoring_results['summary']['total_alerts'] += 1
                if alert.level == AlertLevel.CRITICAL:
                    monitoring_results['summary']['critical_alerts'] += 1
                elif alert.level == AlertLevel.ERROR:
                    monitoring_results['summary']['error_alerts'] += 1
                elif alert.level == AlertLevel.WARNING:
                    monitoring_results['summary']['warning_alerts'] += 1
            
            # Log monitoring results
            if monitoring_results['summary']['total_alerts'] > 0:
                logger.warning(f"Monitoring cycle found {monitoring_results['summary']['total_alerts']} alerts")
            else:
                logger.info("Monitoring cycle completed - no alerts")
                
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            
        return monitoring_results
    
    async def store_monitoring_results(self, results: Dict[str, Any]):
        """
        Store monitoring results in database for historical analysis
        """
        try:
            await db.monitoring_results.insert_one({
                **results,
                'created_at': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error storing monitoring results: {e}")

# Global monitoring service instance
monitoring_service = MonitoringService()