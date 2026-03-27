from fastapi import APIRouter

router = APIRouter(prefix="/voice", tags=["voice-control"])


@router.post("/interpret")
def interpret_voice_command(transcript: str):
    """
    Placeholder for Whisper / Speech-to-Text output
    """
    return {
        "intent": "modify_campaign",
        "updates": {
            "validity_hours": 96
        },
        "confidence": 0.91
    }
