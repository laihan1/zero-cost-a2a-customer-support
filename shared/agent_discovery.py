import logging

import httpx

from shared.config import DISCOVERY_TIMEOUT
from shared.exceptions import (
    AgentUnavailableError,
    AgentTimeoutError,
    AgentDiscoveryError,
)


logger = logging.getLogger(__name__)


async def discover_agent(card_url: str) -> str:

    logger.debug("Starting agent discovery")

    try:
        async with httpx.AsyncClient(
            timeout=DISCOVERY_TIMEOUT
        ) as client:

            response = await client.get(card_url)
            response.raise_for_status()

    except httpx.TimeoutException as exc:
        logger.error("Agent discovery timed out")
        raise AgentTimeoutError(
            "Agent discovery timed out."
        ) from exc

    except httpx.RequestError as exc:
        logger.error("Agent discovery connection failed")
        raise AgentUnavailableError(
            "Unable to connect to agent."
        ) from exc

    except httpx.HTTPStatusError as exc:
        logger.error(
            "Agent discovery HTTP error: %s",
            exc.response.status_code,
        )
        raise

    try:
        agent_card = response.json()

    except ValueError as exc:
        logger.error("Invalid agent card JSON")
        raise AgentDiscoveryError(
            "Invalid agent card JSON."
        ) from exc

    if not isinstance(agent_card, dict):
        logger.error("Invalid agent card format")
        raise AgentDiscoveryError(
            "Invalid agent card format."
        )

    interfaces = agent_card.get("supportedInterfaces", [])

    if not isinstance(interfaces, list):
        logger.error("Invalid supported interfaces")
        raise AgentDiscoveryError(
            "Invalid supported interfaces."
        )

    for interface in interfaces:

        if not isinstance(interface, dict):
            continue

        url = interface.get("url")

        if (
            interface.get("protocolBinding") == "JSONRPC"
            and interface.get("protocolVersion") == "1.0"
            and isinstance(url, str)
            and url.strip()
        ):
            logger.info("Agent discovery successful")
            return url

    logger.warning("No compatible JSON-RPC interface found")

    raise AgentDiscoveryError(
        "No compatible JSON-RPC interface found."
    )