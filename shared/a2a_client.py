import logging
import uuid

import httpx

from shared.agent_discovery import discover_agent
from shared.agent_registry import get_agent_url
from shared.config import REQUEST_TIMEOUT
from shared.exceptions import (
    AgentUnavailableError,
    AgentTimeoutError,
    AgentResponseError,
    AgentRPCError,
)


logger = logging.getLogger(__name__)


async def call_agent_parts(
    card_url: str,
    user_message: str,
    timeout: float = REQUEST_TIMEOUT
) -> list[dict]:

    url = await discover_agent(card_url)

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "ROLE_USER",
                "parts": [{"text": user_message}]
            }
        }
    }

    logger.debug("Sending A2A request")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:

            response = await client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "A2A-Version": "1.0"
                }
            )

            response.raise_for_status()

    except httpx.TimeoutException as exc:
        logger.error("Agent request timed out")
        raise AgentTimeoutError(
            "Agent request timed out."
        ) from exc

    except httpx.RequestError as exc:
        logger.error("Agent connection failed")
        raise AgentUnavailableError(
            "Unable to connect to agent."
        ) from exc

    except httpx.HTTPStatusError as exc:
        logger.error(
            "Agent HTTP error: %s",
            exc.response.status_code
        )
        raise

    try:
        result = response.json()

    except ValueError as exc:
        logger.error("Invalid agent response JSON")
        raise AgentResponseError(
            "Invalid agent response JSON."
        ) from exc

    if not isinstance(result, dict):
        logger.error("Invalid JSON-RPC response")
        raise AgentResponseError(
            "Invalid JSON-RPC response."
        )

    if "error" in result:
        logger.error("Agent returned a JSON-RPC error")
        raise AgentRPCError(
            "Agent returned a JSON-RPC error."
        )

    try:
        parts = result["result"]["message"]["parts"]

    except (KeyError, TypeError) as exc:
        logger.error("Missing response parts")
        raise AgentResponseError(
            "Missing response parts."
        ) from exc

    if (
        not isinstance(parts, list)
        or not parts
        or not all(isinstance(part, dict) for part in parts)
    ):
        logger.error("Invalid response parts")
        raise AgentResponseError(
            "Invalid response parts."
        )

    logger.info("A2A request successful")

    return parts


async def call_agent(
    card_url: str,
    user_message: str,
    timeout: float = REQUEST_TIMEOUT
) -> str:

    parts = await call_agent_parts(
        card_url,
        user_message,
        timeout
    )

    for part in parts:
        if isinstance(part.get("text"), str):
            return part["text"]

    logger.error("Text response not found")

    raise AgentResponseError(
        "Text response not found."
    )


async def call_agent_by_name(
    agent_name: str,
    user_message: str,
    timeout: float = REQUEST_TIMEOUT
) -> str:

    card_url = (
        get_agent_url(agent_name)
        + "/.well-known/agent-card.json"
    )

    return await call_agent(
        card_url,
        user_message,
        timeout
    )


async def call_agent_data_by_name(
    agent_name: str,
    user_message: str,
    timeout: float = REQUEST_TIMEOUT
) -> dict:

    card_url = (
        get_agent_url(agent_name)
        + "/.well-known/agent-card.json"
    )

    parts = await call_agent_parts(
        card_url,
        user_message,
        timeout
    )

    for part in parts:

        if "data" not in part:
            continue

        data = part["data"]

        if (
            not isinstance(data, dict)
            or not isinstance(data.get("agent"), str)
            or not isinstance(data.get("success"), bool)
            or not isinstance(data.get("message"), str)
            or not isinstance(data.get("data"), dict)
            or not (
                data.get("error_code") is None
                or isinstance(data.get("error_code"), str)
            )
            or set(data) - {
                "agent",
                "success",
                "message",
                "data",
                "error_code"
            }
        ):
            logger.error("Invalid structured response")
            raise AgentResponseError(
                "Invalid structured response."
            )

        return data

    logger.error("Structured response not found")

    raise AgentResponseError(
        "Structured response not found."
    )