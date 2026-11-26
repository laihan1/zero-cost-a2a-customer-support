# A conservative code-point limit for support enquiries. It does not guarantee
# that the message fits any particular model's token budget.
MAX_MESSAGE_LENGTH = 400


def validate_customer_message(message: object) -> None:
    """Reject invalid customer input without changing the original message."""
    if not isinstance(message, str):
        raise TypeError("Customer message must be a string.")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Customer message exceeds {MAX_MESSAGE_LENGTH} characters.")
    if not message.strip():
        raise ValueError("Customer message must not be blank.")

    try:
        message.encode("utf-8")
    except UnicodeEncodeError:
        pass
    else:
        return

    # Raise outside the handler so the encoding exception and its input are
    # excluded from the validation exception's context.
    raise ValueError("Customer message must be valid Unicode.")
