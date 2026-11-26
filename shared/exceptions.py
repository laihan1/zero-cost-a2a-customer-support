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

class LLMError(RuntimeError):
    """Base exception for local LLM failures."""


class LLMUnavailableError(LLMError):
    """Raised when the local LLM cannot be reached."""


class LLMTimeoutError(LLMError):
    """Raised when a local LLM request times out."""


class LLMResponseError(LLMError):
    """Raised when the local LLM returns an error or invalid response."""


class LLMDisabledError(LLMError):
    """Raised when local inference is disabled."""
