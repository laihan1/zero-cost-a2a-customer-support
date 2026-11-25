import asyncio

from shared.a2a_client import call_agent_by_name


def ask_supervisor(message):
    return asyncio.run(
        call_agent_by_name("supervisor", message)
    )


def test_supervisor_order():
    response = ask_supervisor("Where is my order ORD001?")
    assert "ORD001" in response
    assert "Shipped" in response


def test_supervisor_refund():
    response = ask_supervisor("Can I refund my order ORD003?")
    assert "Delivered" in response
    assert "eligible for a refund" in response


def test_supervisor_product():
    response = ask_supervisor("How much is the laptop?")
    assert "Gaming Laptop" in response
    assert "RM3500" in response


def test_supervisor_support():
    response = ask_supervisor("What are your opening hours?")
    assert "Monday to Friday" in response

def test_support_does_not_route():
    response = asyncio.run(
        call_agent_by_name(
            "support",
            "Where is my order ORD001?"
        )
    )

    assert "Could you provide more details" in response
    assert "Status: Shipped" not in response