def detect_intent(user_message: str) -> str:
    message = user_message.lower()

    if any(word in message for word in ["refund", "cancel"]):
        return "refund"

    if any(word in message for word in ["order", "tracking", "track"]):
        return "order"

    if any(word in message for word in [
        "product", "price", "stock", "recommend",
        "laptop", "keyboard", "mouse"
    ]):
        return "product"

    return "support"