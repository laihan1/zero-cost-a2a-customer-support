from shared.config import (
    SUPPORT_URL,
    ORDER_URL,
    REFUND_URL,
    PRODUCT_URL,
)

AGENT_REGISTRY = {
    "support": SUPPORT_URL,
    "order": ORDER_URL,
    "refund": REFUND_URL,
    "product": PRODUCT_URL,
}


def get_agent_url(agent_name: str) -> str:
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {agent_name}")

    return AGENT_REGISTRY[agent_name]