from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

CAMPAIGN_PROPOSALS_TOTAL = Counter(
    "campaign_proposals_total", "Total AI proposals generated", ["segment", "status"]
)
BEHAVIORAL_ALERTS_TOTAL = Counter(
    "behavioral_alerts_total", "Total behavioral detections", ["alert_type"]
)
MEMBER_SEGMENTATION_CHANGES = Counter(
    "member_segment_changes_total", "Segment transitions", ["from_segment", "to_segment"]
)
LLM_LATENCY_SECONDS = Histogram(
    "llm_request_latency_seconds", "LLM response time", ["provider", "model"]
)
LLM_TOKENS_USED = Counter(
    "llm_tokens_total", "Total LLM tokens consumed", ["provider", "type"]
)
ACTIVE_CAMPAIGNS = Gauge("active_campaigns_count", "Currently running campaigns")


def prometheus_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
