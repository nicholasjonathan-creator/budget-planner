from fastapi import FastAPI, APIRouter, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid
import re
from bson import ObjectId

# Import our models and services
from models.transaction import (
    Transaction, TransactionCreate, BudgetLimit, BudgetLimitCreate, 
    Category, TransactionType, SMSTransaction
)
from services.transaction_service import TransactionService
from services.sms_service import SMSService
from database import init_db, db

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Budget Planner API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize services
transaction_service = TransactionService()
sms_service = SMSService()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "Budget Planner API is running", "version": "1.0.0", "status": "healthy"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint for production monitoring"""
    try:
        # Check database connection
        await db.command("ping")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": "connected",
            "environment": os.environ.get("ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@api_router.get("/metrics")
async def get_metrics():
    """Basic metrics endpoint for monitoring"""
    try:
        # Get basic stats
        total_transactions = await db.transactions.count_documents({})
        total_sms = await db.sms_transactions.count_documents({})
        processed_sms = await db.sms_transactions.count_documents({"processed": True})
        
        return {
            "total_transactions": total_transactions,
            "total_sms": total_sms,
            "processed_sms": processed_sms,
            "success_rate": (processed_sms / total_sms * 100) if total_sms > 0 else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

# ==================== TRANSACTION ENDPOINTS ====================

@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    """Create a new transaction"""
    try:
        result = await transaction_service.create_transaction(transaction)
        # Update budget spent amounts
        await transaction_service.update_budget_spent(
            transaction.date.month if transaction.date else datetime.now().month,
            transaction.date.year if transaction.date else datetime.now().year
        )
        return result
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(month: Optional[int] = None, year: Optional[int] = None):
    """Get transactions by month/year"""
    try:
        return await transaction_service.get_transactions(month, year)
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    """Get a specific transaction"""
    try:
        transaction = await transaction_service.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/transactions/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, updates: dict = Body(...)):
    """Update a transaction"""
    try:
        result = await transaction_service.update_transaction(transaction_id, updates)
        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """Delete a transaction"""
    try:
        success = await transaction_service.delete_transaction(transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"message": "Transaction deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ENDPOINTS ====================

@api_router.get("/analytics/monthly-summary")
async def get_monthly_summary(month: int, year: int):
    """Get monthly summary of income, expenses, and balance"""
    try:
        return await transaction_service.get_monthly_summary(month, year)
    except Exception as e:
        logger.error(f"Error getting monthly summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/analytics/category-totals")
async def get_category_totals(month: int, year: int):
    """Get transaction totals by category"""
    try:
        return await transaction_service.get_category_totals(month, year)
    except Exception as e:
        logger.error(f"Error getting category totals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BUDGET LIMITS ENDPOINTS ====================

@api_router.post("/budget-limits", response_model=BudgetLimit)
async def create_budget_limit(budget_limit: BudgetLimitCreate):
    """Create or update a budget limit"""
    try:
        result = await transaction_service.create_budget_limit(budget_limit)
        # Update spent amounts
        await transaction_service.update_budget_spent(budget_limit.month, budget_limit.year)
        return result
    except Exception as e:
        logger.error(f"Error creating budget limit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/budget-limits", response_model=List[BudgetLimit])
async def get_budget_limits(month: int, year: int):
    """Get budget limits for a specific month/year"""
    try:
        return await transaction_service.get_budget_limits(month, year)
    except Exception as e:
        logger.error(f"Error getting budget limits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CATEGORIES ENDPOINTS ====================

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    """Get all categories"""
    try:
        cursor = db.categories.find({}).sort("id", 1)
        categories = []
        async for doc in cursor:
            doc.pop('_id', None)  # Remove MongoDB _id
            categories.append(Category(**doc))
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SMS ENDPOINTS ====================

@api_router.post("/sms/receive")
async def receive_sms(phone_number: str = Body(...), message: str = Body(...)):
    """Receive and process SMS transaction"""
    try:
        result = await sms_service.receive_sms(phone_number, message)
        return result
    except Exception as e:
        logger.error(f"Error receiving SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sms/unprocessed")
async def get_unprocessed_sms():
    """Get all unprocessed SMS messages"""
    try:
        return await sms_service.get_unprocessed_sms()
    except Exception as e:
        logger.error(f"Error getting unprocessed SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/sms/reprocess/{sms_id}")
async def reprocess_sms(sms_id: str):
    """Reprocess a specific SMS"""
    try:
        result = await sms_service.reprocess_sms(sms_id)
        return result
    except Exception as e:
        logger.error(f"Error reprocessing SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sms/stats")
async def get_sms_stats():
    """Get SMS processing statistics"""
    try:
        return await sms_service.get_sms_stats()
    except Exception as e:
        logger.error(f"Error getting SMS stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/sms/simulate")
async def simulate_bank_sms(bank_type: str = "hdfc"):
    """Simulate bank SMS for testing"""
    try:
        return await sms_service.simulate_bank_sms(bank_type)
    except Exception as e:
        logger.error(f"Error simulating SMS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sms/failed")
async def get_failed_sms():
    """Get all failed SMS messages for manual classification"""
    try:
        failed_sms = []
        async for doc in db.sms_transactions.find({"processed": False}):
            failed_sms.append({
                "id": str(doc["_id"]),
                "message": doc["message"],
                "phone_number": doc.get("phone_number", ""),
                "timestamp": doc.get("timestamp", ""),
                "reason": "Could not determine transaction type automatically"
            })
        
        return {"success": True, "failed_sms": failed_sms}
    except Exception as e:
        logger.error(f"Error fetching failed SMS: {e}")
        return {"success": False, "error": str(e)}

@api_router.post("/sms/manual-classify")
async def manual_classify_sms(request: dict):
    """Manually classify a failed SMS message"""
    try:
        sms_id = request.get("sms_id")
        transaction_type = request.get("transaction_type")  # 'debit' or 'credit'
        amount = request.get("amount")  # User-provided amount
        description = request.get("description", "")
        currency = request.get("currency", "INR")  # Default to INR
        
        if not sms_id or not transaction_type or not amount:
            return {"success": False, "error": "Missing required fields"}
        
        # Get the original SMS
        sms_doc = await db.sms_transactions.find_one({"_id": ObjectId(sms_id)})
        if not sms_doc:
            return {"success": False, "error": "SMS not found"}
        
        # Extract account number from SMS if possible
        sms_text = sms_doc.get("message", "")
        account_number = "Unknown"
        
        # Try to extract account number using regex
        account_patterns = [
            r'account\s*([a-zA-Z]*\d+)',
            r'a/c\s*([a-zA-Z]*\d+)',
            r'card\s*([a-zA-Z]*\d+)',
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                account_number = match.group(1)
                break
        
        # Create transaction
        transaction_data = {
            "id": str(uuid.uuid4()),
            "type": "expense" if transaction_type == "debit" else "income",
            "category_id": 12,  # Other/Miscellaneous category
            "amount": float(amount),
            "description": description or f"Manual classification - {transaction_type}",
            "date": datetime.now(),
            "source": "sms_manual",
            "merchant": "Manual Entry",
            "account_number": account_number,
            "currency": currency,  # Add currency field
            "raw_data": {
                "sms_text": sms_text,
                "phone_number": sms_doc.get("phone_number", ""),
                "manual_classification": True,
                "classified_as": transaction_type,
                "currency": currency,
                "parsed_at": datetime.now().isoformat()
            }
        }
        
        # Insert transaction
        result = await db.transactions.insert_one(transaction_data)
        
        # Mark SMS as processed
        await db.sms_transactions.update_one(
            {"_id": ObjectId(sms_id)},
            {"$set": {"processed": True, "manual_classification": True}}
        )
        
        logger.info(f"Manual classification completed for SMS {sms_id} with currency {currency}")
        
        return {
            "success": True,
            "message": "Transaction classified successfully",
            "transaction_id": str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error in manual classification: {e}")
        return {"success": False, "error": str(e)}

# Include the router in the main app
app.include_router(api_router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    logger.info("Budget Planner API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Budget Planner API shutting down")

# ==================== ADMIN ENDPOINTS
@app.post("/api/admin/clear-sms-data")
async def clear_sms_data():
    """Clear all SMS-related data for testing purposes"""
    try:
        # Clear failed SMS collection
        failed_sms_collection = db.failed_sms
        await failed_sms_collection.delete_many({})
        
        # Clear all SMS transactions (transactions with source = 'sms' or 'sms_manual')
        transactions_collection = db.transactions
        result = await transactions_collection.delete_many({
            "source": {"$in": ["sms", "sms_manual"]}
        })
        
        # Clear any other SMS-related collections if they exist
        # You can add more cleanup here if needed
        
        logger.info("All SMS data cleared successfully")
        return {
            "success": True,
            "message": "All SMS data cleared successfully",
            "deleted_transactions": result.deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing SMS data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/clear-all-data")
async def clear_all_data():
    """Clear ALL data for complete system reset"""
    try:
        # Clear all transactions
        transactions_collection = db.transactions
        trans_result = await transactions_collection.delete_many({})
        
        # Clear all budget limits
        budget_limits_collection = db.budget_limits
        budget_result = await budget_limits_collection.delete_many({})
        
        # Clear failed SMS collection
        failed_sms_collection = db.failed_sms
        failed_result = await failed_sms_collection.delete_many({})
        
        # Clear SMS transactions collection
        sms_transactions_collection = db.sms_transactions
        sms_result = await sms_transactions_collection.delete_many({})
        
        # Keep categories but you can clear them too if needed
        # categories_collection = db.categories
        # cat_result = await categories_collection.delete_many({})
        
        logger.info("ALL data cleared successfully")
        return {
            "success": True,
            "message": "ALL data cleared successfully - system completely reset",
            "deleted_transactions": trans_result.deleted_count,
            "deleted_budget_limits": budget_result.deleted_count,
            "deleted_failed_sms": failed_result.deleted_count,
            "deleted_sms_transactions": sms_result.deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
