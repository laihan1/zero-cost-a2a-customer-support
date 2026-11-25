import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from shared.a2a_client import call_agent_by_name, call_agent


def test_call_agent_by_name():

    with patch(
        "shared.a2a_client.call_agent",
        new_callable=AsyncMock
    ) as mock_call:

        mock_call.return_value = "Order shipped"

        result = asyncio.run(
            call_agent_by_name("order", "Check order")
        )

        assert result == "Order shipped"

        mock_call.assert_awaited_once_with(
            "http://127.0.0.1:9998/.well-known/agent-card.json",
            "Check order",
            30.0
        )


def test_unknown_agent():

    with pytest.raises(ValueError, match="Unknown agent"):

        asyncio.run(
            call_agent_by_name("payment", "Check payment")
        )


def test_custom_timeout():

    with patch(
        "shared.a2a_client.call_agent",
        new_callable=AsyncMock
    ) as mock_call:

        asyncio.run(
            call_agent_by_name("order", "Check order", timeout=10.0)
        )

        mock_call.assert_awaited_once_with(
            "http://127.0.0.1:9998/.well-known/agent-card.json",
            "Check order",
            10.0
        )


def test_http_error():

    with patch(
        "shared.a2a_client.discover_agent",
        new_callable=AsyncMock
    ) as mock_discover:

        mock_discover.return_value = "http://127.0.0.1:9998/"

        with patch("httpx.AsyncClient.post") as mock_post:

            mock_post.return_value = httpx.Response(
                500,
                request=httpx.Request(
                    "POST", "http://127.0.0.1:9998/"
                )
            )

            with pytest.raises(httpx.HTTPStatusError):
                asyncio.run(
                    call_agent("http://localhost", "Hello")
                )


def test_jsonrpc_error():

    with patch(
        "shared.a2a_client.discover_agent",
        new_callable=AsyncMock
    ) as mock_discover:

        mock_discover.return_value = "http://127.0.0.1:9998/"

        with patch("httpx.AsyncClient.post") as mock_post:

            mock_post.return_value = httpx.Response(
                200,
                json={"error": {"message": "Internal error"}},
                request=httpx.Request(
                    "POST", "http://127.0.0.1:9998/"
                )
            )

            with pytest.raises(RuntimeError):
                asyncio.run(
                    call_agent("http://localhost", "Hello")
                )