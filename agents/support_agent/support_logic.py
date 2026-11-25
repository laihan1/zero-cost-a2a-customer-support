from shared.response_schema import AgentResponse


def get_support_result(user_message: str) -> AgentResponse:

    message = user_message.lower()

    if "hello" in message:
        response = "Hello! Welcome to our customer support."
        topic = "greeting"

    elif "opening hours" in message:
        response = (
            "Our business hours are Monday to Friday, "
            "9 AM to 6 PM."
        )
        topic = "business_hours"

    elif "refund" in message:
        response = (
            "Our refund policy allows eligible customers "
            "to request a refund within 7 days."
        )
        topic = "refund_policy"

    else:
        response = (
            "Thank you for contacting customer support. "
            "Could you provide more details so I can assist you?"
        )
        topic = "clarification"

    return AgentResponse(
        agent="support",
        success=True,
        message=response,
        data={"topic": topic}
    )


def get_support_response(user_message: str) -> str:
    return get_support_result(user_message).message