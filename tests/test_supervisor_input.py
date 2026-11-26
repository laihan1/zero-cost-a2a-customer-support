import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from google.protobuf.json_format import MessageToDict

from agents.supervisor_agent import agent_executor


INVALID_MESSAGE = "Please provide a valid customer message of up to 400 characters."


@pytest.fixture
def boundary():
    context = Mock()
    queue = Mock(enqueue_event=AsyncMock())
    with (
        patch.object(agent_executor, "detect_intent", wraps=agent_executor.detect_intent) as router,
        patch.object(agent_executor, "call_agent_data_by_name") as specialist,
        patch("shared.intent_classifier.chat") as llm,
    ):
        yield context, queue, router, specialist, llm


@pytest.mark.parametrize("enabled", ["false", "true"])
@pytest.mark.parametrize("message", [None, False, "", "\u3000", "x" * 401, "private\ud800text"])
def test_invalid_input_returns_native_parts(boundary, monkeypatch, caplog, enabled, message):
    monkeypatch.setenv("LLM_ENABLED", enabled)
    context, queue, router, specialist, llm = boundary
    context.get_user_input.return_value = message

    asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    router.assert_not_called()
    specialist.assert_not_called()
    llm.assert_not_called()
    queue.enqueue_event.assert_awaited_once()
    response = MessageToDict(queue.enqueue_event.await_args.args[0])
    assert response["parts"] == [
        {"text": INVALID_MESSAGE},
        {"data": {
            "agent": "supervisor",
            "success": False,
            "message": INVALID_MESSAGE,
            "data": {},
            "error_code": "INVALID_INPUT",
        }},
    ]
    assert "private" not in caplog.text
    assert "Unicode" not in caplog.text


@pytest.mark.parametrize("enabled", ["false", "true"])
@pytest.mark.parametrize(("message", "agent"), [
    ("  Track 訂單 😀  ", "order"),
    ("Refund my order お願いします", "refund"),
    ("What is the price? Café", "product"),
    ("😀" * 400, "support"),
])
def test_valid_input_routes_unchanged(boundary, monkeypatch, enabled, message, agent):
    monkeypatch.setenv("LLM_ENABLED", enabled)
    context, queue, router, specialist, llm = boundary
    context.get_user_input.return_value = message
    specialist.return_value = {"agent": agent, "success": True, "message": "Reply"}

    asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    router.assert_called_once_with(message)
    specialist.assert_awaited_once_with(agent, message)
    llm.assert_not_called()
    queue.enqueue_event.assert_awaited_once()
    response = MessageToDict(queue.enqueue_event.await_args.args[0])
    assert response["parts"][1]["data"]["agent"] == agent


@pytest.mark.parametrize(("operation", "error"), [
    ("extraction", TypeError("SDK error")),
    ("routing", ValueError("Router error")),
    ("communication", TypeError("Client error")),
    ("communication", ValueError("Client error")),
])
def test_validation_handler_does_not_swallow_unexpected_errors(boundary, operation, error):
    context, queue, router, specialist, llm = boundary
    context.get_user_input.return_value = "Track my order"
    operations = {"extraction": context.get_user_input, "routing": router,
                  "communication": specialist}
    operations[operation].side_effect = error

    with pytest.raises(type(error)) as exc:
        asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    assert exc.value is error
    queue.enqueue_event.assert_not_called()
    llm.assert_not_called()
