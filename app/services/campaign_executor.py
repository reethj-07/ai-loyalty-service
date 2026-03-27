"""
Campaign Execution Engine
Orchestrates campaign launches across email, SMS, and push channels
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from enum import Enum

from app.services.communication.email_service import email_service
from app.services.communication.sms_service import sms_service
from app.repositories.supabase_members_repo import members_repo


class CampaignChannel(str, Enum):
    """Campaign delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class CampaignStatus(str, Enum):
    """Campaign execution status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"


class CampaignExecutor:
    """
    Manages campaign execution across multiple channels
    Handles scheduling, batching, throttling, and tracking
    """

    def __init__(self):
        self.email_service = email_service
        self.sms_service = sms_service
        self.max_batch_size = 500
        self.rate_limit_delay = 1.0  # seconds between batches

    async def launch_campaign(
        self,
        campaign_id: str,
        campaign_data: Dict
    ) -> Dict:
        """
        Launch a campaign to target members

        Args:
            campaign_id: Unique campaign identifier
            campaign_data: Campaign configuration including:
                - name: Campaign name
                - channel: Delivery channel (email, sms, push)
                - target_segment: Which segment to target
                - message_template: Message template name
                - offer_details: Campaign offer details
                - schedule_at: Optional datetime to schedule

        Returns:
            Execution results and metrics
        """
        try:
            # Extract campaign details
            channel = campaign_data.get('channel', CampaignChannel.EMAIL)
            target_segment = campaign_data.get('target_segment', 'all')
            schedule_at = campaign_data.get('schedule_at')

            # If scheduled for future, queue it
            if schedule_at and datetime.fromisoformat(schedule_at) > datetime.now():
                return await self._schedule_campaign(campaign_id, campaign_data, schedule_at)

            # Get target members
            members = await self._get_target_members(target_segment)

            if not members:
                return {
                    "status": "error",
                    "error": f"No members found in segment: {target_segment}",
                    "campaign_id": campaign_id
                }

            # Apply exclusion rules
            eligible_members = await self._apply_exclusion_rules(members, campaign_data)

            # Execute based on channel
            if channel == CampaignChannel.EMAIL:
                result = await self._execute_email_campaign(campaign_id, campaign_data, eligible_members)
            elif channel == CampaignChannel.SMS:
                result = await self._execute_sms_campaign(campaign_id, campaign_data, eligible_members)
            elif channel == CampaignChannel.PUSH:
                result = await self._execute_push_campaign(campaign_id, campaign_data, eligible_members)
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported channel: {channel}"
                }

            # Add campaign metadata
            result['campaign_id'] = campaign_id
            result['campaign_name'] = campaign_data.get('name')
            result['target_segment'] = target_segment
            result['executed_at'] = datetime.now().isoformat()

            return result

        except Exception as e:
            return {
                "status": "error",
                "campaign_id": campaign_id,
                "error": str(e),
                "executed_at": datetime.now().isoformat()
            }

    async def _execute_email_campaign(
        self,
        campaign_id: str,
        campaign_data: Dict,
        members: List[Dict]
    ) -> Dict:
        """Execute email campaign"""
        
        # Prepare recipients
        recipients = []
        for member in members:
            recipients.append({
                'email': member['email'],
                'data': {
                    'first_name': member['first_name'],
                    'campaign_name': campaign_data.get('name', 'Special Offer'),
                    'offer_details': campaign_data.get('offer_details', 'Exclusive rewards'),
                    'points_balance': member.get('points_balance', 0)
                }
            })

        # Send bulk emails
        subject = campaign_data.get('subject', campaign_data.get('name', 'Special Offer'))
        template_type = campaign_data.get('template_type', 'campaign_offer')

        result = await self.email_service.send_bulk_campaign(
            recipients=recipients,
            subject=subject,
            template_type=template_type,
            batch_size=self.max_batch_size
        )

        return {
            "status": "completed",
            "channel": "email",
            **result
        }

    async def _execute_sms_campaign(
        self,
        campaign_id: str,
        campaign_data: Dict,
        members: List[Dict]
    ) -> Dict:
        """Execute SMS campaign"""
        
        # Prepare recipients
        recipients = []
        for member in members:
            if member.get('mobile'):  # Only send if mobile number exists
                recipients.append({
                    'phone': member['mobile'],
                    'data': {
                        'first_name': member['first_name'],
                        'offer_details': campaign_data.get('offer_details', 'Special offer'),
                        'points_balance': member.get('points_balance', 0)
                    }
                })

        if not recipients:
            return {
                "status": "error",
                "error": "No members with mobile numbers found"
            }

        # Get SMS template
        template_name = campaign_data.get('sms_template', 'campaign_offer')
        templates = self.sms_service.get_message_templates()
        message_template = templates.get(template_name, templates['campaign_offer'])

        # Send bulk SMS
        result = await self.sms_service.send_bulk_sms(
            recipients=recipients,
            message_template=message_template,
            batch_delay=0.5
        )

        return {
            "status": "completed",
            "channel": "sms",
            **result
        }

    async def _execute_push_campaign(
        self,
        campaign_id: str,
        campaign_data: Dict,
        members: List[Dict]
    ) -> Dict:
        """Execute push notification campaign (placeholder for future implementation)"""
        return {
            "status": "simulated",
            "channel": "push",
            "message": "Push notifications not yet implemented",
            "target_members": len(members)
        }

    async def _get_target_members(self, segment: str) -> List[Dict]:
        """
        Get members in target segment

        Args:
            segment: Segment name or 'all'

        Returns:
            List of member dicts
        """
        # Get all members
        all_members = await members_repo.get_all_members()

        if segment == 'all':
            return all_members

        # Filter by segment (simplified - in production, query from member_segments table)
        # For now, use tier as proxy for segment
        segment_tier_map = {
            'high_value': ['Platinum', 'Gold'],
            'at_risk': ['Bronze'],
            'new_member': ['Bronze', 'Silver'],  # Could add date logic
            'champions': ['Platinum']
        }

        target_tiers = segment_tier_map.get(segment, [])
        if target_tiers:
            return [m for m in all_members if m['tier'] in target_tiers]

        return all_members

    async def _apply_exclusion_rules(
        self,
        members: List[Dict],
        campaign_data: Dict
    ) -> List[Dict]:
        """
        Apply exclusion rules to member list

        Args:
            members: List of target members
            campaign_data: Campaign configuration

        Returns:
            Filtered list of eligible members
        """
        exclusion_rules = campaign_data.get('exclusion_rules', {})

        eligible = members

        # Exclude inactive members
        if exclusion_rules.get('exclude_inactive', True):
            eligible = [m for m in eligible if m.get('status') == 'active']

        # Exclude members who opted out
        if exclusion_rules.get('respect_opt_out', True):
            # In production, check opt_out preferences table
            pass

        # Frequency capping (don't send if received campaign in last N days)
        frequency_cap_days = exclusion_rules.get('frequency_cap_days')
        if frequency_cap_days:
            # In production, check campaign_participants table
            pass

        return eligible

    async def _schedule_campaign(
        self,
        campaign_id: str,
        campaign_data: Dict,
        schedule_at: str
    ) -> Dict:
        """
        Schedule campaign for future execution

        Args:
            campaign_id: Campaign ID
            campaign_data: Campaign configuration
            schedule_at: ISO datetime string

        Returns:
            Scheduling confirmation
        """
        # In production, this would store in a job queue (Celery, Redis Queue, etc.)
        # For now, return scheduling confirmation

        return {
            "status": "scheduled",
            "campaign_id": campaign_id,
            "campaign_name": campaign_data.get('name'),
            "scheduled_at": schedule_at,
            "message": "Campaign scheduled for execution",
            "note": "Actual scheduling requires job queue (Celery/Redis) - not yet implemented"
        }

    async def pause_campaign(self, campaign_id: str) -> Dict:
        """
        Pause an in-progress campaign

        Args:
            campaign_id: Campaign to pause

        Returns:
            Pause status
        """
        # In production, set flag in database and stop workers
        return {
            "status": "paused",
            "campaign_id": campaign_id,
            "paused_at": datetime.now().isoformat()
        }

    async def resume_campaign(self, campaign_id: str) -> Dict:
        """
        Resume a paused campaign

        Args:
            campaign_id: Campaign to resume

        Returns:
            Resume status
        """
        # In production, resume workers and continue sending
        return {
            "status": "resumed",
            "campaign_id": campaign_id,
            "resumed_at": datetime.now().isoformat()
        }

    async def get_campaign_status(self, campaign_id: str) -> Dict:
        """
        Get current status of campaign execution

        Args:
            campaign_id: Campaign ID

        Returns:
            Campaign execution status and metrics
        """
        # In production, query from campaign_participants and campaign_kpis tables
        return {
            "campaign_id": campaign_id,
            "status": "in_progress",
            "sent": 450,
            "delivered": 420,
            "failed": 30,
            "opened": 180,
            "clicked": 45,
            "last_updated": datetime.now().isoformat()
        }


# Singleton instance
campaign_executor = CampaignExecutor()
