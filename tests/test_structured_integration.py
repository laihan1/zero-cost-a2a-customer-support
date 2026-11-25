import asyncio

from shared.a2a_client import call_agent_data_by_name


def ask_supervisor(message):
    return asyncio.run(
        call_agent_data_by_name("supervisor", message)
    )


def test_structured_order():
    response = ask_supervisor("Check order ORD001")

    assert response["agent"] == "order"
    assert response["success"] is True
    assert response["data"]["status"] == "Shipped"


def test_structured_refund():
    response = ask_supervisor("Refund ORD003")

    assert response["agent"] == "refund"
    assert response["success"] is True
    assert response["data"]["order_status"] == "Delivered"


def test_structured_product():
    response = ask_supervisor("Laptop price")

    assert response["agent"] == "product"
    assert response["success"] is True
    assert response["data"]["price"] == 3500


def test_structured_support():
    response = ask_supervisor("Opening hours")

    assert response["agent"] == "support"
    assert response["success"] is True
    assert response["data"]["topic"] == "business_hours"


def test_structured_order_not_found():
    response = ask_supervisor("Check order ORD999")

    assert response["agent"] == "order"
    assert response["success"] is False
    assert response["error_code"] == "ORDER_NOT_FOUND"


def test_structured_refund_order_not_found():
    response = ask_supervisor("Refund ORD999")

    assert response["agent"] == "refund"
    assert response["success"] is False
    assert response["error_code"] == "ORDER_NOT_FOUND"