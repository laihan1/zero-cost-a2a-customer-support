import httpx

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.helpers import new_text_message

from agents.refund_agent.refund_logic import (
    extract_order_id,
    get_refund_policy,
    check_refund_eligibility,
)

from agents.refund_agent.a2a_client import get_order_status


class RefundAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        user_message = context.get_user_input()

        order_id = extract_order_id(user_message)

        if not order_id:
            response = get_refund_policy()

        else:
            try:
                status = await get_order_status(order_id)

                if status == "Not Found":
                    response = f"Order {order_id} was not found."

                else:
                    eligibility = check_refund_eligibility(status)

                    response = (
                        f"Order ID: {order_id}\n"
                        f"Order Status: {status}\n"
                        f"{eligibility}"
                    )

            except (httpx.HTTPError, RuntimeError):
                response = (
                    "Unable to verify your order at the moment. "
                    "Please try again later."
                )

        await event_queue.enqueue_event(
            new_text_message(response)
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        return