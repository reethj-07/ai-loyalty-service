"""
Email Service using SendGrid
Handles transactional and campaign emails
"""
import os
from typing import Dict, List, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor


class EmailService:
    """SendGrid email service for campaigns and transactional emails"""

    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@yourdomain.com")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Loyalty Program")
        
        if not self.api_key:
            print("WARNING: SENDGRID_API_KEY not set. Email sending will be simulated.")
            self.client = None
        else:
            self.client = SendGridAPIClient(self.api_key)
        
        self.executor = ThreadPoolExecutor(max_workers=5)

    async def send_campaign_email(
        self,
        to_email: str,
        subject: str,
        template_data: Dict,
        template_type: str = "campaign_offer"
    ) -> Dict:
        """
        Send a campaign email to a member

        Args:
            to_email: Recipient email address
            subject: Email subject line
            template_data: Data for personalizing the email
            template_type: Template to use (campaign_offer, welcome, winback, etc.)

        Returns:
            Sending status and details
        """
        try:
            # Get email content from template
            html_content, text_content = self._render_template(template_type, template_data)

            # Send email
            if self.client:
                result = await self._send_email_async(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content
                )
                return result
            else:
                # Simulation mode (no API key)
                return self._simulate_send(to_email, subject, template_data)

        except Exception as e:
            return {
                "status": "error",
                "to_email": to_email,
                "error": str(e),
                "sent_at": datetime.now().isoformat()
            }

    async def send_bulk_campaign(
        self,
        recipients: List[Dict],
        subject: str,
        template_type: str,
        batch_size: int = 100
    ) -> Dict:
        """
        Send campaign emails to multiple recipients in batches

        Args:
            recipients: List of recipient dicts with email and personalization data
            subject: Email subject
            template_type: Template to use
            batch_size: Number of emails per batch

        Returns:
            Summary of sending results
        """
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "errors": []
        }

        # Process in batches to avoid rate limiting
        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            
            # Send batch concurrently
            tasks = [
                self.send_campaign_email(
                    to_email=recipient['email'],
                    subject=subject,
                    template_data=recipient.get('data', {}),
                    template_type=template_type
                )
                for recipient in batch
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count results
            for result in batch_results:
                if isinstance(result, Exception):
                    results['failed'] += 1
                    results['errors'].append(str(result))
                elif result.get('status') == 'sent':
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(result.get('error', 'Unknown error'))

            # Rate limiting pause between batches
            if i + batch_size < len(recipients):
                await asyncio.sleep(1)  # 1 second between batches

        return results

    async def _send_email_async(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> Dict:
        """Send email using SendGrid API (async wrapper)"""
        
        def _send_sync():
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )

            # Add tracking
            message.tracking_settings = {
                "click_tracking": {"enable": True},
                "open_tracking": {"enable": True}
            }

            response = self.client.send(message)
            return response

        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(self.executor, _send_sync)

        return {
            "status": "sent",
            "to_email": to_email,
            "message_id": response.headers.get('X-Message-Id'),
            "status_code": response.status_code,
            "sent_at": datetime.now().isoformat()
        }

    def _render_template(self, template_type: str, data: Dict) -> tuple:
        """
        Render email template with personalization data

        Args:
            template_type: Template name
            data: Personalization data

        Returns:
            Tuple of (html_content, text_content)
        """
        templates = {
            "campaign_offer": self._campaign_offer_template,
            "welcome": self._welcome_template,
            "winback": self._winback_template,
            "bonus_points": self._bonus_points_template,
            "tier_upgrade": self._tier_upgrade_template
        }

        template_func = templates.get(template_type, self._default_template)
        return template_func(data)

    def _campaign_offer_template(self, data: Dict) -> tuple:
        """Campaign offer email template"""
        member_name = data.get('first_name', 'Valued Member')
        campaign_name = data.get('campaign_name', 'Special Offer')
        offer_details = data.get('offer_details', 'Exclusive rewards await you!')
        points_balance = data.get('points_balance', 0)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; background: #f9f9f9; }}
                .offer-box {{ background: white; padding: 20px; margin: 20px 0; 
                             border-left: 4px solid #667eea; }}
                .cta-button {{ display: inline-block; padding: 15px 30px; 
                              background: #667eea; color: white; text-decoration: none; 
                              border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{campaign_name}</h1>
                </div>
                <div class="content">
                    <h2>Hi {member_name}!</h2>
                    <p>We have an exclusive offer just for you:</p>
                    
                    <div class="offer-box">
                        <h3>{offer_details}</h3>
                    </div>

                    <p>Your current points balance: <strong>{points_balance:,} points</strong></p>

                    <a href="#redeem" class="cta-button">Claim Your Offer</a>

                    <p>This is a limited-time offer. Don't miss out!</p>
                </div>
                <div class="footer">
                    <p>© 2026 Loyalty Program. All rights reserved.</p>
                    <p><a href="#unsubscribe">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        text = f"""
        {campaign_name}

        Hi {member_name}!

        We have an exclusive offer just for you:

        {offer_details}

        Your current points balance: {points_balance:,} points

        This is a limited-time offer. Don't miss out!

        Claim your offer: [link]

        ---
        © 2026 Loyalty Program
        Unsubscribe: [link]
        """

        return html, text

    def _welcome_template(self, data: Dict) -> tuple:
        """Welcome email template for new members"""
        member_name = data.get('first_name', 'there')
        welcome_points = data.get('welcome_points', 500)

        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #667eea;">Welcome to Our Loyalty Program!</h1>
                <p>Hi {member_name},</p>
                <p>Thank you for joining! We've added <strong>{welcome_points} bonus points</strong> to your account to get you started.</p>
                <p>Here's how it works:</p>
                <ul>
                    <li>Earn points with every purchase</li>
                    <li>Get exclusive member-only offers</li>
                    <li>Redeem points for rewards</li>
                </ul>
                <a href="#" style="display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px;">Start Shopping</a>
            </div>
        </body>
        </html>
        """

        text = f"""
        Welcome to Our Loyalty Program!

        Hi {member_name},

        Thank you for joining! We've added {welcome_points} bonus points to your account to get you started.

        Here's how it works:
        - Earn points with every purchase
        - Get exclusive member-only offers
        - Redeem points for rewards

        Start shopping: [link]
        """

        return html, text

    def _winback_template(self, data: Dict) -> tuple:
        """Win-back email for inactive members"""
        member_name = data.get('first_name', 'Valued Customer')
        bonus_offer = data.get('bonus_offer', '20% off your next purchase')

        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1 style="color: #667eea;">We Miss You!</h1>
                <p>Hi {member_name},</p>
                <p>It's been a while since we've seen you. We'd love to welcome you back with a special offer:</p>
                <div style="background: #f0f0f0; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h2 style="color: #667eea;">{bonus_offer}</h2>
                </div>
                <p>Your loyalty means everything to us. Come back and see what's new!</p>
                <a href="#" style="display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none;">Redeem Offer</a>
            </div>
        </body>
        </html>
        """

        text = f"""
        We Miss You!

        Hi {member_name},

        It's been a while since we've seen you. We'd love to welcome you back with a special offer:

        {bonus_offer}

        Your loyalty means everything to us. Come back and see what's new!

        Redeem your offer: [link]
        """

        return html, text

    def _bonus_points_template(self, data: Dict) -> tuple:
        """Bonus points campaign template"""
        member_name = data.get('first_name', 'Member')
        multiplier = data.get('multiplier', '2x')
        validity_days = data.get('validity_days', 7)

        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1 style="color: #667eea;">{multiplier} Points Event!</h1>
                <p>Hi {member_name},</p>
                <p>Earn <strong>{multiplier} points</strong> on all purchases for the next {validity_days} days!</p>
                <p>This is your chance to rack up points fast. Don't wait!</p>
                <a href="#" style="display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none;">Shop Now</a>
            </div>
        </body>
        </html>
        """

        text = f"""
        {multiplier} Points Event!

        Hi {member_name},

        Earn {multiplier} points on all purchases for the next {validity_days} days!

        This is your chance to rack up points fast. Don't wait!

        Shop now: [link]
        """

        return html, text

    def _tier_upgrade_template(self, data: Dict) -> tuple:
        """Tier upgrade notification template"""
        member_name = data.get('first_name', 'Member')
        new_tier = data.get('new_tier', 'Gold')

        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h1 style="color: #FFD700;">Congratulations! You've Been Upgraded!</h1>
                <p>Hi {member_name},</p>
                <p>Your loyalty has paid off! You've been upgraded to <strong>{new_tier}</strong> tier.</p>
                <p>Your new benefits include:</p>
                <ul>
                    <li>Higher points earn rate</li>
                    <li>Exclusive {new_tier} member offers</li>
                    <li>Priority customer service</li>
                </ul>
                <a href="#" style="display: inline-block; padding: 12px 24px; background: #FFD700; color: #333; text-decoration: none;">Explore Benefits</a>
            </div>
        </body>
        </html>
        """

        text = f"""
        Congratulations! You've Been Upgraded!

        Hi {member_name},

        Your loyalty has paid off! You've been upgraded to {new_tier} tier.

        Your new benefits include:
        - Higher points earn rate
        - Exclusive {new_tier} member offers
        - Priority customer service

        Explore your benefits: [link]
        """

        return html, text

    def _default_template(self, data: Dict) -> tuple:
        """Default template fallback"""
        return self._campaign_offer_template(data)

    def _simulate_send(self, to_email: str, subject: str, template_data: Dict) -> Dict:
        """Simulate email sending when no API key is configured"""
        return {
            "status": "simulated",
            "to_email": to_email,
            "subject": subject,
            "message": "Email sending simulated (SENDGRID_API_KEY not configured)",
            "template_data": template_data,
            "sent_at": datetime.now().isoformat()
        }


# Singleton instance
email_service = EmailService()
