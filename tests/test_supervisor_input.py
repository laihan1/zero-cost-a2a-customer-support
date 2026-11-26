import asyncio
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from google.protobuf.json_format import MessageToDict

from agents.supervisor_agent import agent_executor, supervisor_logic
from shared.exceptions import (
    AgentError,
    AgentUnavailableError,
    LLMDisabledError,
    LLMError,
    LLMResponseError,
    LLMTimeoutError,
    LLMUnavailableError,
)


INVALID_MESSAGE = "Please provide a valid customer message of up to 400 characters."


@pytest.fixture
def boundary():
    context = Mock()
    queue = Mock(enqueue_event=AsyncMock())
    with (
        patch.object(supervisor_logic, "detect_intent", wraps=supervisor_logic.detect_intent) as router,
        patch.object(agent_executor, "call_agent_data_by_name") as specialist,
        patch.object(supervisor_logic, "classify_intent") as llm,
    ):
        yield context, queue, router, specialist, llm


@pytest.mark.parametrize("enabled", ["false", "true"])
@pytest.mark.parametrize("message", [None, False, "", "\u3000", "x" * 401, "private\ud800text"])
def test_invalid_input_returns_native_parts(boundary, monkeypatch, caplog, enabled, message):
    monkeypatch.setenv("LLM_ENABLED", enabled)
    context, queue, router, specialist, llm = boundary
    context.get_user_input.return_value = message

    with (
        patch.object(agent_executor, "resolve_intent", wraps=agent_executor.resolve_intent) as resolve,
        patch.object(supervisor_logic, "load_llm_config", wraps=supervisor_logic.load_llm_config) as load,
    ):
        asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    resolve.assert_not_called()
    load.assert_not_called()
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
    # Enabled mode deliberately selects a different intent than the real router.
    llm_intent = {"order": "refund", "refund": "product", "product": "support", "support": "order"}
    selected = llm_intent[agent] if enabled == "true" else agent
    llm.return_value = llm_intent[agent]
    data = {"agent": selected, "success": True, "message": "Reply", "data": {}}
    specialist.return_value = data

    asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    if enabled == "true":
        router.assert_not_called()
        llm.assert_called_once_with(message)
        llm.assert_awaited_once_with(message)
    else:
        router.assert_called_once_with(message)
        llm.assert_not_called()
    specialist.assert_called_once_with(selected, message)
    specialist.assert_awaited_once_with(selected, message)
    queue.enqueue_event.assert_awaited_once()
    response = MessageToDict(queue.enqueue_event.await_args.args[0])
    assert response["parts"] == [
        {"text": "Reply"},
        {"data": {**data, "error_code": None}},
    ]


@pytest.mark.parametrize(("operation", "error"), [
    ("extraction", TypeError("SDK error")),
    ("routing", ValueError("Router error")),
    ("communication", TypeError("Client error")),
    ("communication", ValueError("Client error")),
])
def test_validation_handler_does_not_swallow_unexpected_errors(boundary, monkeypatch, operation, error):
    monkeypatch.setenv("LLM_ENABLED", "false")
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


@pytest.mark.parametrize("enabled", ["false", "true", "fallback"])
def test_specialist_failure_keeps_existing_contract(boundary, monkeypatch, enabled):
    monkeypatch.setenv("LLM_ENABLED", "false" if enabled == "false" else "true")
    context, queue, router, specialist, llm = boundary
    message = "Track my order"
    context.get_user_input.return_value = message
    llm.return_value = "order"
    if enabled == "fallback":
        llm.side_effect = LLMTimeoutError("Local inference timed out")
    specialist.side_effect = AgentUnavailableError("Specialist offline")

    asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    if enabled == "false":
        llm.assert_not_called()
    else:
        llm.assert_awaited_once_with(message)
    if enabled == "true":
        router.assert_not_called()
    else:
        router.assert_called_once_with(message)
    specialist.assert_awaited_once_with("order", message)
    queue.enqueue_event.assert_awaited_once()
    parts = MessageToDict(queue.enqueue_event.await_args.args[0])["parts"]
    reply = "The order agent is currently unavailable. Please try again later."
    assert parts == [
        {"text": reply},
        {"data": {
            "agent": "supervisor",
            "success": False,
            "message": reply,
            "data": {"target_agent": "order"},
            "error_code": "AGENT_UNAVAILABLE",
        }},
    ]


