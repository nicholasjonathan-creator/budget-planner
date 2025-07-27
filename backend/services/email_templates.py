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