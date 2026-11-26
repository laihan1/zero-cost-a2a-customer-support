import asyncio
import json
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from google.protobuf.json_format import MessageToDict

from agents.supervisor_agent import agent_executor, supervisor_logic
from shared import llm_client
from shared.exceptions import AgentUnavailableError


CUSTOMER = "  Track my private order 訂單 😀  "
PRIVATE = "sensitive fixture payload"
ENDPOINT = "http://localhost:11434/api/chat"


def reply(intent="refund", *, generated=None, done=True, reason="stop"):
    if generated is None:
        generated = json.dumps({"intent": intent})
    return httpx.Response(200, json={
        "message": {"role": "assistant", "content": generated},
        "done": done,
        "done_reason": reason,
    })


def specialist_data(agent, message):
    return {
        "agent": agent,
        "success": True,
        "message": f"{agent} reply",
        "data": {"input_length": len(message)},
        "error_code": None,
    }


def request_context(message):
    return Mock(get_user_input=Mock(return_value=message)), Mock(enqueue_event=AsyncMock())


def assert_response(queue, data):
    queue.enqueue_event.assert_awaited_once()
    assert MessageToDict(queue.enqueue_event.await_args.args[0])["parts"] == [
        {"text": data["message"]},
        {"data": data},
    ]


def user_text(request):
    return json.loads(request.content)["messages"][1]["content"]


@pytest.fixture
def pipeline(monkeypatch, caplog):
    settings = {
        "LLM_ENABLED": "true",
        "LLM_BASE_URL": "http://localhost:11434",
        "LLM_MODEL": "qwen3:4b",
        "LLM_TIMEOUT": "2",
        "LLM_TEMPERATURE": "0",
        "LLM_NUM_CTX": "2048",
        "LLM_NUM_PREDICT": "64",
        "LLM_THINK": "false",
        "LLM_KEEP_ALIVE": "10m",
    }
    for name, value in settings.items():
        monkeypatch.setenv(name, value)

    caplog.set_level("DEBUG", logger=llm_client.__name__)
    caplog.set_level("INFO", logger=supervisor_logic.__name__)
    transport_handler = AsyncMock()
    clients = []
    async_client = httpx.AsyncClient

    def make_client(**kwargs):
        assert kwargs == {
            "timeout": float(os.environ["LLM_TIMEOUT"]),
            "trust_env": False,
            "follow_redirects": False,
        }
        client = async_client(transport=httpx.MockTransport(transport_handler), **kwargs)
        clients.append(client)
        return client

    # Replace only the LLM module's HTTPX lookup. A2A's HTTPX import is untouched.
    monkeypatch.setattr(llm_client, "httpx", SimpleNamespace(
        AsyncClient=make_client,
        TimeoutException=httpx.TimeoutException,
        RequestError=httpx.RequestError,
        HTTPStatusError=httpx.HTTPStatusError,
    ))
    specialist = AsyncMock(side_effect=specialist_data)
    router = Mock(wraps=supervisor_logic.detect_intent)
    monkeypatch.setattr(agent_executor, "call_agent_data_by_name", specialist)
    monkeypatch.setattr(supervisor_logic, "detect_intent", router)
    yield SimpleNamespace(
        executor=agent_executor.SupervisorAgentExecutor(),
        transport=transport_handler,
        clients=clients,
        specialist=specialist,
        router=router,
    )
    assert all(client.is_closed for client in clients)


async def execute_with_safety_limit(executor, context, queue):
    task = asyncio.create_task(executor.execute(context, queue))
    try:
        done, _ = await asyncio.wait({task}, timeout=3)
        assert task in done, "Executor exceeded the test safety limit"
        await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


def execute(pipeline, message=CUSTOMER):
    context, queue = request_context(message)
    asyncio.run(execute_with_safety_limit(pipeline.executor, context, queue))
    return queue


def assert_private_logs(caplog, *private_strings):
    assert all(value not in caplog.text for value in private_strings)
    assert "Classify the customer message" not in caplog.text


