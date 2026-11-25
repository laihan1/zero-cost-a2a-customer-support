from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class AgentResponse:
    agent: str
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)