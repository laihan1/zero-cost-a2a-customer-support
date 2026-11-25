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

            with pytest.raises(AgentRPCError):
                asyncio.run(
                    call_agent("http://localhost", "Hello")
                )

from shared.a2a_client import call_agent_data_by_name
from shared.exceptions import (
    AgentUnavailableError,
    AgentTimeoutError,
    AgentResponseError,
    AgentRPCError,
)


@pytest.mark.parametrize("error, expected", [
    (
        httpx.ConnectError("Connection refused"),
        AgentUnavailableError
    ),
    (
        httpx.ReadTimeout("Request timed out"),
        AgentTimeoutError
    ),
])
def test_agent_request_failure(error, expected):

    with patch(
        "shared.a2a_client.discover_agent",
        new_callable=AsyncMock,
        return_value="http://localhost"
    ):
        with patch("httpx.AsyncClient.post") as mock_post:

            mock_post.side_effect = error

            with pytest.raises(expected):
                asyncio.run(
                    call_agent("http://localhost", "Hello")
                )


@pytest.mark.parametrize("payload", [
    [],
    {},
    {"result": None},
    {"result": {"message": {}}},
    {"result": {"message": {"parts": []}}},
    {"result": {"message": {"parts": "invalid"}}},
    {"result": {"message": {"parts": [None]}}},
])
def test_invalid_agent_response(payload):

    with patch(
        "shared.a2a_client.discover_agent",
        new_callable=AsyncMock,
        return_value="http://localhost"
    ):
        with patch("httpx.AsyncClient.post") as mock_post:

            mock_post.return_value = httpx.Response(
                200,
                json=payload,
                request=httpx.Request(
                    "POST", "http://localhost"
                )
            )

            with pytest.raises(AgentResponseError):
                asyncio.run(
                    call_agent("http://localhost", "Hello")
                )


def test_invalid_response_json():

    with patch(
        "shared.a2a_client.discover_agent",
        new_callable=AsyncMock,
        return_value="http://localhost"
    ):
        with patch("httpx.AsyncClient.post") as mock_post:

            mock_post.return_value = httpx.Response(
                200,
                text="Invalid JSON",
                request=httpx.Request(
                    "POST", "http://localhost"
                )
            )

            with pytest.raises(AgentResponseError):
                asyncio.run(
                    call_agent("http://localhost", "Hello")
                )


def test_text_part_not_first():

    with patch(
        "shared.a2a_client.call_agent_parts",
        new_callable=AsyncMock,
        return_value=[
            {"data": {}},
            {"text": "Order shipped"}
        ]
    ):
        result = asyncio.run(
            call_agent("http://localhost", "Hello")
        )

        assert result == "Order shipped"


def test_missing_text_part():

    with patch(
        "shared.a2a_client.call_agent_parts",
        new_callable=AsyncMock,
        return_value=[{"data": {}}]
    ):
        with pytest.raises(AgentResponseError):
            asyncio.run(
                call_agent("http://localhost", "Hello")
            )


def test_valid_structured_response():

    response = {
        "agent": "order",
        "success": True,
        "message": "Order shipped",
        "data": {"status": "Shipped"},
        "error_code": None
    }

    with patch(
        "shared.a2a_client.call_agent_parts",
        new_callable=AsyncMock,
        return_value=[
            {"text": "Order shipped"},
            {"data": response}
        ]
    ):
        result = asyncio.run(
            call_agent_data_by_name("order", "Hello")
        )

        assert result == response


@pytest.mark.parametrize("parts", [
    [{"text": "Hello"}],
    [{"data": None}],
    [{"data": []}],
    [{"data": {}}],
    [{"data": {
        "agent": "order",
        "success": "true",
        "message": "Hello",
        "data": {}
    }}],
    [{"data": {
        "agent": "order",
        "success": True,
        "message": "Hello",
        "data": []
    }}],
])
def test_invalid_structured_response(parts):

    with patch(
        "shared.a2a_client.call_agent_parts",
        new_callable=AsyncMock,
        return_value=parts
    ):
        with pytest.raises(AgentResponseError):
            asyncio.run(
                call_agent_data_by_name("order", "Hello")
            )


def test_agent_error_logging(caplog):

    with patch(
        "shared.a2a_client.discover_agent",
        new_callable=AsyncMock,
        return_value="http://localhost"
    ):
        with patch("httpx.AsyncClient.post") as mock_post:

            mock_post.side_effect = httpx.ConnectError(
                "Connection refused"
            )

            with pytest.raises(AgentUnavailableError):
                asyncio.run(
                    call_agent("http://localhost", "Hello")
                )

    assert "Agent connection failed" in caplog.text