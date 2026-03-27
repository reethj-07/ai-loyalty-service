"""
AI Message Generation Service
Generates personalized campaign messages using LLM
"""
from typing import Dict, List, Optional
import os
import asyncio
import json


class AIMessageGenerator:
    """
    Generates campaign messages using AI (Claude API or fallback templates)
    """

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.use_ai = bool(self.api_key)

        # Fallback to template-based generation if no API key
        if not self.use_ai:
            print("⚠️  No ANTHROPIC_API_KEY found - using template-based messages")

    async def generate_campaign_message(
        self,
        segment: str,
        campaign_type: str,
        behavior: str,
        channel: str = "email",
        brand_name: str = "Loyalty Pro",
        incentive: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate personalized campaign message

        Args:
            segment: Customer segment (high_value, at_risk, new_customers, etc.)
            campaign_type: Type of campaign (welcome, winback, promo, bonus)
            behavior: Detected behavior (declining_engagement, high_value, etc.)
            channel: Communication channel (email, sms, push)
            brand_name: Company/brand name
            incentive: Incentive description (e.g., "500 bonus points")

        Returns:
            dict: Generated message with subject and body
        """
        if self.use_ai:
            return await self._generate_with_ai(
                segment, campaign_type, behavior, channel, brand_name, incentive
            )
        else:
            return self._generate_with_template(
                segment, campaign_type, behavior, channel, brand_name, incentive
            )

    async def _generate_with_ai(
        self,
        segment: str,
        campaign_type: str,
        behavior: str,
        channel: str,
        brand_name: str,
        incentive: Optional[str]
    ) -> Dict[str, str]:
        """
        Generate message using Claude API

        Args:
            segment: Customer segment
            campaign_type: Campaign type
            behavior: Detected behavior
            channel: Channel
            brand_name: Brand name
            incentive: Incentive offer

        Returns:
            dict: Generated message
        """
        try:
            # Attempt to use Anthropic API
            try:
                from anthropic import Anthropic
            except ImportError:
                print("⚠️  anthropic package not installed - using templates")
                return self._generate_with_template(
                    segment, campaign_type, behavior, channel, brand_name, incentive
                )

            client = Anthropic(api_key=self.api_key)

            # Craft prompt for message generation
            prompt = self._build_generation_prompt(
                segment, campaign_type, behavior, channel, brand_name, incentive
            )

            # Call Claude API
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            response_text = message.content[0].text

            # Extract subject and body
            return self._parse_ai_response(response_text, channel)

        except Exception as e:
            print(f"AI generation error: {e}")
            # Fallback to templates
            return self._generate_with_template(
                segment, campaign_type, behavior, channel, brand_name, incentive
            )

    def _build_generation_prompt(
        self,
        segment: str,
        campaign_type: str,
        behavior: str,
        channel: str,
        brand_name: str,
        incentive: Optional[str]
    ) -> str:
        """Build prompt for AI message generation"""

        # Channel-specific constraints
        char_limits = {
            "sms": "Keep message under 160 characters.",
            "email": "Create a compelling subject line and email body (2-3 paragraphs).",
            "push": "Keep message under 100 characters for mobile notification."
        }

        constraint = char_limits.get(channel, "Create an engaging message.")

        prompt = f"""Generate a personalized marketing campaign message for a loyalty program.

**Context:**
- Brand: {brand_name}
- Customer Segment: {segment}
- Campaign Type: {campaign_type}
- Detected Behavior: {behavior}
- Channel: {channel}
- Incentive: {incentive or "Special offer"}

**Requirements:**
- {constraint}
- Tone: Friendly, personalized, and motivating
- Include clear call-to-action
- Emphasize the value of the offer
- Make customer feel appreciated

**Format your response as JSON:**
{{
  "subject": "Subject line here (for email/push)",
  "body": "Message body here",
  "cta": "Call to action text"
}}

Generate the message now:"""

        return prompt

    def _parse_ai_response(self, response_text: str, channel: str) -> Dict[str, str]:
        """Parse AI response into structured message"""
        try:
            # Try to parse as JSON
            if "{" in response_text and "}" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)

                return {
                    "subject": data.get("subject", "Special Offer Just for You!"),
                    "body": data.get("body", response_text),
                    "cta": data.get("cta", "Claim Offer"),
                    "channel": channel,
                    "generated_by": "ai"
                }

        except Exception as e:
            print(f"Error parsing AI response: {e}")

        # Fallback: use entire response as body
        return {
            "subject": "Special Offer for You!",
            "body": response_text,
            "cta": "Learn More",
            "channel": channel,
            "generated_by": "ai"
        }

    def _generate_with_template(
        self,
        segment: str,
        campaign_type: str,
        behavior: str,
        channel: str,
        brand_name: str,
        incentive: Optional[str]
    ) -> Dict[str, str]:
        """
        Generate message using predefined templates

        Args:
            segment: Customer segment
            campaign_type: Campaign type
            behavior: Behavior
            channel: Channel
            brand_name: Brand name
            incentive: Incentive

        Returns:
            dict: Template-based message
        """
        # Template library
        templates = {
            "welcome": {
                "email": {
                    "subject": f"Welcome to {brand_name}! 🎉",
                    "body": f"Welcome to the {brand_name} family! We're thrilled to have you join us. As a special welcome gift, {incentive or 'enjoy exclusive benefits'}. Start earning rewards with every purchase!",
                    "cta": "Start Shopping"
                },
                "sms": {
                    "subject": "Welcome!",
                    "body": f"Welcome to {brand_name}! {incentive or 'Earn rewards'} on your first purchase. Reply START to get offers.",
                    "cta": "Reply START"
                },
                "push": {
                    "subject": f"Welcome to {brand_name}!",
                    "body": f"{incentive or 'Special welcome gift'} waiting for you! Tap to claim.",
                    "cta": "Claim Now"
                }
            },
            "winback": {
                "email": {
                    "subject": f"We miss you at {brand_name}! 😊",
                    "body": f"It's been a while since your last visit to {brand_name}. We'd love to see you again! Come back and {incentive or 'enjoy a special offer just for you'}. Your loyalty means everything to us.",
                    "cta": "Come Back"
                },
                "sms": {
                    "subject": "We miss you!",
                    "body": f"We miss you! Come back to {brand_name} and get {incentive or 'a special surprise'}. Limited time offer!",
                    "cta": "Shop Now"
                },
                "push": {
                    "subject": "We miss you!",
                    "body": f"Your {brand_name} rewards are waiting! {incentive or 'Special offer'} inside.",
                    "cta": "Return"
                }
            },
            "promo": {
                "email": {
                    "subject": f"Exclusive Offer: {incentive or 'Special Deal'} at {brand_name}!",
                    "body": f"Don't miss out on this exclusive opportunity! For a limited time, {incentive or 'enjoy special savings'}. This offer is reserved just for valued customers like you.",
                    "cta": "Shop Now"
                },
                "sms": {
                    "subject": "Exclusive Offer",
                    "body": f"Flash sale! {incentive or 'Special deal'} at {brand_name}. Limited time. Shop now!",
                    "cta": "Shop"
                },
                "push": {
                    "subject": "Flash Sale!",
                    "body": f"{incentive or 'Exclusive deal'} ends soon! Tap to save.",
                    "cta": "Shop Now"
                }
            },
            "bonus": {
                "email": {
                    "subject": f"Bonus Rewards Alert! 🎁",
                    "body": f"Great news! You've earned {incentive or 'bonus rewards'} at {brand_name}! Your loyalty deserves to be rewarded. Use your points on your next purchase and enjoy even more benefits.",
                    "cta": "View Rewards"
                },
                "sms": {
                    "subject": "Bonus Rewards!",
                    "body": f"🎁 {incentive or 'Bonus points'} added to your {brand_name} account! Use them today.",
                    "cta": "Use Points"
                },
                "push": {
                    "subject": "Bonus Rewards Earned!",
                    "body": f"{incentive or 'Extra points'} just for you! Check your balance.",
                    "cta": "View"
                }
            },
            "tier_upgrade": {
                "email": {
                    "subject": f"Congratulations! You've Been Upgraded! 🌟",
                    "body": f"Amazing news! You've reached a new tier in the {brand_name} loyalty program. {incentive or 'Enjoy exclusive VIP benefits'} and even more rewards. Thank you for your continued loyalty!",
                    "cta": "Explore Benefits"
                },
                "sms": {
                    "subject": "You're Upgraded!",
                    "body": f"🌟 Congrats! New tier unlocked at {brand_name}. {incentive or 'VIP perks'} now available!",
                    "cta": "See Perks"
                },
                "push": {
                    "subject": "Tier Upgrade!",
                    "body": f"You've been upgraded! {incentive or 'New benefits'} unlocked.",
                    "cta": "Explore"
                }
            },
            "general": {
                "email": {
                    "subject": f"Something Special from {brand_name}",
                    "body": f"We have something special for you! {incentive or 'Exclusive offer'} available now. Don't miss this opportunity to save and earn more rewards.",
                    "cta": "Learn More"
                },
                "sms": {
                    "subject": "Special Offer",
                    "body": f"{brand_name}: {incentive or 'Special offer'} for you. Limited time!",
                    "cta": "Details"
                },
                "push": {
                    "subject": "Special Offer",
                    "body": f"{incentive or 'New offer'} from {brand_name}. Tap to view.",
                    "cta": "View"
                }
            }
        }

        # Get appropriate template
        campaign_templates = templates.get(campaign_type, templates["general"])
        template = campaign_templates.get(channel, campaign_templates["email"])

        return {
            **template,
            "channel": channel,
            "generated_by": "template"
        }

    async def generate_batch_messages(
        self,
        campaign_requests: List[Dict]
    ) -> List[Dict]:
        """
        Generate multiple messages in batch

        Args:
            campaign_requests: List of campaign parameters

        Returns:
            list: Generated messages
        """
        tasks = [
            self.generate_campaign_message(**request)
            for request in campaign_requests
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        messages = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error generating message {i}: {result}")
                # Fallback message
                messages.append({
                    "subject": "Special Offer",
                    "body": "We have a special offer for you!",
                    "cta": "Learn More",
                    "error": str(result)
                })
            else:
                messages.append(result)

        return messages


# Singleton instance
_message_generator = None


def get_message_generator() -> AIMessageGenerator:
    """Get singleton instance of message generator"""
    global _message_generator
    if _message_generator is None:
        _message_generator = AIMessageGenerator()
    return _message_generator
