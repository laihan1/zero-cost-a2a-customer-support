import httpx
import uuid

from agent_discovery import discover_agent


async def call_agent(card_url: str, user_message: str) -> str:

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

    async with httpx.AsyncClient(timeout=30.0) as client:

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


async def call_order_agent(user_message: str) -> str:

    return await call_agent(
        "http://127.0.0.1:9998/.well-known/agent-card.json",
        user_message
    )


async def call_refund_agent(user_message: str) -> str:

    return await call_agent(
        "http://127.0.0.1:9997/.well-known/agent-card.json",
        user_message
    )

async def call_product_agent(user_message: str) -> str:

    return await call_agent(
        "http://127.0.0.1:9996/.well-known/agent-card.json",
        user_message
    )