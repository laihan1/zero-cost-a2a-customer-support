def get_support_response(user_message: str) -> str:

    message = user_message.lower()

    if "hello" in message:
        return "Hello! Welcome to our customer support."

    elif "opening hours" in message:
        return "Our business hours are Monday to Friday, 9 AM to 6 PM."

    elif "refund" in message:
        return (
            "Our refund policy allows eligible customers "
            "to request a refund within 7 days."
        )

    else:
        return (
            "Thank you for contacting customer support. "
            "Could you provide more details so I can assist you?"
        )