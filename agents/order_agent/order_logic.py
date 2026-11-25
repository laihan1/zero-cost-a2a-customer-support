import re
from shared.response_schema import AgentResponse

ORDERS = {
    "ORD001": {
        "product": "Laptop",
        "status": "Shipped",
        "tracking_number": "TRK123456"
    },
    "ORD002": {
        "product": "Keyboard",
        "status": "Processing",
        "tracking_number": "Not available"
    },
    "ORD003": {
        "product": "Mouse",
        "status": "Delivered",
        "tracking_number": "TRK789012"
    }
}


def get_order_result(user_message: str) -> AgentResponse:

    match = re.search(r"ORD\d+", user_message.upper())

    if not match:
        return AgentResponse(
            agent="order",
            success=False,
            message="Please provide your order ID.",
            error_code="MISSING_ORDER_ID"
        )

    order_id = match.group()
    order = ORDERS.get(order_id)

    if not order:
        return AgentResponse(
            agent="order",
            success=False,
            message=f"Order {order_id} was not found.",
            data={"order_id": order_id},
            error_code="ORDER_NOT_FOUND"
        )

    return AgentResponse(
        agent="order",
        success=True,
        message=(
            f"Order ID: {order_id}\n"
            f"Product: {order['product']}\n"
            f"Status: {order['status']}\n"
            f"Tracking Number: {order['tracking_number']}"
        ),
        data={
            "order_id": order_id,
            **order
        }
    )


def get_order_response(user_message: str) -> str:
    return get_order_result(user_message).message