import asyncio
import logging

import httpx

from shared.config import load_llm_config
from shared.exceptions import (
    LLMDisabledError,
    LLMResponseError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from shared.intent_classifier import classify_intent


logger = logging.getLogger(__name__)

_FALLBACK_REASONS = {
    LLMDisabledError: "llm_disabled",
    LLMUnavailableError: "llm_unavailable",
    LLMTimeoutError: "llm_timeout",
    LLMResponseError: "llm_response_error",
    httpx.HTTPStatusError: "llm_http_error",
}
_RECOVERABLE_ERRORS = tuple(_FALLBACK_REASONS)


async def resolve_intent(user_message: str) -> str:
    """Resolve intent for a customer message already validated by the Supervisor."""
    config = load_llm_config()
    source = "keyword"
    fallback_reason = None

    if config.enabled:
        deadline = asyncio.timeout(config.timeout)
        try:
            async with deadline:
                intent = await classify_intent(user_message)
        except TimeoutError as exc:
            if not deadline.expired() or not isinstance(exc.__cause__, asyncio.CancelledError):
                raise
            fallback_reason = "classification_deadline"
        except _RECOVERABLE_ERRORS as exc:
            fallback_reason = next(
                reason for error_type, reason in _FALLBACK_REASONS.items()
                if isinstance(exc, error_type)
            )
        else:
            if deadline.expired():
                fallback_reason = "classification_deadline"
            else:
                source = "llm"

    if fallback_reason is not None:
        logger.warning("Using keyword fallback: fallback_reason=%s", fallback_reason)
        source = "keyword_fallback"
    if source != "llm":
        intent = detect_intent(user_message)

    logger.info("Resolved intent: intent=%s routing_source=%s", intent, source)
    return intent


def detect_intent(user_message: str) -> str:
    message = user_message.lower()

    if any(word in message for word in [
        "refund", "cancel"
    ]):
        return "refund"

    if any(word in message for word in [
        "order", "tracking", "track"
    ]):
        return "order"

    if any(word in message for word in [
        "product", "price", "stock",
        "laptop", "keyboard", "mouse",
        "recommend", "available", "how much"
    ]):
        return "product"

    return "support"