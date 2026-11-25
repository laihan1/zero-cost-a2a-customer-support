import httpx
import uuid


def send_message(message):

    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "ROLE_USER",
                "parts": [{"text": message}]
            }
        }
    }

    response = httpx.post(
        "http://127.0.0.1:9999/",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "A2A-Version": "1.0"
        },
        timeout=30.0
    )

    assert response.status_code == 200

    result = response.json()

    assert "error" not in result

    return result["result"]["message"]["parts"][0]["text"]


def test_support_question():
    assert "Monday to Friday" in send_message(
        "What are your opening hours?"
    )


def test_order_shipped():
    assert "Status: Shipped" in send_message(
        "Where is my order ORD001?"
    )


def test_order_processing():
    assert "Status: Processing" in send_message(
        "Check order ORD002"
    )


def test_order_delivered():
    assert "Status: Delivered" in send_message(
        "Check order ORD003"
    )


def test_order_not_found():
    assert "was not found" in send_message(
        "Check order ORD999"
    )


def test_missing_order_id():
    assert "Please provide your order ID" in send_message(
        "Where is my order?"
    )

def test_refund_policy():
    assert "7 days" in send_message(
        "What is your refund policy?"
    )


def test_refund_shipped():
    assert "Please wait" in send_message(
        "Refund my order ORD001"
    )


def test_refund_processing():
    assert "cancellation" in send_message(
        "Can I cancel my order ORD002?"
    )


def test_refund_delivered():
    assert "may be eligible for a refund" in send_message(
        "Refund my order ORD003"
    )


def test_refund_not_found():
    assert "was not found" in send_message(
        "Refund my order ORD999"
    )

def test_product_price():
    assert "RM3500" in send_message(
        "How much is the laptop?"
    )


def test_product_in_stock():
    assert "Availability: In Stock" in send_message(
        "Is the keyboard available?"
    )


def test_product_out_of_stock():
    assert "Availability: Out of Stock" in send_message(
        "Do you have a mouse?"
    )


def test_product_details():
    assert "RTX 5050" in send_message(
        "Tell me about the laptop"
    )


def test_product_recommendation():
    assert "Mechanical Keyboard" in send_message(
        "Recommend a product"
    )


def test_product_list():
    assert "Laptop, Keyboard, Mouse" in send_message(
        "What products do you sell?"
    )