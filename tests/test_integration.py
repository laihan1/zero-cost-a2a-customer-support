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