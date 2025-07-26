from fastapi import FastAPI, APIRouter, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

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
