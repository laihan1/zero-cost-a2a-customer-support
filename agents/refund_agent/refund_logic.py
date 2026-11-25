import re


REFUND_POLICY = (
    "Customers can request a refund within 7 days "
    "after receiving their order."
)


def extract_order_id(user_message: str):

    match = re.search(r"ORD\d+", user_message.upper())

    if match:
        return match.group()

    return None


def get_refund_policy() -> str:

    return REFUND_POLICY


def check_refund_eligibility(order_status: str) -> str:

    status = order_status.lower().strip()

    if status == "delivered":
        return (
            "Your order may be eligible for a refund, "
            "subject to the 7-day refund policy."
        )

    elif status == "processing":
        return "Your order may be eligible for cancellation."

    elif status == "shipped":
        return "Please wait until your order has been delivered."

    else:
        return "Unable to determine refund eligibility."