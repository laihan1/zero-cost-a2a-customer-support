from shared.a2a_client import call_agent_by_name
from shared.config import REFUND_REQUEST_TIMEOUT


async def get_order_status(order_id: str) -> str:

    text = await call_agent_by_name(
        "order",
        f"Check order {order_id}",
        timeout=REFUND_REQUEST_TIMEOUT
    )

    if "was not found" in text:
        return "Not Found"

    for line in text.splitlines():
        if line.startswith("Status:"):
            return line.split(":", 1)[1].strip()

    return "Unknown"