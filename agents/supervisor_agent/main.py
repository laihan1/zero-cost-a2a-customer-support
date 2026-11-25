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

from agents.supervisor_agent.agent_executor import SupervisorAgentExecutor
from shared.config import SUPERVISOR_PORT, SUPERVISOR_URL


def main():

    # 1. Define the agent's skill
    supervisor_skill = AgentSkill(
        id="customer_support_orchestration",
        name="Customer Support Orchestration",
        description="Routes customer enquiries to specialist agents.",
        tags=["supervisor", "routing", "orchestration"],
        examples=[
            "Where is my order ORD001?",
            "Can I refund my order ORD003?",
            "How much is the laptop?",
            "What are your opening hours?",
        ],
    )

    # 2. Create the Agent Card
    agent_card = AgentCard(
        name="Supervisor Agent",
        description="Coordinates customer support agents.",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(),
        supported_interfaces=[
            AgentInterface(
                url=f"{SUPERVISOR_URL}/",
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        skills=[supervisor_skill],
    )

    # 3. Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=SupervisorAgentExecutor(),
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
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=SUPERVISOR_PORT,
    )


if __name__ == "__main__":
    main()