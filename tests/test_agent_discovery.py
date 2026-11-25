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