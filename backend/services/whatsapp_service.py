"""
WhatsApp SMS Processing Service
Integrates with Twilio WhatsApp API to receive forwarded bank SMS messages
and process them using existing SMS parsing logic.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from services.sms_parser import SMSTransactionParser
from services.transaction_service import TransactionService
from models.user import User
from database import db

logger = logging.getLogger(__name__)

class WhatsAppSMSProcessor:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            raise ValueError("Missing Twilio configuration. Check environment variables.")
        
        self.client = Client(self.account_sid, self.auth_token)
        self.validator = RequestValidator(self.auth_token)
        self.sms_parser = SMSTransactionParser()
        self.transaction_service = TransactionService()
        self.db = db
    
    def validate_webhook(self, url: str, params: Dict[str, Any], signature: str) -> bool:
        """Validate that the webhook request came from Twilio"""
        try:
            return self.validator.validate(url, params, signature)
        except Exception as e:
            logger.error(f"Webhook validation error: {e}")
            return False
    
    async def process_whatsapp_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming WhatsApp message containing forwarded bank SMS
        """
        try:
            # Extract message details from Twilio webhook
            message_body = webhook_data.get('Body', '').strip()
            from_number = webhook_data.get('From', '').replace('whatsapp:', '')
            to_number = webhook_data.get('To', '').replace('whatsapp:', '')
            message_sid = webhook_data.get('MessageSid', '')
            
            logger.info(f"Received WhatsApp message from {from_number}: {message_body[:100]}...")
            
            # Check if this is a valid WhatsApp message to our number
            if to_number != self.whatsapp_number:
                logger.warning(f"Message received for unexpected number: {to_number}")
                return {"status": "ignored", "reason": "wrong_number"}
            
            # Find user by phone number (simplified - you might want a better user mapping)
            user = await self.find_user_by_phone(from_number)
            if not user:
                # Send instructions to new user
                await self.send_welcome_message(from_number)
                return {"status": "new_user", "message": "Welcome message sent"}
            
            # Process the SMS content using existing parser
            parsing_result = await self.parse_sms_content(message_body, user['user_id'])
            
            if parsing_result['success']:
                # Send confirmation message
                await self.send_success_message(from_number, parsing_result['transaction'])
                
                # Send email notification if enabled
                if user.get('email_notifications_enabled', False):
                    await self.send_email_notification(user, parsing_result['transaction'])
                
                return {
                    "status": "success",
                    "transaction_id": parsing_result['transaction']['transaction_id'],
                    "amount": parsing_result['transaction']['amount'],
                    "merchant": parsing_result['transaction']['merchant']
                }
            else:
                # Send error message with parsing failure details
                await self.send_error_message(from_number, parsing_result['error'])
                return {"status": "failed", "error": parsing_result['error']}
        
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            await self.send_error_message(from_number, "Internal processing error")
            return {"status": "error", "error": str(e)}
    
    async def find_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Find user by phone number - simplified implementation"""
        try:
            # Remove WhatsApp prefix and normalize phone number
            clean_number = phone_number.replace('whatsapp:', '').replace('+', '')
            
            # For now, return a test user - you should implement proper user lookup
            # In production, you'd have a users collection with phone numbers
            users_collection = self.db.users
            user = await users_collection.find_one({"phone_number": clean_number})
            
            if not user:
                # For demo purposes, create a test user mapping
                # In production, users would register their phone numbers
                test_user = await users_collection.find_one({"email": "testuser@example.com"})
                if test_user:
                    # Update test user with phone number
                    await users_collection.update_one(
                        {"_id": test_user["_id"]},
                        {"$set": {"phone_number": clean_number}}
                    )
                    return test_user
            
            return user
        except Exception as e:
            logger.error(f"Error finding user by phone: {e}")
            return None
    
    async def parse_sms_content(self, sms_text: str, user_id: str) -> Dict[str, Any]:
        """Parse SMS content using existing SMS parser"""
        try:
            # Use existing SMS parsing logic
            transaction = self.sms_parser.parse_sms(
                sms_text=sms_text,
                phone_number="whatsapp_forwarded"  # Special identifier for WhatsApp
            )
            
            if transaction:
                # Convert Transaction object to dict and add user_id
                transaction_dict = transaction.dict()
                transaction_dict['user_id'] = user_id
                transaction_dict['processing_method'] = "whatsapp_auto"
                transaction_dict['raw_sms'] = sms_text
                transaction_dict['source'] = "whatsapp"
                
                # Save transaction to database
                transaction_result = await self.db.transactions.insert_one(transaction_dict)
                transaction_id = str(transaction_result.inserted_id)
                
                # Add the ID to the transaction dict for response
                transaction_dict['transaction_id'] = transaction_id
                
                return {
                    "success": True,
                    "transaction": transaction_dict,
                    "parsing_method": "sms_parser"
                }
            else:
                return {
                    "success": False,
                    "error": "Unable to parse bank SMS - format not recognized"
                }
        
        except Exception as e:
            logger.error(f"Error parsing SMS content: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_welcome_message(self, to_number: str):
        """Send welcome message to new WhatsApp user"""
        try:
            welcome_message = """🏦 Welcome to Budget Planner!

