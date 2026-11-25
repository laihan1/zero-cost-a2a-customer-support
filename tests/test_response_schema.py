from shared.response_schema import AgentResponse
from shared.response_message import create_response_message
from agents.order_agent.order_logic import get_order_result
from agents.product_agent.product_logic import get_product_result
from agents.support_agent.support_logic import get_support_result


def test_response_schema_success():
    response = AgentResponse(
        agent="order",
        success=True,
        message="Order found"
    ).to_dict()

    assert response["agent"] == "order"
    assert response["success"] is True
    assert response["data"] == {}
    assert response["error_code"] is None


def test_response_schema_error():
    response = AgentResponse(
        agent="order",
        success=False,
        message="Order not found",
        error_code="ORDER_NOT_FOUND"
    ).to_dict()

    assert response["success"] is False
    assert response["error_code"] == "ORDER_NOT_FOUND"


def test_response_message_parts():
    response = get_order_result("Check order ORD001")
    message = create_response_message(response)

    assert len(message.parts) == 2
    assert message.parts[0].text == response.message
    assert message.parts[1].HasField("data")


def test_order_structured_response():
    response = get_order_result("Check order ORD001")

    assert response.success is True
    assert response.data["order_id"] == "ORD001"
    assert response.data["status"] == "Shipped"


def test_order_not_found():
    response = get_order_result("Check order ORD999")

    assert response.success is False
    assert response.error_code == "ORDER_NOT_FOUND"


def test_order_missing_id():
    response = get_order_result("Check my order")

    assert response.success is False
    assert response.error_code == "MISSING_ORDER_ID"


def test_product_structured_response():
    response = get_product_result("Laptop price")

    assert response.success is True
    assert response.data["price"] == 3500
    assert response.data["currency"] == "MYR"


def test_product_out_of_stock():
    response = get_product_result("Mouse stock")

    assert response.success is True
    assert response.data["stock"] == 0
    assert response.data["availability"] == "Out of Stock"


def test_support_structured_response():
    response = get_support_result("Opening hours")

    assert response.success is True
    assert response.data["topic"] == "business_hours"