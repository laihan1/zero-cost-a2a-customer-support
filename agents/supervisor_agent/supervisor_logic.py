import logging

from shared.config import load_llm_config
from shared.intent_classifier import classify_intent


logger = logging.getLogger(__name__)


async def resolve_intent(user_message: str) -> str:
    """Resolve intent for a customer message already validated by the Supervisor."""
    if load_llm_config().enabled:
        intent = await classify_intent(user_message)
        source = "llm"
    else:
        intent = detect_intent(user_message)
        source = "keyword"

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