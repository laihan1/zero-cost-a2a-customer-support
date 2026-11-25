
import asyncio
import httpx


async def main():

    url = "http://127.0.0.1:9999/"

    payload = {
        "jsonrpc": "2.0",
        "id": "test-request-001",
        "method": "SendMessage",
        "params": {
            "message": {
                "messageId": "test-message-001",
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

        result = response.json()

        print("\nA2A Response:")
        print(result)

        if "error" in result:
            print("\nRequest failed:", result["error"])
        else:
            print("\nA2A communication successful!")


if __name__ == "__main__":
    asyncio.run(main())
