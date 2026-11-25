import httpx
import uuid


async def get_order_status(order_id: str) -> str:

    card_url = (
        "http://127.0.0.1:9998/.well-known/agent-card.json"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:

        card_response = await client.get(card_url)
        card_response.raise_for_status()

        agent_card = card_response.json()

        url = None

        for interface in agent_card.get("supportedInterfaces", []):

            if (
                interface.get("protocolBinding") == "JSONRPC"
                and interface.get("protocolVersion") == "1.0"
                and interface.get("url")
            ):
                url = interface["url"]
                break

        if not url:
            raise RuntimeError("No compatible interface found.")

        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "SendMessage",
            "params": {
                "message": {
                    "messageId": str(uuid.uuid4()),
                    "role": "ROLE_USER",
                    "parts": [
                        {"text": f"Check order {order_id}"}
                    ]
                }
            }
        }

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

        text = result["result"]["message"]["parts"][0]["text"]

        if "was not found" in text:
            return "Not Found"

        for line in text.splitlines():
            if line.startswith("Status:"):
                return line.split(":", 1)[1].strip()

        return "Unknown"