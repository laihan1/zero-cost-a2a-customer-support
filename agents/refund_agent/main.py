import uvicorn

from starlette.applications import Starlette
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)

from agents.refund_agent.agent_executor import RefundAgentExecutor


def main():

    refund_skill = AgentSkill(
        id="refund_management",
        name="Refund Management",
        description="Handles refund policies and eligibility checks.",
        tags=["refund", "cancellation", "eligibility"],
        examples=[
            "What is your refund policy?",
            "I want to refund ORD003",
            "Can I cancel ORD002?",
        ],
    )

    agent_card = AgentCard(
        name="Refund Agent",
        description="An agent that handles customer refund enquiries.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(),
        supported_interfaces=[
            AgentInterface(
                url="http://127.0.0.1:9997/",
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        skills=[refund_skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=RefundAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    app = Starlette(
        routes=[
            *create_agent_card_routes(agent_card),
            *create_jsonrpc_routes(request_handler, "/"),
        ]
    )

    uvicorn.run(app, host="127.0.0.1", port=9997)


if __name__ == "__main__":
    main()