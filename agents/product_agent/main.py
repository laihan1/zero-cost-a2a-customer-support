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

from agents.product_agent.agent_executor import ProductAgentExecutor


def main():

    configure_logging()

    product_skill = AgentSkill(
        id="product_management",
        name="Product Management",
        description="Handles product enquiries, prices, stock and recommendations.",
        tags=["product", "price", "stock", "recommendation"],
        examples=[
            "How much is the laptop?",
            "Is the keyboard available?",
            "Recommend a product",
        ],
    )

    agent_card = AgentCard(
        name="Product Agent",
        description="An agent that handles product enquiries.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(),
        supported_interfaces=[
            AgentInterface(
                url="http://127.0.0.1:9996/",
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        skills=[product_skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=ProductAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    app = Starlette(
        routes=[
            *create_agent_card_routes(agent_card),
            *create_jsonrpc_routes(request_handler, "/"),
        ]
    )

    uvicorn.run(app, host="127.0.0.1", port=9996)


if __name__ == "__main__":
    main()