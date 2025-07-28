from typing import List, Optional
from datetime import datetime
from models.transaction import SMSTransaction
from services.sms_parser import SMSTransactionParser
from database import db
import logging
import hashlib

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.parser = SMSTransactionParser()
        self.sms_collection = db.sms_transactions
        self.transactions_collection = db.transactions
        
    async def receive_sms(self, phone_number: str, message: str, user_id: str = None) -> dict:
        """Receive and process incoming SMS"""
        try:
            # Store raw SMS
            sms_record = SMSTransaction(
                phone_number=phone_number,
                message=message,
                timestamp=datetime.now(),
                processed=False,
                user_id=user_id  # Add user_id to SMS record
            )
            
            # Save to database
            result = await self.collection.insert_one(sms_record.dict())
            sms_id = str(result.inserted_id)
            
            # Parse and process transaction
            transaction = self.parser.parse_sms(message, phone_number)
            
            if transaction:
                # Add user_id to transaction
                transaction_dict = transaction.dict()
                if user_id:
                    transaction_dict['user_id'] = user_id
                    
                # Save transaction to database
                transaction_result = await db.transactions.insert_one(transaction_dict)
                transaction_id = str(transaction_result.inserted_id)
                
                # Update SMS record as processed
                await self.collection.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {"processed": True, "transaction_id": transaction_id}}
                )
                
                logger.info(f"SMS processed successfully: {transaction_id}")
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "sms_id": sms_id,
                    "message": "Transaction processed successfully"
                }
            else:
                logger.warning(f"Failed to parse SMS: {message}")
                return {
                    "success": False,
                    "sms_id": sms_id,
                    "message": "Could not parse transaction from SMS"
                }
                
        except Exception as e:
            logger.error(f"Error processing SMS: {e}")
            return {
                "success": False,
                "message": f"Error processing SMS: {str(e)}"
            }
    
    async def get_unprocessed_sms(self) -> List[SMSTransaction]:
        """Get all unprocessed SMS messages"""
        cursor = self.collection.find({"processed": False})
        return [SMSTransaction(**doc) async for doc in cursor]
    
    async def reprocess_sms(self, sms_id: str) -> dict:
        """Reprocess a specific SMS message"""
        try:
            sms_doc = await self.collection.find_one({"_id": sms_id})
            if not sms_doc:
                return {"success": False, "message": "SMS not found"}
            
            sms = SMSTransaction(**sms_doc)
            return await self.receive_sms(sms.phone_number, sms.message)
            
        except Exception as e:
            logger.error(f"Error reprocessing SMS: {e}")
            return {"success": False, "message": f"Error reprocessing SMS: {str(e)}"}
    
    async def get_sms_stats(self) -> dict:
        """Get SMS processing statistics"""
        try:
            total_sms = await self.collection.count_documents({})
            processed_sms = await self.collection.count_documents({"processed": True})
            failed_sms = await self.collection.count_documents({"processed": False})
            
            return {
                "total_sms": total_sms,
                "processed_sms": processed_sms,
                "failed_sms": failed_sms,
                "success_rate": (processed_sms / total_sms * 100) if total_sms > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting SMS stats: {e}")
            return {"error": str(e)}
    
    async def simulate_bank_sms(self, bank_type: str = "hdfc") -> dict:
        """Simulate common bank SMS formats for testing"""
        test_messages = {
            "hdfc": [
                "Dear Customer, Rs 250.00 debited from your account ending 1234 at STARBUCKS COFFEE on 25-Jul-25. Available balance: Rs 15750.00",
                "Rs 5000.00 credited to your account 5678 - SALARY PAYMENT on 01-Jul-25. Available balance: Rs 25000.00"
            ],
            "sbi": [
                "Your account 1234 has been debited by Rs 120.50 for transaction at DOMINOS PIZZA on 25/07/2025. Balance: Rs 8879.50",
                "Spent Rs 80.00 at METRO STATION via UPI on 25-Jul-25. A/c balance: Rs 4920.00"
            ],
            "icici": [
                "Your card ending 9876 used for Rs 45.00 at UBER TRIP on 25-Jul-25. Available balance: Rs 3455.00",
                "Rs 2000.00 transferred to your account from JOHN DOE on 25-Jul-25. Current balance: Rs 12455.00"
            ]
        }
        
        messages = test_messages.get(bank_type, test_messages["hdfc"])
        results = []
        
        for message in messages:
            result = await self.receive_sms(f"+91{bank_type}bank", message)
            results.append(result)
        
        return {
            "bank_type": bank_type,
            "messages_processed": len(messages),
            "results": results
        }