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
        "http://127.0.0.1:9997/",
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


def test_refund_policy():
    assert "7 days" in send_message("What is your refund policy?")


def test_refund_shipped():
    assert "Please wait" in send_message("Refund ORD001")


def test_refund_processing():
    assert "cancellation" in send_message("Refund ORD002")


def test_refund_delivered():
    assert "may be eligible for a refund" in send_message("Refund ORD003")


def test_refund_not_found():
    assert "was not found" in send_message("Refund ORD999")