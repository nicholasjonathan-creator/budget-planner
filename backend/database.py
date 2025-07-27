from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get("DB_NAME", "budget_planner")]

# Collections
transactions_collection = db.transactions
budget_limits_collection = db.budget_limits
sms_collection = db.sms_transactions
categories_collection = db.categories
users_collection = db.users
notification_preferences_collection = db.notification_preferences
notification_logs_collection = db.notification_logs
analytics_cache_collection = db.analytics_cache
spending_alerts_collection = db.spending_alerts

# Initialize default categories
async def init_categories():
    """Initialize default categories in the database"""
    default_categories = [
        # Income categories
        {"id": 1, "name": "Salary", "color": "#a7f3d0", "type": "income"},
        {"id": 2, "name": "Freelance", "color": "#bfdbfe", "type": "income"},
        {"id": 3, "name": "Investment", "color": "#ddd6fe", "type": "income"},
        {"id": 4, "name": "Other Income", "color": "#fce7f3", "type": "income"},
        
        # Expense categories
        {"id": 5, "name": "Food & Dining", "color": "#fed7d7", "type": "expense"},
        {"id": 6, "name": "Transportation", "color": "#feebc8", "type": "expense"},
        {"id": 7, "name": "Entertainment", "color": "#c6f6d5", "type": "expense"},
        {"id": 8, "name": "Shopping", "color": "#bee3f8", "type": "expense"},
        {"id": 9, "name": "Bills & Utilities", "color": "#e9d8fd", "type": "expense"},
        {"id": 10, "name": "Healthcare", "color": "#fbb6ce", "type": "expense"},
        {"id": 11, "name": "Education", "color": "#fed7e2", "type": "expense"},
        {"id": 12, "name": "Other Expenses", "color": "#fef5e7", "type": "expense"}
    ]
    
    try:
        # Check if categories already exist
        existing_count = await categories_collection.count_documents({})
        if existing_count == 0:
            await categories_collection.insert_many(default_categories)
            print("Default categories initialized")
        else:
            print(f"Categories already exist: {existing_count} categories found")
    except Exception as e:
        print(f"Error initializing categories: {e}")

# Create indexes for better performance
async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Transaction indexes
        await transactions_collection.create_index("date")
        await transactions_collection.create_index("category_id")
        await transactions_collection.create_index("type")
        await transactions_collection.create_index("user_id")  # For user isolation
        await transactions_collection.create_index([("date", -1), ("type", 1)])
        await transactions_collection.create_index([("user_id", 1), ("date", -1)])
        
        # Budget limits indexes
        await budget_limits_collection.create_index([("month", 1), ("year", 1)])
        await budget_limits_collection.create_index("category_id")
        await budget_limits_collection.create_index("user_id")  # For user isolation
        await budget_limits_collection.create_index([("category_id", 1), ("month", 1), ("year", 1)], unique=True)
        await budget_limits_collection.create_index([("user_id", 1), ("category_id", 1), ("month", 1), ("year", 1)], unique=True)
        
        # SMS indexes
        await sms_collection.create_index("timestamp")
        await sms_collection.create_index("processed")
        await sms_collection.create_index("phone_number")
        await sms_collection.create_index("user_id")  # For user isolation
        
        # User indexes
        await users_collection.create_index("email", unique=True)
        await users_collection.create_index("username", unique=True)
        await users_collection.create_index("is_active")
        await users_collection.create_index("created_at")
        
        # Notification preferences indexes
        await notification_preferences_collection.create_index("user_id", unique=True)
        await notification_preferences_collection.create_index("created_at")
        
        # Notification logs indexes
        await notification_logs_collection.create_index("user_id")
        await notification_logs_collection.create_index("notification_type")
        await notification_logs_collection.create_index("sent_at")
        await notification_logs_collection.create_index("delivery_status")
        await notification_logs_collection.create_index([("user_id", 1), ("sent_at", -1)])
        
        print("Database indexes created successfully")
        
    except Exception as e:
        print(f"Error creating indexes: {e}")

# Initialize database on startup
async def init_db():
    """Initialize database with default data and indexes"""
    await init_categories()
    await create_indexes()
    print("Database initialized successfully")