@pytest.mark.parametrize("intent", ["order", "refund", "product", "support"])
def test_real_llm_pipeline_routes_all_supported_intents(pipeline, caplog, intent):
    generated = json.dumps({"intent": intent})
    pipeline.transport.return_value = reply(generated=generated)

    queue = execute(pipeline)

    pipeline.transport.assert_awaited_once()
    request = pipeline.transport.await_args.args[0]
    assert (request.method, str(request.url)) == ("POST", ENDPOINT)
    payload = json.loads(request.content)
    system, user = payload["messages"]
    assert system["role"] == "system"
    assert CUSTOMER not in system["content"]
    assert user == {"role": "user", "content": CUSTOMER}
    assert payload["format"]["additionalProperties"] is False
    assert payload["format"]["properties"]["intent"]["enum"] == [
        "order", "refund", "product", "support",
    ]
    pipeline.router.assert_not_called()
    pipeline.specialist.assert_awaited_once_with(intent, CUSTOMER)
    assert_response(queue, specialist_data(intent, CUSTOMER))
    assert f"intent={intent} routing_source=llm" in caplog.text
    assert_private_logs(caplog, CUSTOMER.strip(), generated)


def test_disabled_pipeline_uses_keyword_without_ollama(pipeline, monkeypatch, caplog):
    monkeypatch.setenv("LLM_ENABLED", "false")

    queue = execute(pipeline)

    pipeline.transport.assert_not_called()
    assert not pipeline.clients
    pipeline.router.assert_called_once_with(CUSTOMER)
    pipeline.specialist.assert_awaited_once_with("order", CUSTOMER)
    assert_response(queue, specialist_data("order", CUSTOMER))
    assert "intent=order routing_source=keyword" in caplog.text
    assert "fallback_reason=" not in caplog.text


def test_invalid_input_pipeline_returns_native_error_without_ollama(pipeline, caplog):
    queue = execute(pipeline, PRIVATE + "\ud800")

    pipeline.transport.assert_not_called()
    assert not pipeline.clients
    pipeline.router.assert_not_called()
    pipeline.specialist.assert_not_called()
    assert_response(queue, {
        "agent": "supervisor",
        "success": False,
        "message": "Please provide a valid customer message of up to 400 characters.",
        "data": {},
        "error_code": "INVALID_INPUT",
    })
    assert_private_logs(caplog, PRIVATE)


@pytest.mark.parametrize(("outcome", "reason"), [
    pytest.param(httpx.ConnectError(PRIVATE), "llm_unavailable", id="connect"),
    pytest.param(httpx.ReadTimeout(PRIVATE), "llm_timeout", id="read-timeout-mapping"),
    pytest.param(httpx.Response(404, text=PRIVATE), "llm_http_error", id="http-404"),
    pytest.param(httpx.Response(503, text=PRIVATE), "llm_http_error", id="http-503"),
    pytest.param(httpx.Response(200, text=PRIVATE), "llm_response_error", id="malformed-envelope"),
    pytest.param(httpx.Response(200, json={"error": PRIVATE}), "llm_response_error", id="api-error"),
    pytest.param(httpx.Response(200, json={
        "done": True, "done_reason": "stop", "message": {"thinking": PRIVATE},
    }), "llm_response_error", id="missing-content"),
    pytest.param(reply(generated='{"intent": ' + PRIVATE), "llm_response_error", id="malformed-intent"),
    pytest.param(reply(generated=json.dumps({"intent": PRIVATE})), "llm_response_error", id="unknown-intent"),
    pytest.param(reply(generated='{"intent":"refund","intent":"support"}'),
                 "llm_response_error", id="duplicate-key"),
    pytest.param(reply(generated=json.dumps({"intent": "refund", "extra": PRIVATE})),
                 "llm_response_error", id="extra-field"),
    pytest.param(reply(done=False), "llm_response_error", id="incomplete"),
    pytest.param(reply(reason="length"), "llm_response_error", id="token-limit"),
])
def test_real_pipeline_falls_back_once_for_recoverable_http_outcome(pipeline, caplog, outcome, reason):
    if isinstance(outcome, httpx.RequestError):
        pipeline.transport.side_effect = outcome
    else:
        pipeline.transport.return_value = outcome

    queue = execute(pipeline)

    pipeline.transport.assert_awaited_once()
    assert user_text(pipeline.transport.await_args.args[0]) == CUSTOMER
    pipeline.router.assert_called_once_with(CUSTOMER)
    pipeline.specialist.assert_awaited_once_with("order", CUSTOMER)
    assert_response(queue, specialist_data("order", CUSTOMER))
    assert f"fallback_reason={reason}" in caplog.text
    assert "intent=order routing_source=keyword_fallback" in caplog.text
    assert_private_logs(caplog, CUSTOMER.strip(), PRIVATE)


