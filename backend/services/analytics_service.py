from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
import math
import logging
from bson import ObjectId

from models.analytics import (
    SpendingTrend, FinancialHealthScore, SpendingPattern, BudgetRecommendation,
    SpendingAlert, AnalyticsSummary, TimeBasedAnalytics, CategoryInsights,
    AnomalyDetection, AnalyticsTimeframe, TrendDirection, AlertSeverity
)
from models.transaction import Transaction, TransactionType
from services.transaction_service import TransactionService
from database import db

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.transaction_service = TransactionService()
        self.analytics_collection = db.analytics_cache
        self.alerts_collection = db.spending_alerts
        
    async def get_spending_trends(self, user_id: str, timeframe: AnalyticsTimeframe, periods: int = 6) -> List[SpendingTrend]:
        """Analyze spending trends over multiple periods"""
        try:
            trends = []
            current_date = datetime.now()
            
            for i in range(periods):
                if timeframe == AnalyticsTimeframe.MONTHLY:
                    period_date = current_date.replace(day=1) - timedelta(days=i*30)
                    month = period_date.month - 1  # Convert to 0-indexed
                    year = period_date.year
                    period_label = f"{year}-{month+1:02d}"
                    
                    transactions = await self.transaction_service.get_transactions(month=month, year=year, user_id=user_id)
                    
                elif timeframe == AnalyticsTimeframe.WEEKLY:
                    period_date = current_date - timedelta(weeks=i)
                    week_start = period_date - timedelta(days=period_date.weekday())
                    week_end = week_start + timedelta(days=6)
                    period_label = f"Week {week_start.strftime('%U')}-{week_start.year}"
                    
                    # Get transactions for the week
                    all_transactions = await self._get_transactions_between_dates(user_id, week_start, week_end)
                    transactions = [t for t in all_transactions if t.type == TransactionType.EXPENSE]
                
                total_amount = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
                category_breakdown = self._get_category_breakdown(transactions)
                
                # Calculate trend direction compared to previous period
                trend_direction = TrendDirection.STABLE
                change_percentage = 0.0
                change_amount = 0.0
                
                if i < periods - 1:  # Not the last period
                    prev_total = trends[-1].total_amount if trends else 0
                    if prev_total > 0:
                        change_amount = total_amount - prev_total
                        change_percentage = (change_amount / prev_total) * 100
                        
                        if change_percentage > 10:
                            trend_direction = TrendDirection.INCREASING
                        elif change_percentage < -10:
                            trend_direction = TrendDirection.DECREASING
                
                trend = SpendingTrend(
                    timeframe=timeframe,
                    period=period_label,
                    total_amount=total_amount,
                    trend_direction=trend_direction,
                    change_percentage=change_percentage,
                    change_amount=change_amount,
                    category_breakdown=category_breakdown
                )
                trends.append(trend)
            
            return list(reversed(trends))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Error analyzing spending trends: {e}")
            return []
    
    async def calculate_financial_health_score(self, user_id: str) -> FinancialHealthScore:
        """Calculate comprehensive financial health score"""
        try:
            # Get last 3 months of data
            current_date = datetime.now()
            three_months_ago = current_date - timedelta(days=90)
            
            transactions = await self._get_transactions_between_dates(
                user_id, three_months_ago, current_date
            )
            
            income_transactions = [t for t in transactions if t.type == TransactionType.INCOME]
            expense_transactions = [t for t in transactions if t.type == TransactionType.EXPENSE]
            
            total_income = sum(t.amount for t in income_transactions)
            total_expenses = sum(t.amount for t in expense_transactions)
            
            # Calculate individual factors (0-1 scale)
            income_stability = await self._calculate_income_stability(income_transactions)
            expense_control = await self._calculate_expense_control(expense_transactions, total_income)
            budget_adherence = await self._calculate_budget_adherence(user_id, expense_transactions)
            
            # Calculate savings rate
            savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
            savings_score = min(max(savings_rate / 20, 0), 1)  # 20% savings = max score
            
            # Debt-to-income ratio (simplified - based on negative balance)
            debt_to_income_ratio = max((total_expenses - total_income) / total_income, 0) if total_income > 0 else 0
            debt_score = max(1 - debt_to_income_ratio, 0)
            
            # Weighted overall score
            score_components = {
                "income_stability": income_stability * 0.25,
                "expense_control": expense_control * 0.25,
                "budget_adherence": budget_adherence * 0.20,
                "savings_rate": savings_score * 0.20,
                "debt_management": debt_score * 0.10
            }
            
            overall_score = int(sum(score_components.values()) * 100)
            
            # Determine grade
            grade = self._score_to_grade(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(
                score_components, savings_rate, debt_to_income_ratio
            )
            
            return FinancialHealthScore(
                score=overall_score,
                grade=grade,
                income_stability=income_stability,
                expense_control=expense_control,
                budget_adherence=budget_adherence,
                savings_rate=savings_rate,
                debt_to_income_ratio=debt_to_income_ratio,
                recommendations=recommendations,
                factors_affecting_score=score_components
            )
            
        except Exception as e:
            logger.error(f"Error calculating financial health score: {e}")
            return FinancialHealthScore(
                score=0, grade="F", income_stability=0, expense_control=0,
                budget_adherence=0, savings_rate=0, debt_to_income_ratio=0,
                recommendations=["Unable to analyze financial health at this time"],
                factors_affecting_score={}
            )
    
    async def analyze_spending_patterns(self, user_id: str, timeframe: AnalyticsTimeframe = AnalyticsTimeframe.MONTHLY) -> List[SpendingPattern]:
        """Analyze detailed spending patterns by category"""
        try:
            # Get current and previous period data
            if timeframe == AnalyticsTimeframe.MONTHLY:
                current_month = datetime.now().month - 1
                current_year = datetime.now().year
                prev_month = (current_month - 1) % 12
                prev_year = current_year if current_month > 0 else current_year - 1
                
                current_transactions = await self.transaction_service.get_transactions(
                    month=current_month, year=current_year, user_id=user_id
                )
                prev_transactions = await self.transaction_service.get_transactions(
                    month=prev_month, year=prev_year, user_id=user_id
                )
            
            expense_transactions = [t for t in current_transactions if t.type == TransactionType.EXPENSE]
            prev_expense_transactions = [t for t in prev_transactions if t.type == TransactionType.EXPENSE]
            
            # Group by category
            category_data = defaultdict(lambda: {'transactions': [], 'prev_transactions': []})
            
            for transaction in expense_transactions:
                category_data[transaction.category_id]['transactions'].append(transaction)
            
            for transaction in prev_expense_transactions:
                category_data[transaction.category_id]['prev_transactions'].append(transaction)
            
            patterns = []
            total_expenses = sum(t.amount for t in expense_transactions)
            
            for category_id, data in category_data.items():
                transactions = data['transactions']
                prev_transactions = data['prev_transactions']
                
                if not transactions:
                    continue
                    
                total_amount = sum(t.amount for t in transactions)
                prev_total = sum(t.amount for t in prev_transactions)
                
                # Calculate trend
                trend_percentage = 0
                if prev_total > 0:
                    trend_percentage = ((total_amount - prev_total) / prev_total) * 100
                
                # Analyze peak spending times
                peak_times = self._analyze_peak_spending_times(transactions)
                
                pattern = SpendingPattern(
                    category_id=category_id,
                    category_name=f"Category {category_id}",  # Would fetch from categories collection
                    total_amount=total_amount,
                    transaction_count=len(transactions),
                    average_amount=total_amount / len(transactions),
                    percentage_of_total=(total_amount / total_expenses * 100) if total_expenses > 0 else 0,
                    trend_compared_to_previous=trend_percentage,
                    peak_spending_times=peak_times
                )
                patterns.append(pattern)
            
            return sorted(patterns, key=lambda x: x.total_amount, reverse=True)
            
        except Exception as e:
            logger.error(f"Error analyzing spending patterns: {e}")
            return []
    
    async def generate_budget_recommendations(self, user_id: str) -> List[BudgetRecommendation]:
        """Generate AI-powered budget recommendations"""
        try:
            # Get historical data for analysis
            three_months_ago = datetime.now() - timedelta(days=90)
            transactions = await self._get_transactions_between_dates(user_id, three_months_ago, datetime.now())
            expense_transactions = [t for t in transactions if t.type == TransactionType.EXPENSE]
            
            # Get current budget limits
            current_month = datetime.now().month - 1
            current_year = datetime.now().year
            budget_limits = await self.transaction_service.get_budget_limits(current_month, current_year)
            
            # Analyze spending by category
            category_spending = defaultdict(list)
            for transaction in expense_transactions:
                category_spending[transaction.category_id].append(transaction.amount)
            
            recommendations = []
            
            for category_id, amounts in category_spending.items():
                if not amounts:
                    continue
                    
                # Statistical analysis
                avg_monthly = sum(amounts) / 3  # 3 months of data
                median_amount = statistics.median(amounts)
                std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                # Find current budget
                current_budget = None
                for budget in budget_limits:
                    if budget.category_id == category_id:
                        current_budget = budget.limit
                        break
                
                # Calculate recommended budget
                # Use median + 1 std dev for more stable budgeting
                recommended_budget = median_amount + (std_dev * 0.5)
                
                # Generate reasoning
                reasoning = self._generate_budget_reasoning(
                    avg_monthly, median_amount, std_dev, current_budget, recommended_budget
                )
                
                # Calculate confidence score
                confidence = self._calculate_recommendation_confidence(amounts, std_dev, len(amounts))
                
                # Calculate potential savings
                potential_savings = max(0, (current_budget or recommended_budget * 1.2) - recommended_budget)
                
                recommendation = BudgetRecommendation(
                    category_id=category_id,
                    category_name=f"Category {category_id}",
                    current_budget=current_budget,
                    recommended_budget=recommended_budget,
                    reasoning=reasoning,
                    potential_savings=potential_savings,
                    confidence_score=confidence
                )
                recommendations.append(recommendation)
            
            return sorted(recommendations, key=lambda x: x.potential_savings, reverse=True)
            
        except Exception as e:
            logger.error(f"Error generating budget recommendations: {e}")
            return []
    
    async def detect_spending_anomalies(self, user_id: str) -> List[SpendingAlert]:
        """Detect unusual spending patterns and generate alerts"""
        try:
            alerts = []
            
            # Get recent transactions (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_transactions = await self._get_transactions_between_dates(user_id, thirty_days_ago, datetime.now())
            
            # Get historical data for comparison (90 days before that)
            historical_start = thirty_days_ago - timedelta(days=90)
            historical_transactions = await self._get_transactions_between_dates(user_id, historical_start, thirty_days_ago)
            
            # Detect large amount anomalies
            large_amount_alerts = await self._detect_large_amount_anomalies(recent_transactions, historical_transactions)
            alerts.extend(large_amount_alerts)
            
            # Detect frequency anomalies
            frequency_alerts = await self._detect_frequency_anomalies(recent_transactions, historical_transactions)
            alerts.extend(frequency_alerts)
            
            # Detect category spending spikes
            category_alerts = await self._detect_category_spikes(recent_transactions, historical_transactions)
            alerts.extend(category_alerts)
            
            # Save alerts to database
            for alert in alerts:
                if not alert.id:
                    alert_dict = alert.dict()
                    result = await self.alerts_collection.insert_one(alert_dict)
                    alert.id = str(result.inserted_id)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error detecting spending anomalies: {e}")
            return []
    
    # Helper methods
    async def _get_transactions_between_dates(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transactions between two dates"""
        try:
            query = {
                "user_id": user_id,
                "date": {"$gte": start_date, "$lt": end_date}
            }
            
            cursor = self.transaction_service.transactions_collection.find(query).sort("date", -1)
            transactions = []
            
            async for doc in cursor:
                doc['id'] = str(doc.pop('_id'))
                transactions.append(Transaction(**doc))
            
            return transactions
            
        except Exception as e:
            logger.error(f"Error getting transactions between dates: {e}")
            return []
    
    def _get_category_breakdown(self, transactions: List[Transaction]) -> Dict[str, float]:
        """Get spending breakdown by category"""
        breakdown = defaultdict(float)
        for transaction in transactions:
            if transaction.type == TransactionType.EXPENSE:
                breakdown[str(transaction.category_id)] += transaction.amount
        return dict(breakdown)
    
    async def _calculate_income_stability(self, income_transactions: List[Transaction]) -> float:
        """Calculate income stability score (0-1)"""
        if len(income_transactions) < 2:
            return 0.5  # Neutral score for insufficient data
        
        amounts = [t.amount for t in income_transactions]
        if len(amounts) < 2:
            return 0.5
            
        std_dev = statistics.stdev(amounts)
        mean_amount = statistics.mean(amounts)
        
        # Coefficient of variation (lower is more stable)
        cv = std_dev / mean_amount if mean_amount > 0 else 1
        
        # Convert to stability score (0-1, higher is better)
        stability = max(0, 1 - min(cv, 1))
        return stability
    
    async def _calculate_expense_control(self, expense_transactions: List[Transaction], total_income: float) -> float:
        """Calculate expense control score (0-1)"""
        if total_income <= 0:
            return 0
        
        total_expenses = sum(t.amount for t in expense_transactions)
        expense_ratio = total_expenses / total_income
        
        # Good expense control is spending less than 80% of income
        if expense_ratio <= 0.8:
            return 1.0
        elif expense_ratio <= 1.0:
            return 1.0 - ((expense_ratio - 0.8) / 0.2) * 0.5
        else:
            return max(0, 0.5 - ((expense_ratio - 1.0) * 0.5))
    
    async def _calculate_budget_adherence(self, user_id: str, expense_transactions: List[Transaction]) -> float:
        """Calculate budget adherence score (0-1)"""
        try:
            current_month = datetime.now().month - 1
            current_year = datetime.now().year
            budget_limits = await self.transaction_service.get_budget_limits(current_month, current_year)
            
            if not budget_limits:
                return 0.5  # Neutral score if no budgets set
            
            category_spending = defaultdict(float)
            for transaction in expense_transactions:
                category_spending[transaction.category_id] += transaction.amount
            
            adherence_scores = []
            for budget in budget_limits:
                spent = category_spending.get(budget.category_id, 0)
                if budget.limit > 0:
                    adherence = min(1.0, spent / budget.limit)
                    adherence_scores.append(1.0 - adherence if adherence <= 1.0 else 0)
            
            return statistics.mean(adherence_scores) if adherence_scores else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating budget adherence: {e}")
            return 0.5
    
    def _score_to_grade(self, score: int) -> str:
        """Convert numeric score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_health_recommendations(self, score_components: Dict[str, float], savings_rate: float, debt_ratio: float) -> List[str]:
        """Generate personalized financial health recommendations"""
        recommendations = []
        
        if score_components.get("income_stability", 0) < 0.7:
            recommendations.append("Consider diversifying income sources or building an emergency fund")
        
        if score_components.get("expense_control", 0) < 0.7:
            recommendations.append("Review and reduce unnecessary expenses to improve spending control")
        
        if score_components.get("budget_adherence", 0) < 0.7:
            recommendations.append("Create realistic budgets and track spending more closely")
        
        if savings_rate < 10:
            recommendations.append("Aim to save at least 10-20% of your income each month")
        
        if debt_ratio > 0.3:
            recommendations.append("Focus on reducing debt to improve your debt-to-income ratio")
        
        if not recommendations:
            recommendations.append("Great job! Continue maintaining your healthy financial habits")
        
        return recommendations
    
    def _analyze_peak_spending_times(self, transactions: List[Transaction]) -> List[str]:
        """Analyze when most spending occurs"""
        hour_spending = defaultdict(float)
        day_spending = defaultdict(float)
        
        for transaction in transactions:
            hour = transaction.date.hour
            day = transaction.date.strftime("%A")
            
            hour_spending[hour] += transaction.amount
            day_spending[day] += transaction.amount
        
        peak_times = []
        
        # Find peak hour
        if hour_spending:
            peak_hour = max(hour_spending, key=hour_spending.get)
            if 6 <= peak_hour <= 11:
                peak_times.append("Morning")
            elif 12 <= peak_hour <= 17:
                peak_times.append("Afternoon")
            elif 18 <= peak_hour <= 22:
                peak_times.append("Evening")
            else:
                peak_times.append("Night")
        
        # Find peak day
        if day_spending:
            peak_day = max(day_spending, key=day_spending.get)
            if peak_day in ["Saturday", "Sunday"]:
                peak_times.append("Weekend")
            else:
                peak_times.append("Weekday")
        
        return peak_times or ["No clear pattern"]
    
    def _generate_budget_reasoning(self, avg: float, median: float, std_dev: float, current: Optional[float], recommended: float) -> str:
        """Generate reasoning for budget recommendation"""
        reasoning_parts = []
        
        reasoning_parts.append(f"Based on 3 months of spending data (avg: ₹{avg:.2f}, median: ₹{median:.2f})")
        
        if std_dev > avg * 0.3:
            reasoning_parts.append("High spending variability suggests buffer needed")
        
        if current:
            if recommended < current:
                reasoning_parts.append(f"Recommended reduction of ₹{current - recommended:.2f} from current budget")
            elif recommended > current:
                reasoning_parts.append(f"Recommended increase of ₹{recommended - current:.2f} for realistic budgeting")
        else:
            reasoning_parts.append("No current budget set - recommendation based on historical patterns")
        
        return ". ".join(reasoning_parts)
    
    def _calculate_recommendation_confidence(self, amounts: List[float], std_dev: float, data_points: int) -> float:
        """Calculate confidence score for recommendation"""
        # More data points = higher confidence
        data_confidence = min(data_points / 10, 1.0)
        
        # Lower standard deviation = higher confidence
        avg_amount = sum(amounts) / len(amounts)
        variability_confidence = max(0, 1 - (std_dev / avg_amount)) if avg_amount > 0 else 0.5
        
        return (data_confidence + variability_confidence) / 2
    
    async def _detect_large_amount_anomalies(self, recent: List[Transaction], historical: List[Transaction]) -> List[SpendingAlert]:
        """Detect unusually large transactions"""
        alerts = []
        
        historical_expenses = [t for t in historical if t.type == TransactionType.EXPENSE]
        if len(historical_expenses) < 5:
            return alerts
        
        amounts = [t.amount for t in historical_expenses]
        mean_amount = statistics.mean(amounts)
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        threshold = mean_amount + (2 * std_dev)  # 2 standard deviations
        
        for transaction in recent:
            if transaction.type == TransactionType.EXPENSE and transaction.amount > threshold:
                alert = SpendingAlert(
                    user_id=transaction.user_id,
                    alert_type="unusual_spending",
                    severity=AlertSeverity.HIGH if transaction.amount > threshold * 1.5 else AlertSeverity.MEDIUM,
                    title="Unusually Large Transaction Detected",
                    description=f"Transaction of ₹{transaction.amount:.2f} is significantly above your typical spending of ₹{mean_amount:.2f}",
                    amount=transaction.amount,
                    category_id=transaction.category_id
                )
                alerts.append(alert)
        
        return alerts
    
    async def _detect_frequency_anomalies(self, recent: List[Transaction], historical: List[Transaction]) -> List[SpendingAlert]:
        """Detect unusual spending frequency"""
        alerts = []
        
        # Compare daily transaction counts
        recent_daily_count = len(recent) / 30  # Recent 30 days
        historical_daily_count = len(historical) / 90  # Historical 90 days
        
        if historical_daily_count > 0:
            frequency_increase = (recent_daily_count - historical_daily_count) / historical_daily_count
            
            if frequency_increase > 0.5:  # 50% increase in frequency
                alert = SpendingAlert(
                    user_id=recent[0].user_id if recent else "",
                    alert_type="frequency_alert",
                    severity=AlertSeverity.MEDIUM,
                    title="Increased Spending Frequency",
                    description=f"Your spending frequency has increased by {frequency_increase*100:.1f}% compared to previous periods",
                    amount=0
                )
                alerts.append(alert)
        
        return alerts
    
    async def _detect_category_spikes(self, recent: List[Transaction], historical: List[Transaction]) -> List[SpendingAlert]:
        """Detect category-specific spending spikes"""
        alerts = []
        
        # Group by category
        recent_by_category = defaultdict(float)
        historical_by_category = defaultdict(float)
        
        for t in recent:
            if t.type == TransactionType.EXPENSE:
                recent_by_category[t.category_id] += t.amount
        
        for t in historical:
            if t.type == TransactionType.EXPENSE:
                historical_by_category[t.category_id] += t.amount
        
        for category_id, recent_amount in recent_by_category.items():
            historical_amount = historical_by_category.get(category_id, 0)
            
            if historical_amount > 0:
                increase = (recent_amount - historical_amount) / historical_amount
                
                if increase > 0.5:  # 50% increase
                    alert = SpendingAlert(
                        user_id=recent[0].user_id if recent else "",
                        alert_type="category_spike",
                        severity=AlertSeverity.HIGH if increase > 1.0 else AlertSeverity.MEDIUM,
                        title=f"Category Spending Spike",
                        description=f"Spending in category {category_id} increased by {increase*100:.1f}% this month",
                        amount=recent_amount,
                        category_id=category_id
                    )
                    alerts.append(alert)
        
        return alerts