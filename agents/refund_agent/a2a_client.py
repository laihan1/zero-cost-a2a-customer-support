from shared.a2a_client import call_agent_data_by_name
from shared.config import REFUND_REQUEST_TIMEOUT


async def get_order_status(order_id: str) -> str:

    result = await call_agent_data_by_name(
        "order",
        f"Check order {order_id}",
        timeout=REFUND_REQUEST_TIMEOUT
    )

    if result.get("error_code") == "ORDER_NOT_FOUND":
        return "Not Found"

    if not result.get("success"):
        return "Unknown"

    return result.get("data", {}).get("status", "Unknown")