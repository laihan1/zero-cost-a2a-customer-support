import httpx
import uuid

from agent_discovery import discover_agent


async def call_order_agent(user_message: str) -> str:

    card_url = (
        "http://127.0.0.1:9998/.well-known/agent-card.json"
    )

    url = await discover_agent(card_url)

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "ROLE_USER",
                "parts": [
                    {
                        "text": user_message
                    }
                ]
            }
        }
    }

    async with httpx.AsyncClient(timeout=10.0) as client:

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