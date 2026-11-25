import asyncio
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from agents.supervisor_agent.agent_executor import (
    SupervisorAgentExecutor,
)
from agents.refund_agent.agent_executor import (
    RefundAgentExecutor,
)
from shared.exceptions import (
    AgentUnavailableError,
    AgentTimeoutError,
    AgentDiscoveryError,
    AgentResponseError,
    AgentRPCError,
)


@pytest.mark.parametrize("error", [
    AgentUnavailableError("Offline"),
    AgentTimeoutError("Timeout"),
    AgentDiscoveryError("Discovery failed"),
    AgentResponseError("Invalid response"),
    AgentRPCError("RPC failed"),
    httpx.ConnectError("Connection failed"),
])
def test_supervisor_fallback(error, caplog):

    context = Mock()
    context.get_user_input.return_value = "Track ORD001"

    event_queue = Mock()
    event_queue.enqueue_event = AsyncMock()

    with patch(
        "agents.supervisor_agent.agent_executor.call_agent_data_by_name",
        new_callable=AsyncMock,
        side_effect=error
    ):
        with patch(
            "agents.supervisor_agent.agent_executor.create_response_message"
        ) as mock_response:

            asyncio.run(
                SupervisorAgentExecutor().execute(
                    context,
                    event_queue
                )
            )

            response = mock_response.call_args.args[0]

            assert response.agent == "supervisor"
            assert response.success is False
            assert response.error_code == "AGENT_UNAVAILABLE"
            assert response.data["target_agent"] == "order"
            assert "Please try again later" in response.message

            event_queue.enqueue_event.assert_awaited_once()

    assert "Agent request failed" in caplog.text
    assert type(error).__name__ in caplog.text


@pytest.mark.parametrize("error", [
    AgentUnavailableError("Offline"),
    AgentTimeoutError("Timeout"),
    AgentDiscoveryError("Discovery failed"),
    AgentResponseError("Invalid response"),
    AgentRPCError("RPC failed"),
    httpx.ConnectError("Connection failed"),
])
def test_refund_fallback(error, caplog):

    context = Mock()
    context.get_user_input.return_value = "Refund ORD001"

    event_queue = Mock()
    event_queue.enqueue_event = AsyncMock()

    with patch(
        "agents.refund_agent.agent_executor.get_order_status",
        new_callable=AsyncMock,
        side_effect=error
    ):
        with patch(
            "agents.refund_agent.agent_executor.create_response_message"
        ) as mock_response:

            asyncio.run(
                RefundAgentExecutor().execute(
                    context,
                    event_queue
                )
            )

            response = mock_response.call_args.args[0]

            assert response.agent == "refund"
            assert response.success is False
            assert response.error_code == "ORDER_AGENT_UNAVAILABLE"
            assert response.data["order_id"] == "ORD001"
            assert "Please try again later" in response.message

            event_queue.enqueue_event.assert_awaited_once()

    assert "Order verification failed" in caplog.text
    assert type(error).__name__ in caplog.text
    assert "ORD001" not in caplog.text