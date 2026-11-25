import uvicorn

from shared.logging_config import configure_logging

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

from agents.order_agent.agent_executor import OrderAgentExecutor


def main():

    configure_logging()

    order_skill = AgentSkill(
        id="order_tracking",
        name="Order Tracking",
        description="Handles order status and tracking enquiries.",
        tags=["order", "tracking", "delivery"],
        examples=[
            "Where is my order ORD001?",
            "Check order ORD002",
            "Track my order ORD003",
        ],
    )

    agent_card = AgentCard(
        name="Order Agent",
        description="An agent that handles customer order enquiries.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(),
        supported_interfaces=[
            AgentInterface(
                url="http://127.0.0.1:9998/",
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        skills=[order_skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=OrderAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    app = Starlette(
        routes=[
            *create_agent_card_routes(agent_card),
            *create_jsonrpc_routes(request_handler, "/"),
        ]
    )

    uvicorn.run(app, host="127.0.0.1", port=9998)


if __name__ == "__main__":
    main()