from a2a.helpers import (
    new_message,
    new_text_part,
    new_data_part,
)
from a2a.types import Message

from shared.response_schema import AgentResponse


def create_response_message(response: AgentResponse) -> Message:
    return new_message(
        parts=[
            new_text_part(response.message),
            new_data_part(response.to_dict()),
        ]
    )