import asyncio
import httpx


async def main():

    url = "http://127.0.0.1:9998/"

    payload = {
        "jsonrpc": "2.0",
        "id": "test-order-001",
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": "order-message-001",
                "role": "ROLE_USER",
                "parts": [
                    {
                        "text": "Where is my order ORD001?"
                    }
                ]
            }
        }
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "A2A-Version": "1.0"
            }
        )

        print("HTTP Status:", response.status_code)
        print("A2A Response:")
        print(response.json())


if __name__ == "__main__":
    asyncio.run(main())