import httpx
from shared.config import DISCOVERY_TIMEOUT

async def discover_agent(card_url: str) -> str:

    async with httpx.AsyncClient(timeout=DISCOVERY_TIMEOUT) as client:
        response = await client.get(card_url)

        response.raise_for_status()

        agent_card = response.json()

        for interface in agent_card.get("supportedInterfaces", []):

            if (
                interface.get("protocolBinding") == "JSONRPC"
                and interface.get("protocolVersion") == "1.0"
                and interface.get("url")
            ):
                return interface["url"]

        raise RuntimeError("No compatible JSON-RPC interface found.")