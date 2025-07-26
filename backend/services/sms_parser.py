import re
from datetime import datetime
from typing import Optional, Dict, Any
from models.transaction import Transaction, TransactionType, TransactionSource

class SMSTransactionParser:
    def __init__(self):
        # Real-world HDFC SMS patterns based on actual messages
        self.hdfc_patterns = {
            # Pattern 1: "Sent Rs.X From HDFC Bank A/C *XXXX To PAYEE On DD/MM/YY"
            'upi_sent': {
                'regex': r'sent\s+rs\.(\d+(?:,\d{3})*(?:\.\d{2})?)\s+from\s+hdfc\s+bank\s+a/c\s*\*?([x\d]+)\s+to\s+(.+?)\s+on\s+(\d{2}/\d{2}/\d{2})',
                'amount_group': 1,
                'account_group': 2,
                'payee_group': 3,
                'date_group': 4,
                'type': 'expense'
            },
            # Pattern 2: "UPDATE: INR X,XX,XXX.XX debited from HDFC Bank XXXX on DD-MMM-YY"
            'update_debit': {
                'regex': r'update.*?inr\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s+debited\s+from\s+hdfc\s+bank\s+([x\d]+)\s+on\s+(\d{2}-[A-Z]{3}-\d{2}).*?info:\s*(.+?)(?:\.|avl)',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'payee_group': 4,
                'type': 'expense'
            },
            # Pattern 3: "Update! INR X,XX,XXX.XX deposited in HDFC Bank A/c XXXX on DD-MMM-YY for PAYEE"
            'update_credit': {
                'regex': r'update.*?inr\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s+deposited\s+in\s+hdfc\s+bank\s+a/c\s+([x\d]+)\s+on\s+(\d{2}-[A-Z]{3}-\d{2})\s+for\s+(.+?)\.?avl',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'payee_group': 4,
                'type': 'income'
            },
            # Pattern 4: "IMPS INR X,XXX.XX sent from HDFC Bank A/c XXXX on DD-MM-YY To A/c XXXXXXXXXX"
            'imps_sent': {
                'regex': r'imps\s+inr\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s+sent\s+from\s+hdfc\s+bank\s+a/c\s+([x\d]+)\s+on\s+(\d{2}-\d{2}-\d{2})\s+to\s+a/c\s+([x\d]+)',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'payee_group': 4,
                'type': 'expense'
            },
            # Pattern 5: "Spent Rs.XXXXX.XX From HDFC Bank Card xXXXX At MERCHANT On YYYY-MM-DD:HH:MM:SS"
            'card_spent': {
                'regex': r'spent\s+rs\.(\d+(?:,\d{3})*(?:\.\d{2})?)\s+from\s+hdfc\s+bank\s+card\s+([x\d]+)\s+at\s+(.+?)\s+on\s+(\d{4}-\d{2}-\d{2}:\d{2}:\d{2}:\d{2})',
                'amount_group': 1,
                'account_group': 2,
                'payee_group': 3,
                'date_group': 4,
                'type': 'expense'
            }
        }
        
        # Fallback patterns for other banks
        self.bank_patterns = {
            'debit': [
                r'debited.*?(?:rs|inr|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'spent.*?(?:rs|inr|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'paid.*?(?:rs|inr|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'withdrawn.*?(?:rs|inr|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(?:rs|inr|₹)\.?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:debited|spent|paid|sent)'
            ],
            'credit': [
                r'credited.*?(?:rs|inr|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'received.*?(?:rs|inr|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'deposited.*?(?:rs|inr|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'(?:rs|inr|₹)\.?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:credited|received|deposited)'
            ]
        }
        
        # Merchant extraction patterns
        self.merchant_patterns = [
            r'to\s+([A-Z][A-Za-z\s\.]+?)(?:\s+on|\s+ref|\s*$)',
            r'at\s+([A-Z][A-Za-z\s\*]+?)(?:\s+on|\s+\d|\s*$)',
            r'for\s+([A-Z][A-Za-z\s]+?)\.(?:avl|$)',
            r'info:\s*[^-]+-([A-Za-z\s]+?)-',
        ]
        
        # Balance extraction
        self.balance_patterns = [
            r'avl\s+bal:?\s*(?:inr|rs)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'bal\s+(?:inr|rs)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'balance.*?(?:rs|inr|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        # Account number extraction
        self.account_patterns = [
            r'a/c\s*\*?([x\d]+)',
            r'card\s*([x\d]+)',
            r'xx(\d{4,})',
            r'account.*?([x\d]{4,})'
        ]

    def parse_sms(self, sms_text: str, phone_number: str) -> Optional[Transaction]:
        """Parse SMS text and extract transaction details"""
        try:
            sms_lower = sms_text.lower()
            
            # Determine transaction type and extract amount
            transaction_type, amount = self._extract_amount_and_type(sms_lower)
            if not amount:
                return None
                
            # Extract merchant/description
            merchant = self._extract_merchant(sms_text)
            
            # Extract account info
            account_number = self._extract_account_number(sms_text)
            
            # Extract balance
            balance = self._extract_balance(sms_lower)
            
            # Generate description
            description = self._generate_description(merchant, sms_text)
            
            # Auto-categorize
            category_id = self._auto_categorize(merchant, description)
            
            return Transaction(
                type=transaction_type,
                category_id=category_id,
                amount=amount,
                description=description,
                date=datetime.now(),
                source=TransactionSource.SMS,
                merchant=merchant,
                account_number=account_number,
                balance=balance,
                raw_data={
                    'sms_text': sms_text,
                    'phone_number': phone_number,
                    'parsed_at': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            print(f"Error parsing SMS: {e}")
            return None

    def _extract_amount_and_type(self, sms_text: str) -> tuple:
        """Extract transaction amount and determine type - Enhanced for HDFC formats"""
        # Try debit patterns first
        for pattern in self.bank_patterns['debit']:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')  # Remove commas
                amount = float(amount_str)
                return TransactionType.EXPENSE, amount
        
        # Try credit patterns
        for pattern in self.bank_patterns['credit']:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')  # Remove commas
                amount = float(amount_str)
                return TransactionType.INCOME, amount
                
        return None, None

    def _extract_merchant(self, sms_text: str) -> Optional[str]:
        """Extract merchant name from SMS"""
        for pattern in self.merchant_patterns:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                merchant = match.group(1).strip()
                # Clean up merchant name
                merchant = re.sub(r'\s+', ' ', merchant)
                return merchant
        return None

    def _extract_account_number(self, sms_text: str) -> Optional[str]:
        """Extract account number from SMS"""
        for pattern in self.account_patterns:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_balance(self, sms_text: str) -> Optional[float]:
        """Extract account balance from SMS"""
        for pattern in self.balance_patterns:
            match = re.search(pattern, sms_text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        return None

    def _generate_description(self, merchant: str, sms_text: str) -> str:
        """Generate transaction description"""
        if merchant:
            return f"Transaction at {merchant}"
        
        # Extract key words from SMS for description
        words = sms_text.split()
        key_words = [word for word in words if len(word) > 3 and word.isalpha()]
        
        if key_words:
            return f"Transaction - {' '.join(key_words[:3])}"
        
        return "Bank transaction"

    def _auto_categorize(self, merchant: str, description: str) -> int:
        """Auto-categorize transaction based on merchant and description"""
        text = f"{merchant or ''} {description}".lower()
        
        # Category mapping (matches frontend mock data)
        category_mapping = {
            5: ['food', 'dining', 'restaurant', 'cafe', 'pizza', 'burger', 'coffee', 'starbucks', 'mcdonalds', 'subway', 'dominos', 'swiggy', 'zomato', 'grubhub', 'uber eats'],
            6: ['transport', 'taxi', 'uber', 'lyft', 'bus', 'train', 'metro', 'gas', 'petrol', 'fuel', 'parking', 'toll'],
            7: ['entertainment', 'movie', 'cinema', 'netflix', 'spotify', 'gaming', 'game', 'theatre', 'concert', 'show'],
            8: ['shopping', 'amazon', 'flipkart', 'mall', 'store', 'clothing', 'fashion', 'shoes', 'electronics', 'gadget'],
            9: ['bill', 'utility', 'electricity', 'water', 'gas', 'internet', 'phone', 'mobile', 'broadband', 'wifi'],
            10: ['health', 'hospital', 'doctor', 'medical', 'pharmacy', 'medicine', 'clinic', 'dental'],
            11: ['education', 'school', 'college', 'university', 'course', 'training', 'book', 'study'],
            12: ['other', 'misc', 'general', 'unknown']
        }
        
        # Check for category matches
        for category_id, keywords in category_mapping.items():
            if any(keyword in text for keyword in keywords):
                return category_id
        
        # Default to "Other Expenses"
        return 12

# Test cases for SMS parsing
def test_sms_parser():
    parser = SMSTransactionParser()
    
    test_cases = [
        "Dear Customer, Rs 250.00 debited from your account ending 1234 at STARBUCKS COFFEE on 25-Jul-25. Available balance: Rs 15750.00",
        "Your account 1234 has been debited by Rs 120.50 for transaction at DOMINOS PIZZA on 25/07/2025. Balance: Rs 8879.50",
        "Rs 5000.00 credited to your account 5678 - SALARY PAYMENT on 01-Jul-25. Available balance: Rs 25000.00",
        "Spent Rs 80.00 at METRO STATION via UPI on 25-Jul-25. A/c balance: Rs 4920.00",
        "Your card ending 9876 used for Rs 45.00 at UBER TRIP on 25-Jul-25. Available balance: Rs 3455.00"
    ]
    
    for i, sms in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"SMS: {sms}")
        transaction = parser.parse_sms(sms, "+1234567890")
        if transaction:
            print(f"Type: {transaction.type}")
            print(f"Amount: {transaction.amount}")
            print(f"Merchant: {transaction.merchant}")
            print(f"Category ID: {transaction.category_id}")
            print(f"Description: {transaction.description}")
            print(f"Balance: {transaction.balance}")
        else:
            print("Failed to parse")

if __name__ == "__main__":
    test_sms_parser()