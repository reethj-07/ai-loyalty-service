from typing import Dict, List
from app.automation.rules import CampaignRule, HighValueTransactionRule


class AutomationEngine:
    def __init__(self):
        self.rules: List[CampaignRule] = [
            HighValueTransactionRule(),
        ]

    def evaluate(self, context: Dict) -> List[Dict]:
        proposals = []

        for rule in self.rules:
            if rule.applies(context):
                proposals.append(rule.propose(context))

        return proposals
