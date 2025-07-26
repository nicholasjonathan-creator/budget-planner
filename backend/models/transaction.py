from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionSource(str, Enum):
    MANUAL = "manual"
    SMS = "sms"
    SMS_MANUAL = "sms_manual"
    EMAIL = "email"

class Category(BaseModel):
    id: int
    name: str
    color: str
    type: TransactionType

class Transaction(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None  # Associate transaction with user
    type: TransactionType
    category_id: int
    amount: float
    description: str
    date: datetime
    source: TransactionSource = TransactionSource.MANUAL
    raw_data: Optional[dict] = None
    merchant: Optional[str] = None
    account_number: Optional[str] = None
    balance: Optional[float] = None
    currency: Optional[str] = "INR"  # Add currency field with INR default

class TransactionCreate(BaseModel):
    type: TransactionType
    category_id: int
    amount: float
    description: str
    date: Optional[datetime] = None
    source: TransactionSource = TransactionSource.MANUAL
    merchant: Optional[str] = None

class BudgetLimit(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None  # Associate budget limit with user
    category_id: int
    limit: float
    spent: float = 0.0
    month: int
    year: int

class BudgetLimitCreate(BaseModel):
    category_id: int
    limit: float
    month: int
    year: int

class SMSTransaction(BaseModel):
    phone_number: str
    message: str
    timestamp: datetime
    processed: bool = False
    transaction_id: Optional[str] = None