import asyncio
from unittest.mock import patch

import pytest

from agents.supervisor_agent import supervisor_logic
from agents.supervisor_agent.supervisor_logic import detect_intent


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
    ):
        assert asyncio.run(supervisor_logic.resolve_intent(message)) == "order"

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
    ):
        with pytest.raises(ValueError, match="LLM_TIMEOUT"):
            asyncio.run(supervisor_logic.resolve_intent("Track my order"))

    router.assert_not_called()
    classifier.assert_not_called()