import httpx

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from agents.refund_agent.refund_logic import (
    extract_order_id,
    get_refund_policy,
    check_refund_eligibility,
)
from agents.refund_agent.a2a_client import get_order_status
from shared.response_schema import AgentResponse
from shared.response_message import create_response_message


class RefundAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        user_message = context.get_user_input()
        order_id = extract_order_id(user_message)

        if not order_id:
            response = AgentResponse(
                agent="refund",
                success=True,
                message=get_refund_policy(),
                data={"refund_period_days": 7}
            )

        else:
            try:
                status = await get_order_status(order_id)

                if status == "Not Found":
                    response = AgentResponse(
                        agent="refund",
                        success=False,
                        message=f"Order {order_id} was not found.",
                        data={"order_id": order_id},
                        error_code="ORDER_NOT_FOUND"
                    )

                else:
                    eligibility = check_refund_eligibility(status)

                    response = AgentResponse(
                        agent="refund",
                        success=status in [
                            "Delivered", "Processing", "Shipped"
                        ],
                        message=(
                            f"Order ID: {order_id}\n"
                            f"Order Status: {status}\n"
                            f"{eligibility}"
                        ),
                        data={
                            "order_id": order_id,
                            "order_status": status,
                            "eligibility": eligibility
                        },
                        error_code=(
                            None if status in [
                                "Delivered", "Processing", "Shipped"
                            ] else "UNKNOWN_ORDER_STATUS"
                        )
                    )

            except (httpx.HTTPError, RuntimeError):
                response = AgentResponse(
                    agent="refund",
                    success=False,
                    message=(
                        "Unable to verify your order at the moment. "
                        "Please try again later."
                    ),
                    data={"order_id": order_id},
                    error_code="ORDER_AGENT_UNAVAILABLE"
                )

        await event_queue.enqueue_event(
            create_response_message(response)
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        return