import pytest

from shared.agent_registry import get_agent_url


def test_support_agent_url():
    assert get_agent_url("support") == "http://127.0.0.1:9999"


def test_order_agent_url():
    assert get_agent_url("order") == "http://127.0.0.1:9998"


def test_refund_agent_url():
    assert get_agent_url("refund") == "http://127.0.0.1:9997"


def test_product_agent_url():
    assert get_agent_url("product") == "http://127.0.0.1:9996"


def test_unknown_agent():
    with pytest.raises(ValueError, match="Unknown agent"):
        get_agent_url("payment")