@pytest.mark.parametrize(("error", "reason"), [
    (LLMDisabledError("sensitive disabled detail"), "llm_disabled"),
    (LLMUnavailableError("sensitive connection detail"), "llm_unavailable"),
    (LLMTimeoutError("sensitive timeout detail"), "llm_timeout"),
    (LLMResponseError("sensitive model output"), "llm_response_error"),
    *[
        (httpx.HTTPStatusError(
            "sensitive HTTP detail",
            request=httpx.Request("POST", "http://localhost:11434/api/chat"),
            response=httpx.Response(status),
        ), "llm_http_error")
        for status in (404, 503)
    ],
])
def test_recoverable_classifier_failure_routes_once(boundary, monkeypatch, caplog, error, reason):
    monkeypatch.setenv("LLM_ENABLED", "true")
    caplog.set_level("INFO")
    context, queue, router, specialist, llm = boundary
    message = "  Cancel my private order 😀  "
    context.get_user_input.return_value = message
    llm.side_effect = error
    data = {"agent": "refund", "success": True, "message": "Reply", "data": {}}
    specialist.return_value = data

    asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    llm.assert_called_once_with(message)
    llm.assert_awaited_once_with(message)
    router.assert_called_once_with(message)
    specialist.assert_called_once_with("refund", message)
    specialist.assert_awaited_once_with("refund", message)
    queue.enqueue_event.assert_awaited_once()
    assert MessageToDict(queue.enqueue_event.await_args.args[0])["parts"] == [
        {"text": "Reply"},
        {"data": {**data, "error_code": None}},
    ]
    assert f"fallback_reason={reason}" in caplog.text
    assert "intent=refund routing_source=keyword_fallback" in caplog.text
    assert "classification_deadline" not in caplog.text
    assert message.strip() not in caplog.text
    assert str(error) not in caplog.text


@pytest.mark.parametrize("error", [
    ValueError("sensitive programming detail"),
    TypeError("sensitive type detail"),
    RuntimeError("sensitive runtime detail"),
    AttributeError("sensitive attribute detail"),
    KeyError("sensitive key detail"),
    LLMError("unrecognized LLM error"),
    AgentError("unexpected agent error"),
    TimeoutError("unrelated timeout"),
    asyncio.CancelledError("sensitive cancellation detail"),
])
def test_classifier_failure_propagates_without_fallback(boundary, monkeypatch, caplog, error):
    monkeypatch.setenv("LLM_ENABLED", "true")
    caplog.set_level("INFO")
    context, queue, router, specialist, llm = boundary
    message = "Track private order"
    context.get_user_input.return_value = message
    llm.side_effect = error

    with pytest.raises(type(error)) as exc:
        asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    assert exc.value is error
    llm.assert_awaited_once_with(message)
    router.assert_not_called()
    specialist.assert_not_called()
    queue.enqueue_event.assert_not_called()
    assert message not in caplog.text
    assert str(error) not in caplog.text
    assert "keyword_fallback" not in caplog.text
    assert "fallback_reason=" not in caplog.text


@pytest.mark.parametrize("during_deadline_cleanup", [False, True])
def test_external_executor_cancellation_propagates(boundary, monkeypatch, during_deadline_cleanup):
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_TIMEOUT", "0.02" if during_deadline_cleanup else "10")
    context, queue, router, specialist, llm = boundary
    message = "Track my order"
    context.get_user_input.return_value = message

    async def run():
        started = asyncio.Event()
        cancelling = asyncio.Event()

        async def classify(user_message):
            started.set()
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                cancelling.set()
                if during_deadline_cleanup:
                    await asyncio.Future()
                raise

        llm.side_effect = classify
        task = asyncio.create_task(agent_executor.SupervisorAgentExecutor().execute(context, queue))
        try:
            await asyncio.wait_for(started.wait(), timeout=3)
            if during_deadline_cleanup:
                await asyncio.wait_for(cancelling.wait(), timeout=3)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=3)
            assert cancelling.is_set()
            assert task.cancelled()
            assert asyncio.all_tasks() == {asyncio.current_task()}
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

    asyncio.run(run())

    llm.assert_awaited_once_with(message)
    router.assert_not_called()
    specialist.assert_not_called()
    queue.enqueue_event.assert_not_called()


def test_invalid_configuration_prevents_executor_routing(boundary, monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "invalid")
    context, queue, router, specialist, llm = boundary
    context.get_user_input.return_value = "Track my order"

    with pytest.raises(ValueError, match="LLM_ENABLED"):
        asyncio.run(agent_executor.SupervisorAgentExecutor().execute(context, queue))

    router.assert_not_called()
    llm.assert_not_called()
    specialist.assert_not_called()
    queue.enqueue_event.assert_not_called()
