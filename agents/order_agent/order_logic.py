import re


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


def get_order_response(user_message: str) -> str:

    match = re.search(r"ORD\d+", user_message.upper())

    if not match:
        return "Please provide your order ID."

    order_id = match.group()

    order = ORDERS.get(order_id)

    if not order:
        return f"Order {order_id} was not found."

    return (
        f"Order ID: {order_id}\n"
        f"Product: {order['product']}\n"
        f"Status: {order['status']}\n"
        f"Tracking Number: {order['tracking_number']}"
    )