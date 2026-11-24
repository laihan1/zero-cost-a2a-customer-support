from agents.support_agent.support_logic import get_support_response


def test_hello():
    assert get_support_response("Hello") == (
        "Hello! Welcome to our customer support."
    )


def test_opening_hours():
    assert get_support_response("What are your opening hours?") == (
        "Our business hours are Monday to Friday, 9 AM to 6 PM."
    )


def test_refund():
    assert get_support_response("What is your refund policy?") == (
        "Our refund policy allows eligible customers "
        "to request a refund within 7 days."
    )


def test_unknown_question():
    assert get_support_response("ABC123") == (
        "Thank you for contacting customer support. "
        "Could you provide more details so I can assist you?"
    )