import httpx
import uuid

from shared.agent_discovery import discover_agent
from shared.agent_registry import get_agent_url
from shared.config import REQUEST_TIMEOUT


async def call_agent(
    card_url: str,
    user_message: str,
    timeout: float = REQUEST_TIMEOUT
) -> str:

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

        result = response.json()

        if "error" in result:
            raise RuntimeError(str(result["error"]))

        return result["result"]["message"]["parts"][0]["text"]


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