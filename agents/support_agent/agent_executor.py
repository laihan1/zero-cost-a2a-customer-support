from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from agents.support_agent.support_logic import get_support_result
from shared.response_message import create_response_message


class SupportAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        user_message = context.get_user_input()
        response = get_support_result(user_message)

        await event_queue.enqueue_event(
            create_response_message(response)
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        return