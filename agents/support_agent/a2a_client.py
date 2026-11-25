from shared.a2a_client import call_agent_by_name


async def call_order_agent(user_message: str) -> str:
    return await call_agent_by_name("order", user_message)


async def call_refund_agent(user_message: str) -> str:
    return await call_agent_by_name("refund", user_message)


async def call_product_agent(user_message: str) -> str:
    return await call_agent_by_name("product", user_message)