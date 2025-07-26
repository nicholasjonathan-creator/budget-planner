import re
from datetime import datetime
from typing import Optional, Dict, Any
from models.transaction import Transaction, TransactionType, TransactionSource

class SMSTransactionParser:
    def __init__(self):
        # Real-world HDFC SMS patterns based on actual messages
        self.hdfc_patterns = {
            # Pattern 1: Multiline "Sent Rs.X\nFrom HDFC Bank A/C *XXXX\nTo PAYEE\nOn DD/MM/YY"
            'upi_sent_multiline': {
                'regex': r'sent\s+rs\.([\d,]+(?:\.\d{2})?)\s*\n?\s*from\s+hdfc\s+bank\s+a/c\s*\*?([x\d]+)\s*\n?\s*to\s+(.+?)\s*\n?\s*on\s+(\d{2}/\d{2}/\d{2})',
                'amount_group': 1,
                'account_group': 2,
                'payee_group': 3,
                'date_group': 4,
                'type': 'expense'
            },
            # Pattern 1b: Single line "Sent Rs.X From HDFC Bank A/C *XXXX To PAYEE On DD/MM/YY"
            'upi_sent': {
                'regex': r'sent\s+rs\.([\d,]+(?:\.\d{2})?)\s+from\s+hdfc\s+bank\s+a/c\s*\*?([x\d]+)\s+to\s+(.+?)\s+on\s+(\d{2}/\d{2}/\d{2})',
                'amount_group': 1,
                'account_group': 2,
                'payee_group': 3,
                'date_group': 4,
                'type': 'expense'
            },
            # Pattern 2: "UPDATE: INR X,XX,XXX.XX debited from HDFC Bank XXXX on DD-MMM-YY"
            'update_debit': {
                'regex': r'update.*?inr\s+([\d,]+(?:\.\d{2})?)\s+debited\s+from\s+hdfc\s+bank\s+([x\d]+)\s+on\s+(\d{2}-[A-Z]{3}-\d{2}).*?info:\s*(.+?)(?:\.|avl)',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'payee_group': 4,
                'type': 'expense'
            },
            # Pattern 3: "Update! INR X,XX,XXX.XX deposited in HDFC Bank A/c XXXX on DD-MMM-YY for PAYEE"
            'update_credit': {
                'regex': r'update.*?inr\s+([\d,]+(?:\.\d{2})?)\s+deposited\s+in\s+hdfc\s+bank\s+a/c\s+([x\d]+)\s+on\s+(\d{2}-[A-Z]{3}-\d{2})\s+for\s+(.+?)\.?\s*avl',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'payee_group': 4,
                'type': 'income'
            },
            # Pattern 4: "IMPS INR X\nsent from HDFC Bank A/c XXXX on DD-MM-YY\nTo A/c XXXXXXXX"
            'imps_sent_multiline': {
                'regex': r'imps\s+inr\s+([\d,]+(?:\.\d{2})?)\s*\n?\s*sent\s+from\s+hdfc\s+bank\s+a/c\s+([x\d]+)\s+on\s+(\d{2}-\d{2}-\d{2})\s*\n?\s*to\s+a/c\s+([x\d]+)',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'payee_group': 4,
                'type': 'expense'
            },
            # Pattern 4b: Single line "IMPS INR X sent from HDFC Bank A/c XXXX on DD-MM-YY To A/c XXXXXXXX"
            'imps_sent': {
                'regex': r'imps\s+inr\s+([\d,]+(?:\.\d{2})?)\s+sent\s+from\s+hdfc\s+bank\s+a/c\s+([x\d]+)\s+on\s+(\d{2}-\d{2}-\d{2})\s+to\s+a/c\s+([x\d]+)',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'payee_group': 4,
                'type': 'expense'
            },
            # Pattern 5: "Spent Rs.XXXXX.XX From HDFC Bank Card xXXXX At MERCHANT On YYYY-MM-DD:HH:MM:SS"
            'card_spent': {
                'regex': r'spent\s+rs\.([\d,]+(?:\.\d{2})?)\s+from\s+hdfc\s+bank\s+card\s+([x\d]+)\s+at\s+(.+?)\s+on\s+(\d{4}-\d{2}-\d{2}:\d{2}:\d{2}:\d{2})',
                'amount_group': 1,
                'account_group': 2,
                'payee_group': 3,
                'date_group': 4,
                'type': 'expense'
            }
        }
        
        # Axis Bank SMS patterns  
        self.axis_patterns = {
            # Pattern 1: "Spent\nCard no. XXXX\nINR amount\ndate time\nMERCHANT\nAvl Lmt INR amount"
            'card_spent_multiline': {
                'regex': r'spent\s*\n?\s*card\s+no\.\s+([x\d]+)\s*\n?\s*(?:inr|usd)\s+([\d,]+(?:\.\d{2})?)\s*\n?\s*(\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s*\n?\s*(.+?)\s*\n?\s*avl\s+lmt',
                'amount_group': 2,
                'account_group': 1,
                'date_group': 3,
                'time_group': 4,
                'payee_group': 5,
                'type': 'expense'
            },
            # Pattern 2: "Debit INR amount\nAxis Bank A/c XXXX\ndate time\nACH-DR-MERCHANT"
            'debit_multiline': {
                'regex': r'debit\s+inr\s+([\d,]+(?:\.\d{2})?)\s*\n?\s*axis\s+bank\s+a/c\s+([x\d]+)\s*\n?\s*(\d{2}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s*\n?\s*ach-dr-(.+?)-',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'time_group': 4,
                'payee_group': 5,
                'type': 'expense'
            },
            # Pattern 3: "INR amount debited\nA/c no. XXXX\ndate, time\nUPI/P2A/ref/MERCHANT"
            'upi_debit_multiline': {
                'regex': r'inr\s+([\d,]+(?:\.\d{2})?)\s+debited\s*\n?\s*a/c\s+no\.\s+([x\d]+)\s*\n?\s*(\d{2}-\d{2}-\d{2}),\s+(\d{2}:\d{2}:\d{2})\s*\n?\s*upi/p2a/[^/]+/(.+?)(?:\s|$)',
                'amount_group': 1,
                'account_group': 2,
                'date_group': 3,
                'time_group': 4,
                'payee_group': 5,
                'type': 'expense'
            },
            # Pattern 4: "PAYMENT ALERT!\nINR amount deducted from HDFC Bank A/C No XXXX towards MERCHANT"
            'payment_alert': {
                'regex': r'payment\s+alert!\s*\n?\s*inr\s+([\d,]+(?:\.\d{2})?)\s+deducted\s+from\s+hdfc\s+bank\s+a/c\s+no\s+(\d+)\s+towards\s+(.+?)(?:\s+umrn|$)',
                'amount_group': 1,
                'account_group': 2,
                'payee_group': 3,
                'date_group': None,  # No date in this format
                'type': 'expense'
            }
        }
        
        # Scapia/Federal Bank SMS patterns
        self.scapia_patterns = {
            # Pattern 1: "Hi! Your txn of ₹amount at MERCHANT on your Scapia Federal ... credit card was successful"
            'credit_card_success': {
                'regex': r'hi!\s*your\s+txn\s+of\s+₹([\d,]+(?:\.\d{2})?)\s+at\s+(.+?)\s+on\s+your\s+scapia\s+federal\s+.*?\s+credit\s+card\s+was\s+successful',
                'amount_group': 1,
                'payee_group': 2,
                'type': 'expense'
            },
            # Pattern 2: "Hi! Your txn for ₹amount at MERCHANT on your Scapia Federal ... credit card has been reversed"
            'credit_card_reversal': {
                'regex': r'hi!\s*your\s+txn\s+for\s+₹([\d,]+(?:\.\d{2})?)\s+at\s+(.+?)\s+on\s+your\s+scapia\s+federal\s+.*?\s+credit\s+card\s+has\s+been\s+reversed',
                'amount_group': 1,
                'payee_group': 2,
                'type': 'income'  # Reversal is income
            }
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
            r'avl\s+bal:\s*inr\s+([\d,]+(?:\.\d{2})?)',
            r'avl\s+bal\s+inr\s+([\d,]+(?:\.\d{2})?)',
            r'avl\s+lmt\s+inr\s+([\d,]+(?:\.\d{2})?)',  # Axis Bank balance format
            r'bal\s+rs\.([\d,]+(?:\.\d{2})?)',
            r'balance.*?(?:rs|inr|₹)?\s*([\d,]+(?:\.\d{2})?)'
        ]
        
        # Account number extraction
        self.account_patterns = [
            r'a/c\s*\*?([x\d]+)',
            r'card\s*([x\d]+)',
            r'xx(\d{4,})',
            r'account.*?([x\d]{4,})'
        ]

    def parse_sms(self, sms_text: str, phone_number: str) -> Optional[Transaction]:
        """Parse SMS text and extract transaction details - Enhanced for real HDFC formats"""
        try:
            sms_lower = sms_text.lower()
            
            # First try HDFC specific patterns
            parsed_data = self._parse_hdfc_sms(sms_text)
            if parsed_data:
                return Transaction(
                    type=parsed_data['type'],
                    category_id=self._auto_categorize(parsed_data['payee'], parsed_data['payee']),
                    amount=parsed_data['amount'],
                    description=self._generate_description(parsed_data['payee'], sms_text),
                    date=self._parse_date(parsed_data['date']),
                    source=TransactionSource.SMS,
                    merchant=parsed_data['payee'],
                    account_number=parsed_data['account'],
                    balance=parsed_data.get('balance'),
                    raw_data={
                        'sms_text': sms_text,
                        'phone_number': phone_number,
                        'parsed_at': datetime.now().isoformat(),
                        'bank': 'HDFC',
                        'parsing_method': 'hdfc_specific'
                    }
                )
            
            # Try Axis Bank specific patterns
            parsed_data = self._parse_axis_sms(sms_text)
            if parsed_data:
                return Transaction(
                    type=parsed_data['type'],
                    category_id=self._auto_categorize(parsed_data['payee'], parsed_data['payee']),
                    amount=parsed_data['amount'],
                    description=self._generate_description(parsed_data['payee'], sms_text),
                    date=self._parse_date(parsed_data['date']),
                    source=TransactionSource.SMS,
                    merchant=parsed_data['payee'],
                    account_number=parsed_data['account'],
                    balance=parsed_data.get('balance'),
                    raw_data={
                        'sms_text': sms_text,
                        'phone_number': phone_number,
                        'parsed_at': datetime.now().isoformat(),
                        'bank': 'Axis Bank',
                        'parsing_method': 'axis_specific'
                    }
                )
            
            # Try Scapia/Federal Bank specific patterns
            parsed_data = self._parse_scapia_sms(sms_text)
            if parsed_data:
                return Transaction(
                    type=parsed_data['type'],
                    category_id=self._auto_categorize(parsed_data['payee'], parsed_data['payee']),
                    amount=parsed_data['amount'],
                    description=self._generate_description(parsed_data['payee'], sms_text),
                    date=parsed_data.get('date', datetime.now().strftime('%d-%m-%y')),
                    source=TransactionSource.SMS,
                    merchant=parsed_data['payee'],
                    account_number=parsed_data.get('account', 'Scapia Card'),
                    balance=parsed_data.get('balance'),
                    raw_data={
                        'sms_text': sms_text,
                        'phone_number': phone_number,
                        'parsed_at': datetime.now().isoformat(),
                        'bank': 'Federal Bank (Scapia)',
                        'parsing_method': 'scapia_specific'
                    }
                )
            
            # Fallback to generic patterns
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
                    'parsed_at': datetime.now().isoformat(),
                    'parsing_method': 'generic'
                }
            )
            
        except Exception as e:
            print(f"Error parsing SMS: {e}")
            return None

    def _parse_hdfc_sms(self, sms_text: str) -> Optional[dict]:
        """Parse HDFC specific SMS formats"""
        for pattern_name, pattern_info in self.hdfc_patterns.items():
            match = re.search(pattern_info['regex'], sms_text, re.IGNORECASE)
            if match:
                amount_str = match.group(pattern_info['amount_group']).replace(',', '')
                amount = float(amount_str)
                
                account = match.group(pattern_info['account_group'])
                date_str = match.group(pattern_info['date_group'])
                
                # Extract payee
                payee = self._clean_payee_name(match.group(pattern_info['payee_group']))
                
                # Extract balance if available
                balance = self._extract_balance(sms_text)
                
                return {
                    'amount': amount,
                    'account': account,
                    'date': date_str,
                    'payee': payee,
                    'type': TransactionType.EXPENSE if pattern_info['type'] == 'expense' else TransactionType.INCOME,
                    'balance': balance,
                    'pattern_matched': pattern_name
                }
        
        return None

    def _parse_axis_sms(self, sms_text: str) -> Optional[dict]:
        """Parse Axis Bank specific SMS formats"""
        for pattern_name, pattern_info in self.axis_patterns.items():
            match = re.search(pattern_info['regex'], sms_text, re.IGNORECASE)
            if match:
                amount_str = match.group(pattern_info['amount_group']).replace(',', '')
                
                # Handle USD conversion (rough estimate)
                if 'usd' in sms_text.lower():
                    amount = float(amount_str) * 83.0  # Convert USD to INR (rough rate)
                else:
                    amount = float(amount_str)
                
                account = match.group(pattern_info['account_group'])
                
                # Handle date if available
                if pattern_info.get('date_group') is not None:
                    date_str = match.group(pattern_info['date_group'])
                else:
                    date_str = datetime.now().strftime('%d-%m-%y')  # Use current date if not available
                
                # Extract payee
                payee = self._clean_payee_name(match.group(pattern_info['payee_group']))
                
                # Extract balance if available
                balance = self._extract_balance(sms_text)
                
                return {
                    'amount': amount,
                    'account': account,
                    'date': date_str,
                    'payee': payee,
                    'type': TransactionType.EXPENSE if pattern_info['type'] == 'expense' else TransactionType.INCOME,
                    'balance': balance,
                    'pattern_matched': pattern_name
                }
        
        return None

    def _parse_scapia_sms(self, sms_text: str) -> Optional[dict]:
        """Parse Scapia/Federal Bank specific SMS formats"""
        for pattern_name, pattern_info in self.scapia_patterns.items():
            match = re.search(pattern_info['regex'], sms_text, re.IGNORECASE)
            if match:
                amount_str = match.group(pattern_info['amount_group']).replace(',', '')
                amount = float(amount_str)
                
                # Extract payee (merchant)
                payee = self._clean_payee_name(match.group(pattern_info['payee_group']))
                
                return {
                    'amount': amount,
                    'payee': payee,
                    'type': TransactionType.EXPENSE if pattern_info['type'] == 'expense' else TransactionType.INCOME,
                    'pattern_matched': pattern_name,
                    'date': datetime.now().strftime('%d-%m-%y'),  # Use current date
                    'account': 'Scapia Card'
                }
        
        return None

    def _clean_payee_name(self, payee_raw: str) -> str:
        """Clean and format payee name"""
        # Clean up common patterns
        payee = payee_raw.strip()
        
        # Remove newlines and extra spaces
        payee = re.sub(r'\s*\n\s*', ' ', payee)
        payee = re.sub(r'\s+', ' ', payee)
        
        # Handle specific patterns
        if 'imps-' in payee.lower():
            # Extract from IMPS pattern: "IMPS-520611360945-Old Man-HDFC-xxxxxxxxxx5124-Rent"
            parts = payee.split('-')
            if len(parts) >= 3:
                payee = parts[2]  # Get the name part
        
        # Handle ACH patterns: "ACH D- TP ACH INDIANESIGN-1862188817"
        if 'ach d-' in payee.lower():
            # Extract company name from ACH pattern
            ach_match = re.search(r'ach\s+d-\s*.*?([a-zA-Z]+)-\d+', payee, re.IGNORECASE)
            if ach_match:
                company_part = ach_match.group(1)
                if company_part and len(company_part) > 2:
                    payee = company_part
            else:
                # Fallback: extract the last alphabetic part before numbers
                ach_fallback = re.search(r'([a-zA-Z]+)-?\d+$', payee, re.IGNORECASE)
                if ach_fallback:
                    payee = ach_fallback.group(1)
        
        # Handle account transfers (extract account number)
        if 'a/c' in payee.lower() and 'x' in payee.lower():
            # For account transfers, use "Account Transfer" as payee
            account_match = re.search(r'(x+\d+)', payee, re.IGNORECASE)
            if account_match:
                payee = f"Account Transfer - {account_match.group(1)}"
        
        # Clean up extra spaces and dots
        payee = re.sub(r'\s+', ' ', payee)
        payee = re.sub(r'\.+', '.', payee)
        
        return payee.strip()

    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats from HDFC SMS"""
        try:
            # Format: DD/MM/YY
            if '/' in date_str and len(date_str) == 8:
                return datetime.strptime(date_str, '%d/%m/%y')
            
            # Format: DD-MMM-YY
            elif '-' in date_str and len(date_str) == 9:
                return datetime.strptime(date_str, '%d-%b-%y')
            
            # Format: YYYY-MM-DD:HH:MM:SS
            elif ':' in date_str:
                return datetime.strptime(date_str, '%Y-%m-%d:%H:%M:%S')
            
            # Format: DD-MM-YY
            elif '-' in date_str and len(date_str) == 8:
                return datetime.strptime(date_str, '%d-%m-%y')
            
        except ValueError:
            pass
        
        # Default to current time if parsing fails
        return datetime.now()

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

# Test with real HDFC SMS messages
def test_sms_parser():
    parser = SMSTransactionParser()
    
    real_hdfc_messages = [
        # User-provided real HDFC examples (multiline format)
        "Sent Rs.134985.00\nFrom HDFC Bank A/C *2953\nTo FINZOOM INVESTMENT ADVISORS PRIVATE LIMITED\nOn 25/07/25\nRef 520648518501\nNot You?\nCall 18002586161/SMS BLOCK UPI to 7308080808",
        "Sent Rs.5000.00\nFrom HDFC Bank A/C *2953\nTo MELODY HENRIETTA NICHOLAS\nOn 25/07/25\nRef 108669255361\nNot You?\nCall 18002586161/SMS BLOCK UPI to 7308080808",
        "Sent Rs.175.00\nFrom HDFC Bank A/C *2953\nTo RAMESH .  H.R..\nOn 18/07/25\nRef 108305259738\nNot You?\nCall 18002586161/SMS BLOCK UPI to 7308080808",
        "UPDATE: INR 1,37,083.00 debited from HDFC Bank XX2953 on 25-JUL-25. Info: IMPS-520611360945-Old Man-HDFC-xxxxxxxxxx5124-Rent. Avl bal:INR 3,75,261.90",
        "Update! INR 4,95,865.00 deposited in HDFC Bank A/c XX2953 on 25-JUL-25 for WFISPL CREDIT.Avl bal INR 5,12,344.90. Cheque deposits in A/C are subject to clearing",
        "IMPS INR 5,000.00\nsent from HDFC Bank A/c XX2953 on 25-07-25\nTo A/c xxxxxxxxxxx1254\nRef-520611366849\nNot you?Call 18002586161/SMS BLOCK OB to 7308080808",
        "Spent Rs.15065.08 From HDFC Bank Card x7722 At RAZ*Allard Educational On 2025-07-15:00:18:09 Bal Rs.25407.31 Not You? Call 18002586161/SMS BLOCK DC  7722 to 7308080808",
        "UPDATE: INR 5,000.00 debited from HDFC Bank XX2953 on 01-JUL-25. Info: ACH D- TP ACH INDIANESIGN-1862188817. Avl bal:INR 2,40,315.16",
        "UPDATE: INR 25,000.00 debited from HDFC Bank XX2953 on 01-JUL-25. Info: ACH D- TP ACH INDIANESIGN-1862147866. Avl bal:INR 2,45,315.16",
        "Sent Rs.549.00\nFrom HDFC Bank A/C x2953\nTo Blinkit\nOn 29/06/25\nRef 107215970082\nNot You?\nCall 18002586161/SMS BLOCK UPI to 7308080808",
        
        # Original test examples
        "Sent Rs.134985.00 From HDFC Bank A/C *2953 To FINZOOM INVESTMENT ADVISORS PRIVATE LIMITED On 25/07/25 Ref 520648518501 Not You? Call 18002586161/SMS BLOCK UPI to 7308080808",
        "Sent Rs.5000.00 From HDFC Bank A/C *2953 To MELODY HENRIETTA NICHOLAS On 25/07/25 Ref 108669255361 Not You? Call 18002586161/SMS BLOCK UPI to 7308080808",
        "UPDATE: INR 1,37,083.00 debited from HDFC Bank XX2953 on 25-JUL-25. Info: IMPS-520611360945-Old Man-HDFC-xxxxxxxxxx5124-Rent. Avl bal:INR 3,75,261.90",
        "Update! INR 4,95,865.00 deposited in HDFC Bank A/c XX2953 on 25-JUL-25 for WFISPL CREDIT.Avl bal INR 5,12,344.90. Cheque deposits in A/C are subject to clearing",
        "IMPS INR 5,000.00 sent from HDFC Bank A/c XX2953 on 25-07-25 To A/c xxxxxxxxxxx1254 Ref-520611366849 Not you?Call 18002586161/SMS BLOCK OB to 7308080808",
        "Spent Rs.15065.08 From HDFC Bank Card x7722 At RAZ*Allard Educational On 2025-07-15:00:18:09 Bal Rs.25407.31 Not You? Call 18002586161/SMS BLOCK DC 7722 to 7308080808",
        "UPDATE: INR 5,000.00 debited from HDFC Bank XX2953 on 01-JUL-25. Info: ACH D- TP ACH INDIANESIGN-1862188817. Avl bal:INR 2,40,315.16",
        "Sent Rs.549.00 From HDFC Bank A/C x2953 To Blinkit On 29/06/25 Ref 107215970082 Not You? Call 18002586161/SMS BLOCK UPI to 7308080808"
    ]
    
    print("Testing HDFC SMS Parser with Real Messages")
    print("=" * 50)
    
    for i, sms in enumerate(real_hdfc_messages, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"SMS: {sms[:80]}...")
        transaction = parser.parse_sms(sms, "+918000000000")
        if transaction:
            print(f"✅ SUCCESS")
            print(f"   Amount: ₹{transaction.amount:,.2f}")
            print(f"   Type: {transaction.type}")
            print(f"   Payee: {transaction.merchant}")
            print(f"   Account: {transaction.account_number}")
            print(f"   Date: {transaction.date}")
            print(f"   Category: {transaction.category_id}")
            print(f"   Balance: ₹{transaction.balance:,.2f}" if transaction.balance else "N/A")
        else:
            print(f"❌ FAILED TO PARSE")

if __name__ == "__main__":
    test_sms_parser()