import json
import os
from typing import Any

from langchain_core.messages import AIMessage

from app.core.config import settings


class FallbackChatModel:
    """Minimal fallback model when no provider key is configured."""

    async def ainvoke(self, _messages: Any, **_kwargs: Any) -> AIMessage:
        return AIMessage(
            content=json.dumps(
                {
                    "summary": "Fallback reasoning path used",
                    "patterns": ["No external LLM key configured"],
                    "recommended_campaign": "Re-engagement follow-up",
                    "confidence": 0.55,
                }
            )
        )



def get_llm(streaming: bool = False):
    """
    Returns the best available free LLM.
    Priority: Groq (llama-3.3-70b-versatile, free tier) → Anthropic (claude-haiku, cheapest)
    Reads LLM_PROVIDER env var: "groq" | "anthropic"
    """
    provider = (settings.llm_provider or os.getenv("LLM_PROVIDER", "groq")).lower()

    if provider == "groq":
        groq_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
        if groq_key:
            from langchain_groq import ChatGroq

            return ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=groq_key,
                temperature=0.2,
                streaming=streaming,
            )

        anthropic_key = settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model="claude-3-5-haiku-latest",
                anthropic_api_key=anthropic_key,
                temperature=0.2,
                streaming=streaming,
            )

        return FallbackChatModel()

    if provider == "anthropic":
        anthropic_key = settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                model="claude-3-5-haiku-latest",
                anthropic_api_key=anthropic_key,
                temperature=0.2,
                streaming=streaming,
            )

        groq_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
        if groq_key:
            from langchain_groq import ChatGroq

            return ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=groq_key,
                temperature=0.2,
                streaming=streaming,
            )

        return FallbackChatModel()

    return FallbackChatModel()
