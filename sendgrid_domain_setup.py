#!/usr/bin/env python3
"""
SendGrid Domain Authentication Setup and Verification Script
For Budget Planner Production Email Configuration

This script helps set up domain authentication for budgetplanner.app
and verifies the SendGrid configuration.
"""

import requests
import json
import os
from datetime import datetime

SENDGRID_API_KEY = "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"
DOMAIN = "budgetplanner.app"
SENDER_EMAIL = "nicholasjonathan@gmail.com"

class SendGridDomainSetup:
    def __init__(self):
        self.api_key = SENDGRID_API_KEY
        self.base_url = "https://api.sendgrid.com/v3"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def check_api_key_status(self):
        """Verify SendGrid API key is valid"""
        print("🔑 Checking SendGrid API Key Status...")
        print("=" * 60)
        
        try:
            response = requests.get(f"{self.base_url}/user/account", headers=self.headers)
            
            if response.status_code == 200:
                account_data = response.json()
                print(f"✅ API Key Valid")
                print(f"   Account Type: {account_data.get('type', 'N/A')}")
                print(f"   Reputation: {account_data.get('reputation', 'N/A')}")
                return True
            else:
                print(f"❌ API Key Invalid: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking API key: {e}")
            return False
    
    def check_sender_verification(self):
        """Check if sender email is verified"""
        print(f"\n📧 Checking Sender Email Verification for {SENDER_EMAIL}...")
        print("=" * 60)
        
        try:
            response = requests.get(f"{self.base_url}/verified_senders", headers=self.headers)
            
            if response.status_code == 200:
                verified_senders = response.json().get('results', [])
                
                for sender in verified_senders:
                    if sender.get('from_email') == SENDER_EMAIL:
                        verification_status = sender.get('verified')
                        print(f"✅ Sender Found: {SENDER_EMAIL}")
                        print(f"   Verified: {'Yes' if verification_status else 'No'}")
                        print(f"   From Name: {sender.get('from_name', 'N/A')}")
                        return verification_status
                
                print(f"⚠️  Sender {SENDER_EMAIL} not found in verified senders")
                print("   This means emails may be rejected or go to spam")
                return False
                
            else:
                print(f"❌ Failed to check verified senders: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking sender verification: {e}")
            return False
    
    def setup_domain_authentication(self):
        """Set up domain authentication for budgetplanner.app"""
        print(f"\n🌐 Setting up Domain Authentication for {DOMAIN}...")
        print("=" * 60)
        
        domain_config = {
            "domain": DOMAIN,
            "subdomain": "mail",  # This creates mail.budgetplanner.app
            "automatic_security": True,
            "custom_spf": True,
            "default": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/whitelabel/domains",
                headers=self.headers,
                json=domain_config
            )
            
            if response.status_code == 201:
                domain_data = response.json()
                domain_id = domain_data.get('id')
                
                print(f"✅ Domain authentication setup initiated")
                print(f"   Domain ID: {domain_id}")
                print(f"   Subdomain: {domain_data.get('subdomain')}")
                
                # Get DNS records that need to be configured
                self.get_dns_records(domain_id)
                return domain_id
                
            else:
                print(f"❌ Failed to setup domain authentication: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error setting up domain authentication: {e}")
            return None
    
    def get_dns_records(self, domain_id=None):
        """Get DNS records that need to be configured"""
        print(f"\n📋 DNS Records for {DOMAIN}...")
        print("=" * 60)
        
        if not domain_id:
            # Try to find existing domain
            response = requests.get(f"{self.base_url}/whitelabel/domains", headers=self.headers)
            if response.status_code == 200:
                domains = response.json()
                for domain in domains:
                    if domain.get('domain') == DOMAIN:
                        domain_id = domain.get('id')
                        break
        
        if not domain_id:
            print("⚠️  No domain authentication found. Please run setup first.")
            return
        
        try:
            response = requests.get(
                f"{self.base_url}/whitelabel/domains/{domain_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                domain_data = response.json()
                dns_records = domain_data.get('dns', {})
                
                print("📝 DNS Records to Add to your Domain Provider:")
                print("\n🔸 CNAME Records:")
                for record in dns_records.get('mail_cname', []):
                    print(f"   Host: {record.get('host')}")
                    print(f"   Value: {record.get('data')}")
                    print()
                
                print("🔸 MX Record:")
                mx_record = dns_records.get('mail_server', {})
                if mx_record:
                    print(f"   Host: {DOMAIN}")
                    print(f"   Value: {mx_record.get('data')}")
                    print(f"   Priority: 10")
                    print()
                
                print("🔸 TXT Record (SPF):")
                for record in dns_records.get('spf', []):
                    print(f"   Host: {record.get('host')}")
                    print(f"   Value: {record.get('data')}")
                    print()
                
                print("🔸 DKIM Records:")
                for record in dns_records.get('dkim', []):
                    print(f"   Host: {record.get('host')}")
                    print(f"   Value: {record.get('data')}")
                    print()
                
                return dns_records
                
        except Exception as e:
            print(f"❌ Error getting DNS records: {e}")
            return None
    
    def verify_domain_authentication(self):
        """Verify domain authentication status"""
        print(f"\n✅ Verifying Domain Authentication for {DOMAIN}...")
        print("=" * 60)
        
        try:
            response = requests.get(f"{self.base_url}/whitelabel/domains", headers=self.headers)
            
            if response.status_code == 200:
                domains = response.json()
                
                for domain in domains:
                    if domain.get('domain') == DOMAIN:
                        valid = domain.get('valid')
                        legacy = domain.get('legacy')
                        
                        print(f"✅ Domain Found: {DOMAIN}")
                        print(f"   Valid: {'Yes' if valid else 'No'}")
                        print(f"   Legacy: {'Yes' if legacy else 'No'}")
                        print(f"   ID: {domain.get('id')}")
                        
                        if not valid:
                            print("\n⚠️  Domain not yet verified. DNS records may still be propagating.")
                            print("   This can take up to 24-48 hours after DNS configuration.")
                        
                        return valid
                
                print(f"⚠️  Domain {DOMAIN} not found in authenticated domains")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying domain authentication: {e}")
            return False
    
    def send_test_email(self):
        """Send a test email to verify everything is working"""
        print(f"\n📬 Sending Test Email from {SENDER_EMAIL}...")
        print("=" * 60)
        
        test_email_data = {
            "personalizations": [
                {
                    "to": [{"email": SENDER_EMAIL}],
                    "subject": "Budget Planner - SendGrid Production Test"
                }
            ],
            "from": {"email": SENDER_EMAIL, "name": "Budget Planner"},
            "content": [
                {
                    "type": "text/html",
                    "value": """
                    <html>
                        <body>
                            <h2>🎉 SendGrid Production Setup Successful!</h2>
                            <p>This email confirms that your Budget Planner SendGrid integration is working correctly.</p>
                            <div style="border: 1px solid #ccc; padding: 15px; margin: 10px 0;">
                                <h3>Configuration Details:</h3>
                                <p><strong>Domain:</strong> budgetplanner.app</p>
                                <p><strong>Sender:</strong> nicholasjonathan@gmail.com</p>
                                <p><strong>Status:</strong> Production Ready ✅</p>
                            </div>
                            <p><em>Budget Planner - Built for India 🇮🇳</em></p>
                        </body>
                    </html>
                    """
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/mail/send",
                headers=self.headers,
                json=test_email_data
            )
            
            if response.status_code == 202:
                print("✅ Test email sent successfully!")
                print(f"   Sent to: {SENDER_EMAIL}")
                print("   Check your inbox (and spam folder)")
                return True
            else:
                print(f"❌ Failed to send test email: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending test email: {e}")
            return False
    
    def run_complete_setup(self):
        """Run the complete SendGrid production setup process"""
        print("🚀 BUDGET PLANNER - SENDGRID PRODUCTION SETUP")
        print("=" * 70)
        print(f"Domain: {DOMAIN}")
        print(f"Sender: {SENDER_EMAIL}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Step 1: Check API key
        if not self.check_api_key_status():
            print("\n❌ Setup aborted due to invalid API key")
            return False
        
        # Step 2: Check sender verification
        sender_verified = self.check_sender_verification()
        
        # Step 3: Setup domain authentication
        domain_id = self.setup_domain_authentication()
        
        # Step 4: Get DNS records
        if domain_id:
            dns_records = self.get_dns_records(domain_id)
        
        # Step 5: Verify domain (may not be valid immediately)
        domain_valid = self.verify_domain_authentication()
        
        # Step 6: Send test email
        test_email_sent = self.send_test_email()
        
        # Summary
        print(f"\n📊 SETUP SUMMARY")
        print("=" * 70)
        print(f"✅ API Key: Valid")
        print(f"{'✅' if sender_verified else '⚠️ '} Sender Verification: {'Complete' if sender_verified else 'Pending'}")
        print(f"{'✅' if domain_id else '❌'} Domain Setup: {'Complete' if domain_id else 'Failed'}")
        print(f"{'✅' if domain_valid else '⚠️ '} Domain Verification: {'Complete' if domain_valid else 'Pending'}")
        print(f"{'✅' if test_email_sent else '❌'} Test Email: {'Sent' if test_email_sent else 'Failed'}")
        
        if not sender_verified:
            print(f"\n⚠️  NEXT STEPS REQUIRED:")
            print(f"1. Log into SendGrid dashboard")
            print(f"2. Go to Settings → Sender Authentication")  
            print(f"3. Add and verify sender: {SENDER_EMAIL}")
        
        if domain_id and not domain_valid:
            print(f"\n⚠️  DNS CONFIGURATION REQUIRED:")
            print(f"1. Add the DNS records shown above to your domain provider")
            print(f"2. Wait 24-48 hours for DNS propagation")
            print(f"3. Re-run verification")
        
        print(f"\n🎉 SendGrid production setup is {'COMPLETE' if sender_verified and domain_valid else 'IN PROGRESS'}!")
        return True

if __name__ == "__main__":
    setup = SendGridDomainSetup()
    setup.run_complete_setup()