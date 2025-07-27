from typing import List, Dict, Any
from datetime import datetime
from services.email_service import EmailService
from models.user import User
from models.notification import NotificationType
from models.analytics import SpendingAlert, FinancialHealthScore, BudgetRecommendation

class EmailTemplates(EmailService):
    """Email templates for various notification types"""
    
    async def send_welcome_email(self, user: User) -> bool:
        """Send welcome email to new users"""
        content = f"""
        <h2>Welcome to Budget Planner! 🎉</h2>
        <p>We're excited to have you on board. Budget Planner will help you track your income, expenses, and stay within budget with ease.</p>
        
        <div class="highlight">
            <h3>🚀 Get Started:</h3>
            <ul>
                <li><strong>Add Transactions:</strong> Manually add your income and expenses</li>
                <li><strong>SMS Integration:</strong> Forward bank SMS to automatically track transactions</li>
                <li><strong>Set Budgets:</strong> Create monthly budget limits for different categories</li>
                <li><strong>View Analytics:</strong> Get insights into your spending patterns</li>
            </ul>
        </div>
        
        <a href="#" class="button">Start Managing Your Budget</a>
        
        <p>If you have any questions, feel free to reach out to us. Happy budgeting!</p>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject="Welcome to Budget Planner - Start Your Financial Journey! 🏦",
            html_content=self._get_base_template(
                "Welcome to Budget Planner",
                content,
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.ACCOUNT_UPDATES
        )
    
    async def send_budget_alert(
        self, 
        user: User, 
        category_name: str, 
        spent_amount: float, 
        budget_limit: float, 
        percentage_spent: float
    ) -> bool:
        """Send budget limit alert email"""
        status_class = "warning" if percentage_spent >= 100 else "warning"
        status_text = "Budget Exceeded!" if percentage_spent >= 100 else "Budget Alert!"
        
        content = f"""
        <h2 class="{status_class}">⚠️ {status_text}</h2>
        <p>Your spending in the <strong>{category_name}</strong> category has reached a significant level.</p>
        
        <div class="highlight">
            <table>
                <tr>
                    <td><strong>Category:</strong></td>
                    <td>{category_name}</td>
                </tr>
                <tr>
                    <td><strong>Amount Spent:</strong></td>
                    <td class="amount">₹{spent_amount:,.2f}</td>
                </tr>
                <tr>
                    <td><strong>Budget Limit:</strong></td>
                    <td>₹{budget_limit:,.2f}</td>
                </tr>
                <tr>
                    <td><strong>Percentage Used:</strong></td>
                    <td class="{status_class}">{percentage_spent:.1f}%</td>
                </tr>
                <tr>
                    <td><strong>Remaining:</strong></td>
                    <td>₹{max(0, budget_limit - spent_amount):,.2f}</td>
                </tr>
            </table>
        </div>
        
        <p>Consider reviewing your spending in this category to stay within your budget goals.</p>
        
        <a href="#" class="button">View Budget Details</a>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject=f"Budget Alert: {category_name} - {percentage_spent:.0f}% Used 📊",
            html_content=self._get_base_template(
                "Budget Alert",
                content,
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.BUDGET_ALERT
        )
    
    async def send_monthly_summary(
        self, 
        user: User,
        month: int,
        year: int,
        total_income: float,
        total_expenses: float,
        balance: float,
        top_categories: List[Dict[str, Any]],
        transaction_count: int
    ) -> bool:
        """Send monthly financial summary email"""
        month_names = [
            "", "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month_name = month_names[month]
        
        balance_class = "success" if balance >= 0 else "warning"
        balance_text = "Surplus" if balance >= 0 else "Deficit"
        
        # Top categories HTML
        categories_html = ""
        if top_categories:
            categories_html = "<h3>Top Spending Categories:</h3><table><tr><th>Category</th><th>Amount</th><th>Transactions</th></tr>"
            for category in top_categories[:5]:  # Top 5 categories
                categories_html += f"""
                <tr>
                    <td>{category['name']}</td>
                    <td>₹{category['amount']:,.2f}</td>
                    <td>{category['count']}</td>
                </tr>
                """
            categories_html += "</table>"
        
        content = f"""
        <h2>📊 Monthly Summary - {month_name} {year}</h2>
        <p>Here's your financial overview for {month_name} {year}:</p>
        
        <div class="highlight">
            <table>
                <tr>
                    <td><strong>Total Income:</strong></td>
                    <td class="success amount">₹{total_income:,.2f}</td>
                </tr>
                <tr>
                    <td><strong>Total Expenses:</strong></td>
                    <td class="warning amount">₹{total_expenses:,.2f}</td>
                </tr>
                <tr>
                    <td><strong>Net {balance_text}:</strong></td>
                    <td class="{balance_class} amount">₹{abs(balance):,.2f}</td>
                </tr>
                <tr>
                    <td><strong>Total Transactions:</strong></td>
                    <td>{transaction_count}</td>
                </tr>
            </table>
        </div>
        
        {categories_html}
        
        <p>{"Great job maintaining a positive balance!" if balance >= 0 else "Consider reviewing your expenses to improve your financial position."}</p>
        
        <a href="#" class="button">View Detailed Report</a>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject=f"Monthly Summary: {month_name} {year} - ₹{balance:,.2f} {balance_text} 💰",
            html_content=self._get_base_template(
                f"Monthly Summary - {month_name} {year}",
                content,
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.MONTHLY_SUMMARY
        )
    
    async def send_transaction_confirmation(
        self, 
        user: User,
        transaction_type: str,
        amount: float,
        category: str,
        description: str,
        date: datetime
    ) -> bool:
        """Send transaction confirmation email"""
        type_icon = "💰" if transaction_type == "income" else "💸"
        type_class = "success" if transaction_type == "income" else "warning"
        
        content = f"""
        <h2>{type_icon} Transaction Confirmed</h2>
        <p>A new {transaction_type} transaction has been added to your account:</p>
        
        <div class="highlight">
            <table>
                <tr>
                    <td><strong>Type:</strong></td>
                    <td class="{type_class}">{transaction_type.title()}</td>
                </tr>
                <tr>
                    <td><strong>Amount:</strong></td>
                    <td class="amount">₹{amount:,.2f}</td>
                </tr>
                <tr>
                    <td><strong>Category:</strong></td>
                    <td>{category}</td>
                </tr>
                <tr>
                    <td><strong>Description:</strong></td>
                    <td>{description}</td>
                </tr>
                <tr>
                    <td><strong>Date:</strong></td>
                    <td>{date.strftime('%d %B %Y at %I:%M %p')}</td>
                </tr>
            </table>
        </div>
        
        <p>This transaction has been automatically categorized and added to your budget tracking.</p>
        
        <a href="#" class="button">View Transaction Details</a>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject=f"Transaction Confirmed: ₹{amount:,.2f} {transaction_type.title()} 📝",
            html_content=self._get_base_template(
                "Transaction Confirmation",
                content,
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.TRANSACTION_CONFIRMATION
        )
    
    async def send_sms_processing_summary(
        self, 
        user: User,
        processed_count: int,
        successful_count: int,
        failed_count: int,
        date_range: str
    ) -> bool:
        """Send SMS processing summary email"""
        success_rate = (successful_count / processed_count * 100) if processed_count > 0 else 0
        
        content = f"""
        <h2>📱 SMS Processing Summary</h2>
        <p>Here's your SMS transaction processing summary for {date_range}:</p>
        
        <div class="highlight">
            <table>
                <tr>
                    <td><strong>Total SMS Processed:</strong></td>
                    <td>{processed_count}</td>
                </tr>
                <tr>
                    <td><strong>Successfully Parsed:</strong></td>
                    <td class="success">{successful_count}</td>
                </tr>
                <tr>
                    <td><strong>Failed to Parse:</strong></td>
                    <td class="warning">{failed_count}</td>
                </tr>
                <tr>
                    <td><strong>Success Rate:</strong></td>
                    <td>{success_rate:.1f}%</td>
                </tr>
            </table>
        </div>
        
        {f'<p class="warning">You have {failed_count} SMS messages that require manual classification.</p>' if failed_count > 0 else ''}
        
        <p>Keep forwarding your bank SMS to automatically track transactions!</p>
        
        <a href="#" class="button">Review SMS Processing</a>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject=f"SMS Processing Summary: {successful_count}/{processed_count} Processed 📊",
            html_content=self._get_base_template(
                "SMS Processing Summary",
                content,
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.SMS_PROCESSING
        )
    
    # ==================== ANALYTICS EMAIL TEMPLATES ====================
    
    async def send_spending_alert_email(
        self, 
        user: User, 
        alert: SpendingAlert
    ) -> bool:
        """Send spending alert email for unusual spending patterns"""
        severity_config = {
            "critical": {"color": "critical", "emoji": "🚨", "priority": "CRITICAL"},
            "high": {"color": "warning", "emoji": "⚠️", "priority": "HIGH"},
            "medium": {"color": "warning", "emoji": "📊", "priority": "MEDIUM"},
            "low": {"color": "info", "emoji": "💡", "priority": "LOW"}
        }
        
        config = severity_config.get(alert.severity, severity_config["medium"])
        
        # Format alert type for display
        alert_type_display = {
            "unusual_spending": "Unusual Spending Pattern",
            "budget_exceeded": "Budget Limit Exceeded", 
            "trend_alert": "Spending Trend Alert",
            "frequency_alert": "Spending Frequency Alert",
            "category_spike": "Category Spending Spike"
        }.get(alert.alert_type, alert.alert_type.replace("_", " ").title())
        
        content = f"""
        <h2 class="{config['color']}">{config['emoji']} {config['priority']} ALERT: {alert_type_display}</h2>
        <p><strong>{alert.title}</strong></p>
        <p>{alert.description}</p>
        
        <div class="highlight">
            <table>
                <tr>
                    <td><strong>Alert Type:</strong></td>
                    <td>{alert_type_display}</td>
                </tr>
                <tr>
                    <td><strong>Severity:</strong></td>
                    <td class="{config['color']}">{alert.severity.upper()}</td>
                </tr>
                {f'''<tr>
                    <td><strong>Amount:</strong></td>
                    <td class="amount">₹{alert.amount:,.2f}</td>
                </tr>''' if alert.amount > 0 else ''}
                {f'''<tr>
                    <td><strong>Category:</strong></td>
                    <td>Category {alert.category_id}</td>
                </tr>''' if alert.category_id else ''}
                <tr>
                    <td><strong>Detected On:</strong></td>
                    <td>{alert.date_detected.strftime('%d %B %Y at %I:%M %p')}</td>
                </tr>
            </table>
        </div>
        
        <div class="action-section">
            <h3>💡 Recommended Actions:</h3>
            <ul>
                <li>Review your recent transactions for this pattern</li>
                <li>Consider adjusting your budget limits if needed</li>
                <li>Set up category-specific spending limits</li>
                <li>Enable more frequent spending alerts</li>
            </ul>
        </div>
        
        <a href="#" class="button">View Analytics Dashboard</a>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject=f"{config['priority']} Alert: {alert.title} {config['emoji']}",
            html_content=self._get_base_template(
                f"{config['priority']} Spending Alert",
                content,
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.BUDGET_ALERT
        )
    
    async def send_financial_health_report(
        self, 
        user: User, 
        health_score: FinancialHealthScore,
        previous_score: int = None
    ) -> bool:
        """Send monthly financial health report email"""
        score_trend = ""
        if previous_score:
            diff = health_score.score - previous_score
            if diff > 0:
                score_trend = f"<span class='success'>↗️ +{diff} points from last month</span>"
            elif diff < 0:
                score_trend = f"<span class='warning'>↘️ {diff} points from last month</span>"
            else:
                score_trend = "<span class='info'>→ No change from last month</span>"
        
        grade_color = {
            "A+": "success", "A": "success", "B+": "success", "B": "info",
            "C+": "info", "C": "warning", "D": "warning", "F": "critical"
        }.get(health_score.grade, "info")
        
        content = f"""
        <h2>📊 Your Monthly Financial Health Report</h2>
        <p>Here's how your financial health looks this month:</p>
        
        <div class="score-display">
            <div class="score-circle">
                <h1 class="{grade_color}">{health_score.score}/100</h1>
                <h2 class="{grade_color}">Grade: {health_score.grade}</h2>
                {f'<p>{score_trend}</p>' if score_trend else ''}
            </div>
        </div>
        
        <div class="highlight">
            <h3>📈 Health Factors Breakdown:</h3>
            <table>
                <tr>
                    <td><strong>Income Stability:</strong></td>
                    <td>{health_score.income_stability * 100:.0f}%</td>
                </tr>
                <tr>
                    <td><strong>Expense Control:</strong></td>
                    <td>{health_score.expense_control * 100:.0f}%</td>
                </tr>
                <tr>
                    <td><strong>Budget Adherence:</strong></td>
                    <td>{health_score.budget_adherence * 100:.0f}%</td>
                </tr>
                <tr>
                    <td><strong>Savings Rate:</strong></td>
                    <td class="{'success' if health_score.savings_rate > 10 else 'warning'}">{health_score.savings_rate:.1f}%</td>
                </tr>
                <tr>
                    <td><strong>Debt-to-Income Ratio:</strong></td>
                    <td class="{'success' if health_score.debt_to_income_ratio < 0.3 else 'warning'}">{health_score.debt_to_income_ratio * 100:.1f}%</td>
                </tr>
            </table>
        </div>
        
        {f'''<div class="recommendations">
            <h3>💡 Personalized Recommendations:</h3>
            <ul>
                {chr(10).join([f"<li>{rec}</li>" for rec in health_score.recommendations])}
            </ul>
        </div>''' if health_score.recommendations else ''}
        
        <p>Keep tracking your expenses and follow our recommendations to improve your financial health!</p>
        
        <a href="#" class="button">View Detailed Analytics</a>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject=f"Financial Health Report: {health_score.score}/100 ({health_score.grade}) 📊",
            html_content=self._get_base_template(
                "Monthly Financial Health Report",
                content,
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.MONTHLY_SUMMARY
        )
    
    async def send_budget_recommendations_email(
        self, 
        user: User, 
        recommendations: List[BudgetRecommendation]
    ) -> bool:
        """Send AI-powered budget recommendations email"""
        if not recommendations:
            return False
            
        total_potential_savings = sum(rec.potential_savings for rec in recommendations)
        high_confidence_recs = [rec for rec in recommendations if rec.confidence_score > 0.7]
        
        recommendations_html = ""
        for rec in recommendations[:5]:  # Limit to top 5 recommendations
            confidence_color = "success" if rec.confidence_score > 0.8 else "warning" if rec.confidence_score > 0.6 else "info"
            current_budget_text = f"₹{rec.current_budget:,.2f}" if rec.current_budget else "Not set"
            
            recommendations_html += f"""
            <div class="recommendation-item">
                <h4>Category {rec.category_id}</h4>
                <div class="rec-details">
                    <table>
                        <tr>
                            <td><strong>Current Budget:</strong></td>
                            <td>{current_budget_text}</td>
                        </tr>
                        <tr>
                            <td><strong>Recommended:</strong></td>
                            <td class="success">₹{rec.recommended_budget:,.2f}</td>
                        </tr>
                        <tr>
                            <td><strong>Potential Savings:</strong></td>
                            <td class="success">₹{rec.potential_savings:,.2f}</td>
                        </tr>
                        <tr>
                            <td><strong>Confidence:</strong></td>
                            <td class="{confidence_color}">{rec.confidence_score * 100:.0f}%</td>
                        </tr>
                    </table>
                    <p class="reasoning">{rec.reasoning}</p>
                </div>
            </div>
            """
        
        content = f"""
        <h2>🎯 AI-Powered Budget Recommendations</h2>
        <p>Based on your spending patterns, we've identified opportunities to optimize your budget:</p>
        
        <div class="summary-stats">
            <div class="stat-item">
                <h3 class="success">₹{total_potential_savings:,.2f}</h3>
                <p>Total Potential Monthly Savings</p>
            </div>
            <div class="stat-item">
                <h3 class="info">{len(recommendations)}</h3>
                <p>Budget Recommendations</p>
            </div>
            <div class="stat-item">
                <h3 class="success">{len(high_confidence_recs)}</h3>
                <p>High Confidence Suggestions</p>
            </div>
        </div>
        
        <div class="recommendations-list">
            <h3>📋 Top Recommendations:</h3>
            {recommendations_html}
        </div>
        
        <div class="action-section">
            <h3>🚀 Next Steps:</h3>
            <ul>
                <li>Review each recommendation carefully</li>
                <li>Start with high-confidence suggestions</li>
                <li>Adjust budgets gradually over 2-3 months</li>
                <li>Monitor your spending after changes</li>
            </ul>
        </div>
        
        <a href="#" class="button">Apply Recommendations</a>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject=f"Budget Optimization: Save ₹{total_potential_savings:,.0f}/month 🎯",
            html_content=self._get_base_template(
                "AI Budget Recommendations",
                content,  
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.BUDGET_ALERT
        )
    
    async def send_weekly_analytics_digest(
        self, 
        user: User,
        week_summary: Dict[str, Any]
    ) -> bool:
        """Send weekly analytics digest email"""
        total_spent = week_summary.get('total_spent', 0)
        total_income = week_summary.get('total_income', 0)
        net_balance = total_income - total_spent
        transaction_count = week_summary.get('transaction_count', 0)
        top_categories = week_summary.get('top_categories', [])
        alerts_count = week_summary.get('alerts_count', 0)
        
        balance_color = "success" if net_balance >= 0 else "warning"
        week_range = week_summary.get('week_range', 'This Week')
        
        top_categories_html = ""
        for i, cat in enumerate(top_categories[:3], 1):
            top_categories_html += f"""
            <tr>
                <td>{i}. {cat.get('name', f'Category {cat.get("id")}')}:</td>
                <td class="amount">₹{cat.get('amount', 0):,.2f}</td>
            </tr>
            """
        
        content = f"""
        <h2>📈 Weekly Financial Digest</h2>
        <p>Here's your financial summary for {week_range}:</p>
        
        <div class="weekly-stats">
            <div class="stat-grid">
                <div class="stat-item success">
                    <h3>₹{total_income:,.2f}</h3>
                    <p>Total Income</p>
                </div>
                <div class="stat-item warning">
                    <h3>₹{total_spent:,.2f}</h3>
                    <p>Total Spent</p>
                </div>
                <div class="stat-item {balance_color}">
                    <h3>₹{net_balance:,.2f}</h3>
                    <p>Net Balance</p>
                </div>
                <div class="stat-item info">
                    <h3>{transaction_count}</h3>
                    <p>Transactions</p>
                </div>
            </div>
        </div>
        
        {f'''<div class="highlight">
            <h3>🏆 Top Spending Categories:</h3>
            <table>
                {top_categories_html}
            </table>
        </div>''' if top_categories else ''}
        
        {f'''<div class="alerts-section">
            <h3 class="warning">⚠️ Spending Alerts: {alerts_count}</h3>
            <p>You received {alerts_count} spending alert{'s' if alerts_count != 1 else ''} this week. Review your analytics dashboard for details.</p>
        </div>''' if alerts_count > 0 else ''}
        
        <div class="action-section">
            <p>💡 <strong>Tip:</strong> Regular monitoring helps maintain healthy spending habits. Keep up the great work!</p>
        </div>
        
        <a href="#" class="button">View Full Analytics</a>
        """
        
        return await self.send_email(
            to_email=user.email,
            subject=f"Weekly Digest: ₹{total_spent:,.0f} spent, {transaction_count} transactions 📊",
            html_content=self._get_base_template(
                "Weekly Financial Digest",
                content,
                user.username
            ),
            user_id=user.id,
            notification_type=NotificationType.WEEKLY_SUMMARY
        )