def test_specialist_failure_after_http_fallback_keeps_unavailable_contract(pipeline):
    pipeline.transport.return_value = httpx.Response(503)
    pipeline.specialist.side_effect = AgentUnavailableError(PRIVATE)

    queue = execute(pipeline)

    pipeline.transport.assert_awaited_once()
    pipeline.router.assert_called_once_with(CUSTOMER)
    pipeline.specialist.assert_awaited_once_with("order", CUSTOMER)
    assert_response(queue, {
        "agent": "supervisor",
        "success": False,
        "message": "The order agent is currently unavailable. Please try again later.",
        "data": {"target_agent": "order"},
        "error_code": "AGENT_UNAVAILABLE",
    })


def test_deadline_discards_late_valid_result_from_transport(pipeline, monkeypatch, caplog):
    monkeypatch.setenv("LLM_TIMEOUT", "0.05")
    cancelled = Mock()

    async def respond(request):
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            cancelled()
            return reply("refund")

    pipeline.transport.side_effect = respond
    queue = execute(pipeline)

    cancelled.assert_called_once()
    pipeline.transport.assert_awaited_once()
    pipeline.router.assert_called_once_with(CUSTOMER)
    pipeline.specialist.assert_awaited_once_with("order", CUSTOMER)
    assert_response(queue, specialist_data("order", CUSTOMER))
    assert "fallback_reason=classification_deadline" in caplog.text
    assert "intent=order routing_source=keyword_fallback" in caplog.text


@pytest.mark.parametrize("expires", [False, True], ids=["success", "deadline-fallback"])
def test_classification_deadline_does_not_cover_specialist(pipeline, monkeypatch, caplog, expires):
    monkeypatch.setenv("LLM_TIMEOUT", "0.08")
    deadlines = []
    cleaned = Mock()

    def capture_deadline(delay):
        deadline = asyncio.timeout(delay)
        deadlines.append(deadline)
        return deadline

    monkeypatch.setattr(supervisor_logic, "asyncio", SimpleNamespace(
        timeout=capture_deadline,
        CancelledError=asyncio.CancelledError,
    ))

    async def respond(request):
        if not expires:
            return reply("refund")
        assert asyncio.current_task() is executor_task
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            await asyncio.sleep(0)
            cleaned()
            raise

    async def specialist(agent, message):
        assert len(deadlines) == 1
        assert deadlines[0].expired() is expires
        if expires:
            cleaned.assert_called_once()
        # Hold the specialist until after the actual classification deadline.
        release = asyncio.Event()
        loop = asyncio.get_running_loop()
        timer = loop.call_at(max(loop.time(), deadlines[0].when()) + 0.01, release.set)
        try:
            await release.wait()
        finally:
            timer.cancel()
        assert loop.time() >= deadlines[0].when()
        return specialist_data(agent, message)

    pipeline.transport.side_effect = respond
    pipeline.specialist.side_effect = specialist
    context, queue = request_context(CUSTOMER)
    executor_task = None

    async def run():
        nonlocal executor_task
        baseline = asyncio.all_tasks()
        executor_task = asyncio.create_task(pipeline.executor.execute(context, queue))
        await asyncio.wait_for(executor_task, timeout=3)
        assert asyncio.all_tasks() == baseline

    asyncio.run(run())

    expected = "order" if expires else "refund"
    pipeline.transport.assert_awaited_once()
    pipeline.specialist.assert_awaited_once_with(expected, CUSTOMER)
    assert_response(queue, specialist_data(expected, CUSTOMER))
    if expires:
        pipeline.router.assert_called_once_with(CUSTOMER)
        assert "fallback_reason=classification_deadline" in caplog.text
        assert "routing_source=keyword_fallback" in caplog.text
    else:
        cleaned.assert_not_called()
        pipeline.router.assert_not_called()
        assert "routing_source=llm" in caplog.text
        assert "fallback_reason=" not in caplog.text


