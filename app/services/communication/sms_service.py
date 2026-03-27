"""
SMS Service using Twilio
Handles campaign SMS and transactional messages
"""
import os
from typing import Dict, List
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor


class SMSService:
    """Twilio SMS service for campaigns and transactional messages"""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.from_number]):
            print("WARNING: Twilio credentials not set. SMS sending will be simulated.")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
        
        self.executor = ThreadPoolExecutor(max_workers=3)

    async def send_campaign_sms(
        self,
        to_number: str,
        message: str,
        template_data: Dict = None
    ) -> Dict:
        """
        Send SMS to a member

        Args:
            to_number: Recipient phone number (E.164 format: +1234567890)
            message: SMS message text
            template_data: Optional data for personalizing the message

        Returns:
            Sending status and details
        """
        try:
            # Personalize message if template data provided
            if template_data:
                message = self._personalize_message(message, template_data)

            # Validate message length (SMS limit: 160 chars for single, 1600 for concatenated)
            if len(message) > 1600:
                return {
                    "status": "error",
                    "error": "Message too long (max 1600 characters)",
                    "to_number": to_number
                }

            # Send SMS
            if self.client:
                result = await self._send_sms_async(to_number, message)
                return result
            else:
                # Simulation mode
                return self._simulate_send(to_number, message)

        except Exception as e:
            return {
                "status": "error",
                "to_number": to_number,
                "error": str(e),
                "sent_at": datetime.now().isoformat()
            }

    async def send_bulk_sms(
        self,
        recipients: List[Dict],
        message_template: str,
        batch_delay: float = 0.5
    ) -> Dict:
        """
        Send SMS to multiple recipients

        Args:
            recipients: List of dicts with 'phone' and optional 'data' for personalization
            message_template: SMS message template
            batch_delay: Delay between messages to avoid rate limiting (seconds)

        Returns:
            Summary of sending results
        """
        results = {
            "total": len(recipients),
            "sent": 0,
            "failed": 0,
            "errors": [],
            "cost_estimate": 0.0
        }

        for recipient in recipients:
            phone = recipient.get('phone')
            data = recipient.get('data', {})

            result = await self.send_campaign_sms(
                to_number=phone,
                message=message_template,
                template_data=data
            )

            if result.get('status') in ['sent', 'queued', 'simulated']:
                results['sent'] += 1
                # Estimate cost: $0.0075 per SMS (Twilio pricing)
                results['cost_estimate'] += 0.0075
            else:
                results['failed'] += 1
                results['errors'].append({
                    "phone": phone,
                    "error": result.get('error')
                })

            # Rate limiting
            await asyncio.sleep(batch_delay)

        return results

    async def _send_sms_async(self, to_number: str, message: str) -> Dict:
        """Send SMS using Twilio API (async wrapper)"""
        
        def _send_sync():
            response = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return response

        # Run in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(self.executor, _send_sync)

        return {
            "status": response.status,  # queued, sent, delivered, etc.
            "to_number": to_number,
            "message_sid": response.sid,
            "segments": response.num_segments,
            "price": response.price,
            "sent_at": datetime.now().isoformat()
        }

    def _personalize_message(self, template: str, data: Dict) -> str:
        """
        Personalize SMS message with member data

        Args:
            template: Message template with {placeholders}
            data: Personalization data

        Returns:
            Personalized message
        """
        try:
            return template.format(**data)
        except KeyError as e:
            print(f"Missing template variable: {e}")
            return template

    def get_message_templates(self) -> Dict[str, str]:
        """
        Get predefined SMS templates

        Returns:
            Dictionary of template name -> template string
        """
        return {
            "campaign_offer": (
                "Hi {first_name}! Exclusive offer: {offer_details}. "
                "Your points: {points_balance}. Reply STOP to opt out."
            ),
            "welcome": (
                "Welcome {first_name}! You've earned {welcome_points} bonus points. "
                "Start shopping to earn more! Reply STOP to opt out."
            ),
            "winback": (
                "We miss you {first_name}! Here's {bonus_offer} to welcome you back. "
                "Shop now! Reply STOP to opt out."
            ),
            "bonus_points": (
                "🎉 {first_name}, earn {multiplier} points on all purchases for {validity_days} days! "
                "Don't miss out! Reply STOP to opt out."
            ),
            "tier_upgrade": (
                "Congrats {first_name}! You've been upgraded to {new_tier} tier! "
                "Enjoy exclusive benefits. Reply STOP to opt out."
            ),
            "points_reminder": (
                "Hi {first_name}, you have {points_balance} points! "
                "Redeem them for rewards. Reply STOP to opt out."
            ),
            "expiring_points": (
                "⚠️ {first_name}, {expiring_points} points expire in {days_left} days! "
                "Use them now. Reply STOP to opt out."
            )
        }

    def _simulate_send(self, to_number: str, message: str) -> Dict:
        """Simulate SMS sending when credentials not configured"""
        return {
            "status": "simulated",
            "to_number": to_number,
            "message": message,
            "message_length": len(message),
            "segments": (len(message) // 160) + 1,
            "note": "SMS sending simulated (Twilio credentials not configured)",
            "sent_at": datetime.now().isoformat()
        }

    async def check_delivery_status(self, message_sid: str) -> Dict:
        """
        Check delivery status of sent SMS

        Args:
            message_sid: Twilio message SID

        Returns:
            Delivery status information
        """
        if not self.client:
            return {"error": "Twilio client not configured"}

        try:
            def _check_sync():
                return self.client.messages(message_sid).fetch()

            loop = asyncio.get_event_loop()
            message = await loop.run_in_executor(self.executor, _check_sync)

            return {
                "sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": str(message.date_sent),
                "error_code": message.error_code,
                "error_message": message.error_message
            }

        except TwilioRestException as e:
            return {
                "error": str(e),
                "message_sid": message_sid
            }


# Singleton instance
sms_service = SMSService()
