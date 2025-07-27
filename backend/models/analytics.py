from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AnalyticsTimeframe(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class TrendDirection(str, Enum):
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SpendingTrend(BaseModel):
    timeframe: AnalyticsTimeframe
    period: str  # e.g., "2025-01", "Week 23-2025"
    total_amount: float
    trend_direction: TrendDirection
    change_percentage: float
    change_amount: float
    category_breakdown: Dict[str, float]

class FinancialHealthScore(BaseModel):
    score: int  # 0-100
    grade: str  # A+, A, B+, B, C+, C, D, F
    income_stability: float  # 0-1
    expense_control: float  # 0-1 
    budget_adherence: float  # 0-1
    savings_rate: float  # percentage
    debt_to_income_ratio: float
    recommendations: List[str]
    factors_affecting_score: Dict[str, float]

class SpendingPattern(BaseModel):
    category_id: int
    category_name: str
    total_amount: float
    transaction_count: int
    average_amount: float
    percentage_of_total: float
    trend_compared_to_previous: float  # percentage change
    peak_spending_times: List[str]  # e.g., ["Weekend", "Evening"]
    
class BudgetRecommendation(BaseModel):
    category_id: int
    category_name: str
    current_budget: Optional[float]
    recommended_budget: float
    reasoning: str
    potential_savings: float
    confidence_score: float  # 0-1
    
class SpendingAlert(BaseModel):
    id: Optional[str] = None
    user_id: str
    alert_type: str  # "unusual_spending", "budget_exceeded", "trend_alert"
    severity: AlertSeverity
    title: str
    description: str
    amount: float
    category_id: Optional[int] = None
    date_detected: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = False
    action_taken: bool = False

class AnalyticsSummary(BaseModel):
    timeframe: AnalyticsTimeframe
    period: str
    total_income: float
    total_expenses: float 
    net_balance: float
    spending_trends: List[SpendingTrend]
    financial_health: FinancialHealthScore
    spending_patterns: List[SpendingPattern]
    budget_recommendations: List[BudgetRecommendation]
    alerts: List[SpendingAlert]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class TimeBasedAnalytics(BaseModel):
    hourly_distribution: Dict[int, float]  # hour (0-23) -> amount
    daily_distribution: Dict[str, float]   # day name -> amount
    weekly_distribution: Dict[int, float]  # week number -> amount
    monthly_distribution: Dict[int, float] # month (1-12) -> amount

class CategoryInsights(BaseModel):
    category_id: int
    category_name: str
    total_amount: float
    transaction_count: int
    average_transaction: float
    largest_transaction: float
    smallest_transaction: float
    most_frequent_merchant: Optional[str]
    spending_velocity: float  # transactions per day
    seasonal_patterns: Dict[str, float]  # season -> multiplier

class AnomalyDetection(BaseModel):
    transaction_id: str
    anomaly_type: str  # "amount", "frequency", "timing", "merchant"
    severity_score: float  # 0-1
    description: str
    expected_range: Dict[str, float]  # min, max, average
    actual_value: float
    detected_at: datetime = Field(default_factory=datetime.utcnow)