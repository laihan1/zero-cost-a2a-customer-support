import asyncio
from unittest.mock import patch

import httpx
import pytest

from shared.agent_discovery import discover_agent


def test_discover_agent():

    card = {
        "supportedInterfaces": [
            {
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
                "url": "http://127.0.0.1:9998/"
            }
        ]
    }

    with patch("httpx.AsyncClient.get") as mock_get:

        mock_get.return_value = httpx.Response(
            200,
            json=card,
            request=httpx.Request("GET", "http://localhost")
        )

        result = asyncio.run(
            discover_agent("http://localhost")
        )

        assert result == "http://127.0.0.1:9998/"


def test_no_compatible_interface():

    with patch("httpx.AsyncClient.get") as mock_get:

        mock_get.return_value = httpx.Response(
            200,
            json={"supportedInterfaces": []},
            request=httpx.Request("GET", "http://localhost")
        )

        with pytest.raises(RuntimeError):
            asyncio.run(
                discover_agent("http://localhost")
            )


def test_discovery_http_error():

    with patch("httpx.AsyncClient.get") as mock_get:

        mock_get.return_value = httpx.Response(
            404,
            request=httpx.Request("GET", "http://localhost")
        )

        with pytest.raises(httpx.HTTPStatusError):
            asyncio.run(
                discover_agent("http://localhost")
            )

from shared.exceptions import (
    AgentUnavailableError,
    AgentTimeoutError,
    AgentDiscoveryError,
)


def test_discovery_connection_error():

    with patch("httpx.AsyncClient.get") as mock_get:

        mock_get.side_effect = httpx.ConnectError(
            "Connection refused"
        )

        with pytest.raises(AgentUnavailableError):
            asyncio.run(
                discover_agent("http://localhost")
            )


def test_discovery_timeout():

    with patch("httpx.AsyncClient.get") as mock_get:

        mock_get.side_effect = httpx.ReadTimeout(
            "Request timed out"
        )

        with pytest.raises(AgentTimeoutError):
            asyncio.run(
                discover_agent("http://localhost")
            )


def test_discovery_invalid_json():

    with patch("httpx.AsyncClient.get") as mock_get:

        mock_get.return_value = httpx.Response(
            200,
            text="Invalid JSON",
            request=httpx.Request("GET", "http://localhost")
        )

        with pytest.raises(AgentDiscoveryError):
            asyncio.run(
                discover_agent("http://localhost")
            )


@pytest.mark.parametrize("card", [
    [],
    None,
    "invalid card",
    {"supportedInterfaces": None},
    {"supportedInterfaces": "invalid"},
    {"supportedInterfaces": [None]},
    {
        "supportedInterfaces": [
            {
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
                "url": 123
            }
        ]
    },
])
def test_discovery_invalid_card(card):

    with patch("httpx.AsyncClient.get") as mock_get:

        mock_get.return_value = httpx.Response(
            200,
            json=card,
            request=httpx.Request("GET", "http://localhost")
        )

        with pytest.raises(AgentDiscoveryError):
            asyncio.run(
                discover_agent("http://localhost")
            )


def test_discovery_error_logging(caplog):

    with patch("httpx.AsyncClient.get") as mock_get:

        mock_get.side_effect = httpx.ConnectError(
            "Connection refused"
        )

        with pytest.raises(AgentUnavailableError):
            asyncio.run(
                discover_agent("http://localhost")
            )

    assert "Agent discovery connection failed" in caplog.text