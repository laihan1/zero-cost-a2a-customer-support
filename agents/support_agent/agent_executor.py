import httpx

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.helpers import new_text_message

from support_logic import get_support_response
from a2a_client import call_order_agent


class SupportAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        user_message = context.get_user_input()
        message = user_message.lower()

        if "order" in message or "tracking" in message:

            try:
                response = await call_order_agent(user_message)

            except (httpx.HTTPError, RuntimeError):
                response = (
                    "The order service is currently unavailable. "
                    "Please try again later."
                )

        else:
            response = get_support_response(user_message)

        await event_queue.enqueue_event(
            new_text_message(response)
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        return