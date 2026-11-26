import logging

import httpx

from shared.config import load_llm_config
from shared.exceptions import (
    LLMDisabledError,
    LLMResponseError,
    LLMTimeoutError,
    LLMUnavailableError,
)


logger = logging.getLogger(__name__)


async def chat(
    messages: list[dict],
    *,
    response_format: dict | None = None,
    require_complete: bool = False,
) -> str:
    """Return Ollama message content, optionally requiring normal completion."""
    config = load_llm_config()
    if not config.enabled:
        raise LLMDisabledError("Local LLM is disabled.")

    payload = {
        "model": config.model,
        "messages": messages,
        "stream": False,
        "think": config.think,
        "keep_alive": config.keep_alive,
        "options": {
            "temperature": config.temperature,
            "num_ctx": config.num_ctx,
            "num_predict": config.num_predict,
        },
    }
    if response_format is not None:
        payload["format"] = response_format

    logger.debug("Sending local LLM chat request")
    try:
        async with httpx.AsyncClient(
            timeout=config.timeout,
            trust_env=False,
            follow_redirects=False,
        ) as client:
            response = await client.post(f"{config.base_url}/api/chat", json=payload)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        logger.error("Local LLM request timed out")
        raise LLMTimeoutError("Local LLM request timed out.") from exc
    except httpx.RequestError as exc:
        logger.error("Local LLM connection failed")
        raise LLMUnavailableError("Unable to reach local LLM.") from exc
    except httpx.HTTPStatusError as exc:
        logger.error("Local LLM HTTP error: %s", exc.response.status_code)
        raise

    try:
        result = response.json()
    except ValueError:
        logger.error("Invalid local LLM response JSON")
        raise LLMResponseError("Invalid local LLM response JSON.") from None

    if not isinstance(result, dict):
        logger.error("Invalid local LLM response envelope")
        raise LLMResponseError("Expected a local LLM response object.")
    if "error" in result:
        logger.error("Local LLM returned an API error")
        raise LLMResponseError("Local LLM returned an API error.")

    if require_complete and (
        result.get("done") is not True or result.get("done_reason") != "stop"
    ):
        logger.error("Invalid local LLM completion metadata")
        raise LLMResponseError("Expected normal local LLM completion.")

    message = result.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        logger.error("Invalid local LLM message content")
        raise LLMResponseError("Expected non-empty local LLM message content.")

    logger.debug("Local LLM chat request succeeded")
    return content
