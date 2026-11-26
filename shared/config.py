import math
import os
from collections.abc import Mapping
from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import urlsplit


# Agent ports
SUPPORT_PORT = 9999
ORDER_PORT = 9998
REFUND_PORT = 9997
PRODUCT_PORT = 9996
SUPERVISOR_PORT = 9995

# Agent URLs
SUPPORT_URL = f"http://127.0.0.1:{SUPPORT_PORT}"
ORDER_URL = f"http://127.0.0.1:{ORDER_PORT}"
REFUND_URL = f"http://127.0.0.1:{REFUND_PORT}"
PRODUCT_URL = f"http://127.0.0.1:{PRODUCT_PORT}"
SUPERVISOR_URL = f"http://127.0.0.1:{SUPERVISOR_PORT}"

# A2A timeout settings (seconds)
DISCOVERY_TIMEOUT = 10.0
REQUEST_TIMEOUT = 30.0
REFUND_REQUEST_TIMEOUT = 10.0

@dataclass(frozen=True)
class LLMConfig:
    enabled: bool
    base_url: str
    model: str
    timeout: float
    temperature: float
    num_ctx: int
    num_predict: int
    think: bool
    keep_alive: str


def _llm_boolean(name: str, value: str) -> bool:
    value = value.strip().lower()
    if value not in {"true", "false"}:
        raise ValueError(f"{name} must be true or false.")
    return value == "true"


def _llm_number(
    name: str,
    value: str,
    convert: type[int] | type[float],
    minimum: int,
) -> int | float:
    try:
        parsed = convert(value)
        if math.isfinite(parsed) and parsed >= minimum:
            return parsed
    except (ValueError, OverflowError):
        pass
    raise ValueError(f"{name} must be a finite {convert.__name__} >= {minimum}.")


def _llm_base_url(value: str) -> str:
    error = "LLM_BASE_URL must be a loopback HTTP origin, with an optional port."
    if any(character.isspace() or ord(character) < 32 for character in value):
        raise ValueError(error)

    try:
        url = urlsplit(value)
        host = url.hostname
        port = url.port
        local = host == "localhost" or (
            host is not None and ip_address(host).is_loopback
        )
    except ValueError:
        raise ValueError(error) from None

    if (
        not local
        or url.scheme != "http"
        or url.path not in {"", "/"}
        or port == 0
    ):
        raise ValueError(error)

    authority = f"[{host}]" if ":" in host else host
    if port is not None:
        authority = f"{authority}:{port}"
    if url.netloc.lower() != authority or "?" in value or "#" in value:
        raise ValueError(error)
    return f"http://{authority}"


def load_llm_config(environ: Mapping[str, str] | None = None) -> LLMConfig:
    """Read and validate LLM settings on demand."""
    if environ is None:
        environ = os.environ

    enabled = _llm_boolean("LLM_ENABLED", environ.get("LLM_ENABLED", "false"))
    think = _llm_boolean("LLM_THINK", environ.get("LLM_THINK", "false"))
    base_url = _llm_base_url(environ.get("LLM_BASE_URL", "http://localhost:11434"))
    model = environ.get("LLM_MODEL", "qwen3:4b").strip()
    keep_alive = environ.get("LLM_KEEP_ALIVE", "10m").strip()
    if not model:
        raise ValueError("LLM_MODEL must be non-empty.")
    if not keep_alive:
        raise ValueError("LLM_KEEP_ALIVE must be non-empty.")

    timeout = _llm_number("LLM_TIMEOUT", environ.get("LLM_TIMEOUT", "15.0"), float, 0)
    if timeout == 0:
        raise ValueError("LLM_TIMEOUT must be greater than zero.")

    return LLMConfig(
        enabled=enabled,
        base_url=base_url,
        model=model,
        timeout=float(timeout),
        temperature=float(_llm_number(
            "LLM_TEMPERATURE", environ.get("LLM_TEMPERATURE", "0"), float, 0
        )),
        num_ctx=int(_llm_number(
            "LLM_NUM_CTX", environ.get("LLM_NUM_CTX", "2048"), int, 1
        )),
        num_predict=int(_llm_number(
            "LLM_NUM_PREDICT", environ.get("LLM_NUM_PREDICT", "64"), int, 1
        )),
        think=think,
        keep_alive=keep_alive,
    )
