import asyncio
from unittest.mock import patch

import pytest

from agents.supervisor_agent import supervisor_logic
from agents.supervisor_agent.supervisor_logic import detect_intent
from shared.exceptions import LLMTimeoutError


def test_order_intent():
    assert detect_intent("Where is my order ORD001?") == "order"


def test_refund_intent():
    assert detect_intent("Can I refund my order ORD003?") == "refund"


def test_product_intent():
    assert detect_intent("How much is the laptop?") == "product"


def test_support_intent():
    assert detect_intent("What are your opening hours?") == "support"


def test_refund_priority():
    assert detect_intent("Cancel my order") == "refund"


def test_case_insensitive():
    assert detect_intent("WHERE IS MY ORDER?") == "order"


def test_unknown_intent():
    assert detect_intent("Hello") == "support"


def test_empty_message():
    assert detect_intent("") == "support"

def test_available_intent():
    assert detect_intent("What is available?") == "product"


def test_how_much_intent():
    assert detect_intent("How much is it?") == "product"


def test_track_intent():
    assert detect_intent("Can I track my parcel?") == "order"


@pytest.mark.parametrize("enabled", [None, "false"])
def test_resolve_intent_uses_keyword_by_default(monkeypatch, caplog, enabled):
    if enabled is None:
        monkeypatch.delenv("LLM_ENABLED", raising=False)
    else:
        monkeypatch.setenv("LLM_ENABLED", enabled)
    caplog.set_level("INFO")
    message = "  Track private order 😀  "

    with (
        patch.object(supervisor_logic, "detect_intent", wraps=detect_intent) as router,
        patch.object(supervisor_logic, "classify_intent") as classifier,
        patch.object(supervisor_logic.asyncio, "timeout") as deadline,
    ):
        assert asyncio.run(supervisor_logic.resolve_intent(message)) == "order"

    deadline.assert_not_called()

    router.assert_called_once_with(message)
    classifier.assert_not_called()
    assert "intent=order routing_source=keyword" in caplog.text
    assert message.strip() not in caplog.text


@pytest.mark.parametrize("intent", ["order", "refund", "product", "support"])
def test_resolve_intent_uses_enabled_classifier(monkeypatch, caplog, intent):
    monkeypatch.setenv("LLM_ENABLED", "true")
    caplog.set_level("INFO")
    message = "  Track private order 😀  "

    with (
        patch.object(supervisor_logic, "detect_intent", wraps=detect_intent) as router,
        patch.object(supervisor_logic, "classify_intent", return_value=intent) as classifier,
    ):
        assert asyncio.run(supervisor_logic.resolve_intent(message)) == intent

    router.assert_not_called()
    classifier.assert_called_once_with(message)
    classifier.assert_awaited_once_with(message)
    assert f"intent={intent} routing_source=llm" in caplog.text
    assert message.strip() not in caplog.text


def test_resolve_intent_reloads_config_between_requests(monkeypatch):
    message = "Track my order"
    with patch.object(supervisor_logic, "classify_intent", return_value="refund") as classifier:
        monkeypatch.setenv("LLM_ENABLED", "false")
        assert asyncio.run(supervisor_logic.resolve_intent(message)) == "order"
        classifier.assert_not_called()

        monkeypatch.setenv("LLM_ENABLED", "true")
        assert asyncio.run(supervisor_logic.resolve_intent(message)) == "refund"
        classifier.assert_awaited_once_with(message)


def test_disabled_mode_still_rejects_invalid_configuration(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "false")
    monkeypatch.setenv("LLM_TIMEOUT", "invalid")
    with (
        patch.object(supervisor_logic, "detect_intent") as router,
        patch.object(supervisor_logic, "classify_intent") as classifier,
        patch.object(supervisor_logic.asyncio, "timeout") as deadline,
    ):
        with pytest.raises(ValueError, match="LLM_TIMEOUT"):
            asyncio.run(supervisor_logic.resolve_intent("Track my order"))

    router.assert_not_called()
    classifier.assert_not_called()
    deadline.assert_not_called()


def test_classifier_completes_within_real_deadline(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_TIMEOUT", "1")

    async def classify(message):
        await asyncio.sleep(0)
        return "refund"

    with (
        patch.object(supervisor_logic, "classify_intent", side_effect=classify) as classifier,
        patch.object(supervisor_logic, "detect_intent", wraps=detect_intent) as router,
    ):
        assert asyncio.run(supervisor_logic.resolve_intent("Track my order")) == "refund"

    classifier.assert_awaited_once_with("Track my order")
    router.assert_not_called()


def test_real_deadline_cancels_classifier_before_keyword_fallback(monkeypatch, caplog):
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_TIMEOUT", "0.02")
    caplog.set_level("INFO")
    message = "  Track private order 😀  "
    events = []

    async def classify(text):
        assert text == message
        assert asyncio.current_task() is resolver_task
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            events.append("cancelled")
            await asyncio.sleep(0)
            events.append("cleaned")
            raise

    def keyword(text):
        events.append("routed")
        return detect_intent(text)

    async def run():
        nonlocal resolver_task
        resolver_task = asyncio.create_task(supervisor_logic.resolve_intent(message))
        assert await asyncio.wait_for(resolver_task, timeout=3) == "order"
        assert asyncio.all_tasks() == {asyncio.current_task()}

    resolver_task = None
    with (
        patch.object(supervisor_logic, "classify_intent", side_effect=classify) as classifier,
        patch.object(supervisor_logic, "detect_intent", side_effect=keyword) as router,
        patch.object(supervisor_logic.asyncio, "timeout", wraps=asyncio.timeout) as deadline,
    ):
        asyncio.run(run())

    deadline.assert_called_once_with(0.02)
    classifier.assert_awaited_once_with(message)
    router.assert_called_once_with(message)
    assert events == ["cancelled", "cleaned", "routed"]
    assert "fallback_reason=classification_deadline" in caplog.text
    assert "routing_source=keyword_fallback" in caplog.text
    assert "llm_timeout" not in caplog.text
    assert message.strip() not in caplog.text


def test_keyword_fallback_error_propagates_without_retry(monkeypatch):
    monkeypatch.setenv("LLM_ENABLED", "true")
    error = RuntimeError("Keyword failure")
    message = "Track my order"

    with (
        patch.object(supervisor_logic, "classify_intent", side_effect=LLMTimeoutError()) as classifier,
        patch.object(supervisor_logic, "detect_intent", side_effect=error) as router,
    ):
        with pytest.raises(RuntimeError) as exc:
            asyncio.run(supervisor_logic.resolve_intent(message))

    assert exc.value is error
    classifier.assert_awaited_once_with(message)
    router.assert_called_once_with(message)