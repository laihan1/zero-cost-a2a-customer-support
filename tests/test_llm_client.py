import asyncio
import json
import logging
from unittest.mock import patch

import httpx
import pytest

from shared.config import load_llm_config
from shared.exceptions import (
    LLMDisabledError,
    LLMResponseError,
    LLMTimeoutError,
    LLMUnavailableError,
)
from shared.llm_client import chat


MESSAGES = [{"role": "user", "content": "Private customer message"}]


@pytest.fixture(autouse=True)
def llm_config():
    with patch(
        "shared.llm_client.load_llm_config",
        return_value=load_llm_config({"LLM_ENABLED": "true"}),
    ) as loader:
        yield loader


@pytest.fixture(autouse=True)
def mock_client():
    with patch("shared.llm_client.httpx.AsyncClient") as client:
        post = client.return_value.__aenter__.return_value.post
        yield client, post


def response(status=200, **kwargs):
    request = httpx.Request("POST", "http://localhost:11434/api/chat")
    return httpx.Response(status, request=request, **kwargs)


def test_disabled_llm(llm_config, mock_client):
    llm_config.return_value = load_llm_config({})
    with pytest.raises(LLMDisabledError):
        asyncio.run(chat(MESSAGES))
    mock_client[0].assert_not_called()


def test_invalid_config_opens_no_client(llm_config, mock_client):
    llm_config.side_effect = ValueError("Invalid LLM_BASE_URL")
    with pytest.raises(ValueError, match="LLM_BASE_URL"):
        asyncio.run(chat(MESSAGES))
    mock_client[0].assert_not_called()


@pytest.mark.parametrize("schema", [None, {}, {"type": "object"}])
def test_chat_payload_and_content(mock_client, schema):
    client, post = mock_client
    post.return_value = response(json={"message": {"content": "  A reply  "}})
    assert asyncio.run(chat(MESSAGES, response_format=schema)) == "  A reply  "

    payload = {
        "model": "qwen3:4b",
        "messages": MESSAGES,
        "stream": False,
        "think": False,
        "keep_alive": "10m",
        "options": {"temperature": 0.0, "num_ctx": 2048, "num_predict": 64},
    }
    if schema is not None:
        payload["format"] = schema
    client.assert_called_once_with(timeout=15.0, trust_env=False, follow_redirects=False)
    post.assert_awaited_once_with("http://localhost:11434/api/chat", json=payload)


def test_custom_timeout(mock_client, llm_config):
    client, post = mock_client
    llm_config.return_value = load_llm_config({
        "LLM_ENABLED": "true",
        "LLM_TIMEOUT": "2.75",
        "LLM_BASE_URL": "http://127.0.0.1:8080/",
    })
    post.return_value = response(json={"message": {"content": "Reply"}})

    asyncio.run(chat(MESSAGES))

    client.assert_called_once_with(timeout=2.75, trust_env=False, follow_redirects=False)
    assert post.await_args.args[0] == "http://127.0.0.1:8080/api/chat"


@pytest.mark.parametrize(("error", "expected"), [
    (httpx.ConnectError("Connection refused"), LLMUnavailableError),
    (httpx.ReadTimeout("Read timed out"), LLMTimeoutError),
    (httpx.ConnectTimeout("Connection timed out"), LLMTimeoutError),
])
def test_transport_errors(mock_client, error, expected):
    post = mock_client[1]
    post.side_effect = error
    with pytest.raises(expected) as exc:
        asyncio.run(chat(MESSAGES))
    assert exc.value.__cause__ is error
    assert post.await_count == 1


@pytest.mark.parametrize("status", [302, 400, 404, 500, 503])
def test_preserve_http_status_error(mock_client, status):
    post = mock_client[1]
    post.return_value = response(status, headers={"Location": "http://example.com"})
    with pytest.raises(httpx.HTTPStatusError) as exc:
        asyncio.run(chat(MESSAGES))
    assert exc.value.response.status_code == status
    assert post.await_count == 1


def test_malformed_json(mock_client):
    mock_client[1].return_value = response(content=b"{broken")
    with pytest.raises(LLMResponseError, match="JSON"):
        asyncio.run(chat(MESSAGES))


@pytest.mark.parametrize("body", [
    None,
    [],
    "response",
    {},
    {"message": None},
    {"message": []},
    {"message": {}},
    {"message": {"content": ""}},
    {"message": {"content": " \n "}},
    {"message": {"content": 1}},
    {"message": {"content": False}},
    {"message": {"content": None}},
    {"error": "Model error", "message": {"content": "Unexpected reply"}},
])
def test_invalid_response(mock_client, body):
    mock_client[1].return_value = response(content=json.dumps(body).encode())
    with pytest.raises(LLMResponseError):
        asyncio.run(chat(MESSAGES))


def test_logs_exclude_sensitive_data(mock_client, caplog):
    caplog.set_level(logging.DEBUG, logger="shared.llm_client")
    mock_client[1].return_value = response(json={
        "message": {"content": "Private answer"},
        "error": "Private API detail with credential=sensitive",
    })
    with pytest.raises(LLMResponseError) as exc:
        asyncio.run(chat(MESSAGES))
    assert "Local LLM returned an API error" in caplog.text
    for secret in ("Private customer message", "Private answer", "credential=sensitive"):
        assert secret not in caplog.text
        assert secret not in str(exc.value)


def test_chat_accepts_normal_completion(mock_client):
    post = mock_client[1]
    content = '{"intent": "order"}'
    post.return_value = response(json={
        "message": {"content": content},
        "done": True,
        "done_reason": "stop",
    })

    assert asyncio.run(chat(MESSAGES, require_complete=True)) == content
    post.assert_awaited_once()


@pytest.mark.parametrize("metadata", [
    {"done_reason": "stop"},
    {"done": True},
    {"done": False, "done_reason": "stop"},
    {"done": 1, "done_reason": "stop"},
    {"done": "true", "done_reason": "stop"},
    {"done": None, "done_reason": "stop"},
    {"done": True, "done_reason": "length"},
    {"done": True, "done_reason": "unknown"},
    {"done": True, "done_reason": 1},
    {"done": True, "done_reason": None},
])
def test_chat_rejects_invalid_completion_metadata(mock_client, metadata):
    post = mock_client[1]
    post.return_value = response(json={
        "message": {"content": '{"intent": "order"}'},
        **metadata,
    })

    with pytest.raises(LLMResponseError, match="completion"):
        asyncio.run(chat(MESSAGES, require_complete=True))
    post.assert_awaited_once()


def test_default_chat_does_not_require_normal_completion(mock_client):
    mock_client[1].return_value = response(json={
        "message": {"content": "Reply"},
        "done": False,
        "done_reason": "length",
    })

    assert asyncio.run(chat(MESSAGES)) == "Reply"


def test_strict_chat_preserves_http_status_error(mock_client):
    mock_client[1].return_value = response(503, json={"error": "Unavailable"})
    with pytest.raises(httpx.HTTPStatusError) as exc:
        asyncio.run(chat(MESSAGES, require_complete=True))
    assert exc.value.response.status_code == 503
