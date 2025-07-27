from typing import List, Optional
from datetime import datetime
from models.transaction import Transaction, TransactionCreate, BudgetLimit, BudgetLimitCreate
from database import db
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self):
        self.transactions_collection = db.transactions
        self.budget_limits_collection = db.budget_limits
        
    async def create_transaction(self, transaction: TransactionCreate, user_id: str = None) -> Transaction:
        """Create a new transaction"""
        try:
            transaction_dict = transaction.dict()
            if not transaction_dict.get('date'):
                transaction_dict['date'] = datetime.now()
            
            # Add user_id if provided
            if user_id:
                transaction_dict['user_id'] = user_id
            
            result = await self.transactions_collection.insert_one(transaction_dict)
            transaction_dict['id'] = str(result.inserted_id)
            
            logger.info(f"Transaction created: {transaction_dict['id']}")
            return Transaction(**transaction_dict)
            
        except Exception as e:
            logger.error(f"Error creating transaction: {e}")
            raise
    
    async def get_transactions(self, month: int = None, year: int = None, user_id: str = None) -> List[Transaction]:
        """Get transactions by month/year"""
        try:
            query = {}
            
            # Filter by user_id if provided
            if user_id:
                query['user_id'] = user_id
                
            if month is not None and year is not None:
                # Frontend sends 0-indexed months (0=January, 6=July)
                # Convert to 1-indexed for datetime (1=January, 7=July)
                actual_month = month + 1
                
                start_date = datetime(year, actual_month, 1)
                if actual_month == 12:
                    end_date = datetime(year + 1, 1, 1)
                else:
                    end_date = datetime(year, actual_month + 1, 1)
                
                query['date'] = {'$gte': start_date, '$lt': end_date}
            
            cursor = self.transactions_collection.find(query).sort("date", -1)
            transactions = []
            
            async for doc in cursor:
                doc['id'] = str(doc.pop('_id'))
                transactions.append(Transaction(**doc))
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting transactions: {e}")
            raise
    
    async def get_transaction_by_id(self, transaction_id: str, user_id: str = None) -> Optional[Transaction]:
        """Get a specific transaction by ID with user isolation"""
        try:
            query = {"_id": ObjectId(transaction_id)}
            if user_id:
                query["user_id"] = user_id
                
            doc = await self.transactions_collection.find_one(query)
            if doc:
                doc['id'] = str(doc.pop('_id'))
                return Transaction(**doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting transaction: {e}")
            return None
    
    async def update_transaction(self, transaction_id: str, updates: dict, user_id: str = None) -> Optional[Transaction]:
        """Update a transaction with user isolation"""
        try:
            # Build query with user isolation
            query = {"_id": ObjectId(transaction_id)}
            if user_id:
                query["user_id"] = user_id
            
            result = await self.transactions_collection.update_one(
                query,
                {"$set": updates}
            )
            
            if result.modified_count:
                updated_transaction = await self.get_transaction_by_id(transaction_id)
                
                # Update budget spent amounts if transaction was updated
                if updated_transaction and user_id:
                    # Convert date to month/year for budget update
                    month = updated_transaction.date.month - 1  # Convert to 0-indexed
                    year = updated_transaction.date.year
                    await self.update_budget_spent(month, year, user_id)
                
                return updated_transaction
            return None
            
        except Exception as e:
            logger.error(f"Error updating transaction: {e}")
            return None
    
    async def delete_transaction(self, transaction_id: str, user_id: str = None) -> bool:
        """Delete a transaction with user isolation"""
        try:
            # Build query with user isolation
            query = {"_id": ObjectId(transaction_id)}
            if user_id:
                query["user_id"] = user_id
            
            # Get transaction before deletion to update budgets
            transaction = await self.get_transaction_by_id(transaction_id)
            
            result = await self.transactions_collection.delete_one(query)
            success = result.deleted_count > 0
            
            # Update budget spent amounts if transaction was deleted
            if success and transaction and user_id:
                # Convert date to month/year for budget update
                month = transaction.date.month - 1  # Convert to 0-indexed
                year = transaction.date.year
                await self.update_budget_spent(month, year, user_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting transaction: {e}")
            return False
    
    async def get_category_totals(self, month: int, year: int, user_id: str = None) -> dict:
        """Get transaction totals by category for a specific month/year"""
        try:
            # Frontend sends 0-indexed months, convert to 1-indexed
            actual_month = month + 1
            
            start_date = datetime(year, actual_month, 1)
            if actual_month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, actual_month + 1, 1)
            
            match_query = {
                "date": {"$gte": start_date, "$lt": end_date}
            }
            
            # Filter by user_id if provided
            if user_id:
                match_query["user_id"] = user_id
            
            pipeline = [
                {
                    "$match": match_query
                },
                {
                    "$group": {
                        "_id": {
                            "category_id": "$category_id",
                            "type": "$type"
                        },
                        "total": {"$sum": "$amount"}
                    }
                }
            ]
            
            cursor = self.transactions_collection.aggregate(pipeline)
            results = {}
            
            async for doc in cursor:
                category_id = doc['_id']['category_id']
                transaction_type = doc['_id']['type']
                total = doc['total']
                
                if category_id not in results:
                    results[category_id] = {"income": 0, "expense": 0}
                
                results[category_id][transaction_type] = total
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting category totals: {e}")
            return {}
    
    async def get_monthly_summary(self, month: int, year: int, user_id: str = None) -> dict:
        """Get monthly summary of income, expenses, and balance"""
        try:
            # Frontend sends 0-indexed months, convert to 1-indexed
            actual_month = month + 1
            
            start_date = datetime(year, actual_month, 1)
            if actual_month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, actual_month + 1, 1)
            
            match_query = {
                "date": {"$gte": start_date, "$lt": end_date}
            }
            
            # Filter by user_id if provided
            if user_id:
                match_query["user_id"] = user_id
            
            pipeline = [
                {
                    "$match": match_query
                },
                {
                    "$group": {
                        "_id": "$type",
                        "total": {"$sum": "$amount"}
                    }
                }
            ]
            
            cursor = self.transactions_collection.aggregate(pipeline)
            summary = {"income": 0, "expense": 0, "balance": 0}
            
            async for doc in cursor:
                summary[doc['_id']] = doc['total']
            
            summary['balance'] = summary['income'] - summary['expense']
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting monthly summary: {e}")
            return {"income": 0, "expense": 0, "balance": 0}
    
    # Budget Limits Management
    async def create_budget_limit(self, budget_limit: BudgetLimitCreate, user_id: str = None) -> BudgetLimit:
        """Create or update a budget limit"""
        try:
            budget_dict = budget_limit.dict()
            
            # Add user_id if provided
            if user_id:
                budget_dict['user_id'] = user_id
            
            # Frontend sends 0-indexed months, but we store 1-indexed
            actual_month = budget_dict['month'] + 1
            budget_dict['month'] = actual_month
            
            # Check if limit already exists for this category/month/year/user
            query = {
                "category_id": budget_dict['category_id'],
                "month": actual_month,
                "year": budget_dict['year']
            }
            if user_id:
                query['user_id'] = user_id
                
            existing = await self.budget_limits_collection.find_one(query)
            
            if existing:
                # Update existing limit
                await self.budget_limits_collection.update_one(
                    {"_id": existing['_id']},
                    {"$set": {"limit": budget_dict['limit']}}
                )
                existing['limit'] = budget_dict['limit']
                existing['id'] = str(existing.pop('_id'))
                return BudgetLimit(**existing)
            else:
                # Create new limit
                result = await self.budget_limits_collection.insert_one(budget_dict)
                budget_dict['id'] = str(result.inserted_id)
                return BudgetLimit(**budget_dict)
                
        except Exception as e:
            logger.error(f"Error creating budget limit: {e}")
            raise
    
    async def get_budget_limits(self, month: int, year: int, user_id: str = None) -> List[BudgetLimit]:
        """Get budget limits for a specific month/year"""
        try:
            # Frontend sends 0-indexed months, convert to 1-indexed for storage
            actual_month = month + 1
            
            query = {
                "month": actual_month,
                "year": year
            }
            # Filter by user_id if provided
            if user_id:
                query['user_id'] = user_id
            
            cursor = self.budget_limits_collection.find(query)
            
            budget_limits = []
            async for doc in cursor:
                doc['id'] = str(doc.pop('_id'))
                budget_limits.append(BudgetLimit(**doc))
            
            return budget_limits
            
        except Exception as e:
            logger.error(f"Error getting budget limits: {e}")
            return []
    
    async def update_budget_spent(self, month: int, year: int, user_id: str = None):
        """Update spent amounts for all budget limits"""
        try:
            # Frontend sends 0-indexed months, convert to 1-indexed
            actual_month = month + 1
            
            category_totals = await self.get_category_totals(month, year, user_id)
            
            budget_limits = await self.get_budget_limits(month, year, user_id)
            
            for budget_limit in budget_limits:
                spent = category_totals.get(budget_limit.category_id, {}).get('expense', 0)
                
                await self.budget_limits_collection.update_one(
                    {"_id": ObjectId(budget_limit.id)},
                    {"$set": {"spent": spent}}
                )
            
            logger.info(f"Updated budget spent amounts for {actual_month}/{year} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating budget spent: {e}")