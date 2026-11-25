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

from agents.support_agent.agent_executor import SupportAgentExecutor


def main():

    # 1. Define the agent's skill
    support_skill = AgentSkill(
        id="customer_support",
        name="Customer Support",
        description="Handles basic customer support questions.",
        tags=["support", "FAQ", "refund", "business hours"],
        examples=[
            "Hello",
            "What are your opening hours?",
            "What is your refund policy?",
        ],
    )

    # 2. Create the Agent Card
    agent_card = AgentCard(
        name="Support Agent",
        description="A basic customer support agent.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(),
        supported_interfaces=[
            AgentInterface(
                url="http://127.0.0.1:9999/",
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        skills=[support_skill],
    )

    # 3. Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=SupportAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    # 4. Create A2A routes
    app = Starlette(
        routes=[
            *create_agent_card_routes(agent_card),
            *create_jsonrpc_routes(request_handler, "/"),
        ]
    )

    # 5. Start server
    uvicorn.run(app, host="127.0.0.1", port=9999)


if __name__ == "__main__":
    main()