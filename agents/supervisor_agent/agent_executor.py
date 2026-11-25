import httpx

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.helpers import new_text_message

from agents.supervisor_agent.supervisor_logic import detect_intent
from shared.a2a_client import call_agent_by_name


class SupervisorAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        user_message = context.get_user_input()
        agent_name = detect_intent(user_message)

        try:
            response = await call_agent_by_name(
                agent_name,
                user_message,
            )

        except (httpx.HTTPError, RuntimeError):
            response = (
                f"The {agent_name} agent is currently unavailable. "
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
        raise NotImplementedError("Cancellation is not supported.")