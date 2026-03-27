# services/mock_ai_engine.py
class MockAIEngine:
    async def generate(self, behavior_signal: dict) -> dict:
        return {
            "behavior_change": behavior_signal,
            "suggested_campaign": {
                "objective": "retention",
                "audience_hint": "recently inactive users",
                "offer_hint": "bonus points",
                "timing_hint": "within 48 hours"
            },
            "roi_score": 0.63
        }