To get started:
1. Register at our app: https://0f621684-5333-4b17-9188-b8424f0e0b0c.preview.emergentagent.com
2. Forward your bank SMS messages here
3. We'll automatically track your transactions!

Supported banks: HDFC, ICICI, SBI, Axis, Scapia

Simply forward any bank SMS to this number and we'll handle the rest! 🚀"""

            message = self.client.messages.create(
                body=welcome_message,
                from_=f'whatsapp:{self.whatsapp_number}',
                to=f'whatsapp:{to_number}'
            )
            
            logger.info(f"Welcome message sent to {to_number}: {message.sid}")
            
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
    
    async def send_success_message(self, to_number: str, transaction: Dict[str, Any]):
        """Send success confirmation message"""
        try:
            amount = transaction.get('amount', 0)
            merchant = transaction.get('merchant', 'Unknown')
            transaction_type = transaction.get('transaction_type', 'expense')
            category = transaction.get('category', 'Other')
            
            emoji = "💸" if transaction_type == "expense" else "💰"
            
            success_message = f"""{emoji} Transaction Processed Successfully!

Amount: ₹{amount:,.2f}
Type: {transaction_type.title()}
Merchant: {merchant}
Category: {category}

✅ Added to your Budget Planner dashboard!
View details: https://0f621684-5333-4b17-9188-b8424f0e0b0c.preview.emergentagent.com"""

            message = self.client.messages.create(
                body=success_message,
                from_=f'whatsapp:{self.whatsapp_number}',
                to=f'whatsapp:{to_number}'
            )
            
            logger.info(f"Success message sent to {to_number}: {message.sid}")
            
        except Exception as e:
            logger.error(f"Error sending success message: {e}")
    
    async def send_error_message(self, to_number: str, error_details: str):
        """Send error message when SMS parsing fails"""
        try:
            error_message = f"""❌ Unable to Process SMS

Issue: {error_details}

Please ensure:
✅ Forward bank SMS messages only
✅ Include complete SMS text
✅ Supported banks: HDFC, ICICI, SBI, Axis, Scapia

Try forwarding the complete SMS again, or add it manually in the app.

App: https://0f621684-5333-4b17-9188-b8424f0e0b0c.preview.emergentagent.com"""

            message = self.client.messages.create(
                body=error_message,
                from_=f'whatsapp:{self.whatsapp_number}',
                to=f'whatsapp:{to_number}'
            )
            
            logger.info(f"Error message sent to {to_number}: {message.sid}")
            
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
    
    async def send_email_notification(self, user: Dict[str, Any], transaction: Dict[str, Any]):
        """Send email notification for processed transaction"""
        try:
            if user.get('email') and user.get('transaction_confirmation_enabled', False):
                # Email notification functionality temporarily disabled
                # await send_transaction_confirmation_email(
                #     user['email'],
                #     user.get('username', 'User'),
                #     transaction
                # )
                logger.info(f"Email notification would be sent to {user['email']} (currently disabled)")
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def get_webhook_response(self) -> str:
        """Generate TwiML response for webhook"""
        # Return empty TwiML response (no reply needed)
        return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'


# Initialize the processor
whatsapp_processor = WhatsAppSMSProcessor()