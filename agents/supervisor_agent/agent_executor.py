import logging

import httpx

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue

from agents.supervisor_agent.supervisor_logic import resolve_intent
from shared.a2a_client import call_agent_data_by_name
from shared.customer_message import MAX_MESSAGE_LENGTH, validate_customer_message
from shared.response_schema import AgentResponse
from shared.response_message import create_response_message


logger = logging.getLogger(__name__)


class SupervisorAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:

        user_message = context.get_user_input()
        try:
            validate_customer_message(user_message)
        except (TypeError, ValueError):
            response = AgentResponse(
                agent="supervisor",
                success=False,
                message=(
                    "Please provide a valid customer message "
                    f"of up to {MAX_MESSAGE_LENGTH} characters."
                ),
                data={},
                error_code="INVALID_INPUT",
            )
            await event_queue.enqueue_event(create_response_message(response))
            return

        agent_name = await resolve_intent(user_message)

        try:
            result = await call_agent_data_by_name(
                agent_name,
                user_message
            )

            response = AgentResponse(**result)

            logger.info(
                "Agent response received: target=%s success=%s",
                agent_name,
                response.success
            )

        except (httpx.HTTPError, RuntimeError) as exc:

            logger.warning(
                "Agent request failed: target=%s error=%s",
                agent_name,
                type(exc).__name__
            )

            response = AgentResponse(
                agent="supervisor",
                success=False,
                message=(
                    f"The {agent_name} agent is currently unavailable. "
                    "Please try again later."
                ),
                data={"target_agent": agent_name},
                error_code="AGENT_UNAVAILABLE"
            )

        await event_queue.enqueue_event(
            create_response_message(response)
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        raise NotImplementedError(
            "Cancellation is not supported."
        )