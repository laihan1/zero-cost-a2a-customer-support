class AgentError(RuntimeError):
    """Base exception for agent communication errors."""


class AgentUnavailableError(AgentError):
    """Raised when an agent cannot be reached."""


class AgentTimeoutError(AgentError):
    """Raised when an agent request times out."""


class AgentDiscoveryError(AgentError):
    """Raised when agent discovery fails."""


class AgentResponseError(AgentError):
    """Raised when an agent returns an invalid response."""


class AgentRPCError(AgentError):
    """Raised when an agent returns a JSON-RPC error."""