@pytest.mark.parametrize("failure", [RuntimeError, TimeoutError])
def test_unexpected_error_during_deadline_cleanup_propagates(pipeline, monkeypatch, caplog, failure):
    monkeypatch.setenv("LLM_TIMEOUT", "0.05")
    original = failure(PRIVATE)
    cleaned = Mock()

    async def respond(request):
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            cleaned()
            raise original from None

    pipeline.transport.side_effect = respond
    context, queue = request_context(CUSTOMER)

    with pytest.raises(failure) as exc:
        asyncio.run(execute_with_safety_limit(pipeline.executor, context, queue))

    assert exc.value is original
    assert not isinstance(original.__cause__, asyncio.CancelledError)
    cleaned.assert_called_once()
    pipeline.transport.assert_awaited_once()
    pipeline.router.assert_not_called()
    pipeline.specialist.assert_not_called()
    queue.enqueue_event.assert_not_called()
    assert "fallback_reason=" not in caplog.text
    assert_private_logs(caplog, PRIVATE)


def test_external_cancellation_reaches_inflight_http_transport(pipeline, monkeypatch, caplog):
    monkeypatch.setenv("LLM_TIMEOUT", "10")
    context, queue = request_context(CUSTOMER)

    async def run():
        baseline = asyncio.all_tasks()
        entered = asyncio.Event()
        cleaned = asyncio.Event()

        async def respond(request):
            entered.set()
            try:
                await asyncio.Future()
            except asyncio.CancelledError:
                await asyncio.sleep(0)
                cleaned.set()
                raise

        pipeline.transport.side_effect = respond
        task = asyncio.create_task(pipeline.executor.execute(context, queue))
        try:
            await asyncio.wait_for(entered.wait(), timeout=3)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await asyncio.wait_for(task, timeout=3)
            assert cleaned.is_set()
            assert task.cancelled()
            assert asyncio.all_tasks() == baseline
        finally:
            if not task.done():
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)

    asyncio.run(run())

    pipeline.transport.assert_awaited_once()
    pipeline.router.assert_not_called()
    pipeline.specialist.assert_not_called()
    queue.enqueue_event.assert_not_called()
    assert "fallback_reason=" not in caplog.text


def test_concurrent_pipeline_requests_isolate_mixed_outcomes(pipeline, monkeypatch, caplog):
    monkeypatch.setenv("LLM_TIMEOUT", "10")
    messages = {
        "success": "Where is my private order?",
        "fallback": "Please refund my private order.",
        "cancel": "Which laptop do you recommend for my private use?",
        "unexpected": "What are your private opening hours?",
    }
    by_message = {message: key for key, message in messages.items()}
    calls = {key: request_context(message) for key, message in messages.items()}
    unexpected = RuntimeError(PRIVATE)

    async def run():
        baseline = asyncio.all_tasks()
        entered = {key: asyncio.Event() for key in messages}
        release = asyncio.Event()
        blocked = asyncio.Event()
        cancelled = asyncio.Event()

        async def respond(request):
            key = by_message[user_text(request)]
            entered[key].set()
            if key == "cancel":
                try:
                    await blocked.wait()
                except asyncio.CancelledError:
                    cancelled.set()
                    raise
            await release.wait()
            if key == "success":
                return reply("product")
            if key == "fallback":
                return httpx.Response(503, text=PRIVATE)
            raise unexpected

        pipeline.transport.side_effect = respond
        tasks = {
            key: asyncio.create_task(pipeline.executor.execute(*call))
            for key, call in calls.items()
        }
        try:
            await asyncio.wait_for(
                asyncio.gather(*(event.wait() for event in entered.values())), timeout=3
            )
            release.set()
            tasks["cancel"].cancel()
            results = await asyncio.wait_for(
                asyncio.gather(*tasks.values(), return_exceptions=True), timeout=3
            )
            assert results[0:2] == [None, None]
            assert isinstance(results[2], asyncio.CancelledError)
            assert results[3] is unexpected
            assert cancelled.is_set()
            assert asyncio.all_tasks() == baseline
        finally:
            for task in tasks.values():
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks.values(), return_exceptions=True)

    asyncio.run(run())

    assert sorted(user_text(call.args[0]) for call in pipeline.transport.await_args_list) == sorted(
        messages.values()
    )
    pipeline.router.assert_called_once_with(messages["fallback"])
    assert sorted(call.args for call in pipeline.specialist.await_args_list) == [
        ("product", messages["success"]),
        ("refund", messages["fallback"]),
    ]
    for key, expected in (("success", "product"), ("fallback", "refund")):
        assert_response(calls[key][1], specialist_data(expected, messages[key]))
    calls["cancel"][1].enqueue_event.assert_not_called()
    calls["unexpected"][1].enqueue_event.assert_not_called()
    assert_private_logs(caplog, PRIVATE, *messages.values())
