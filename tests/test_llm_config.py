import pytest

from shared.config import LLMConfig, load_llm_config


def test_defaults():
    assert load_llm_config({}) == LLMConfig(
        enabled=False,
        base_url="http://localhost:11434",
        model="qwen3:4b",
        timeout=15.0,
        temperature=0.0,
        num_ctx=2048,
        num_predict=64,
        think=False,
        keep_alive="10m",
    )


def test_environment_overrides(monkeypatch):
    overrides = {
        "LLM_ENABLED": "TRUE",
        "LLM_BASE_URL": "http://[::1]:8080/",
        "LLM_MODEL": "other-model",
        "LLM_TIMEOUT": "3.5",
        "LLM_TEMPERATURE": "0.3",
        "LLM_NUM_CTX": "4096",
        "LLM_NUM_PREDICT": "128",
        "LLM_THINK": "true",
        "LLM_KEEP_ALIVE": "5m",
    }
    for name, value in overrides.items():
        monkeypatch.setenv(name, value)

    assert load_llm_config() == LLMConfig(
        enabled=True,
        base_url="http://[::1]:8080",
        model="other-model",
        timeout=3.5,
        temperature=0.3,
        num_ctx=4096,
        num_predict=128,
        think=True,
        keep_alive="5m",
    )


@pytest.mark.parametrize(("name", "value"), [
    ("LLM_ENABLED", "maybe"),
    ("LLM_THINK", "1"),
    ("LLM_TIMEOUT", "NaN"),
    ("LLM_TIMEOUT", "0"),
    ("LLM_TIMEOUT", "-1"),
    ("LLM_TEMPERATURE", "inf"),
    ("LLM_TEMPERATURE", "-0.1"),
    ("LLM_NUM_CTX", "2.5"),
    ("LLM_NUM_CTX", "0"),
    ("LLM_NUM_PREDICT", "-1"),
    ("LLM_MODEL", " "),
    ("LLM_KEEP_ALIVE", ""),
])
def test_invalid_configuration(name, value):
    with pytest.raises(ValueError, match=name):
        load_llm_config({name: value})


@pytest.mark.parametrize("url", [
    "http://localhost",
    "http://127.0.0.2:11434",
    "http://[::1]:11434",
])
def test_loopback_origins(url):
    assert load_llm_config({"LLM_BASE_URL": url}).base_url == url


@pytest.mark.parametrize("url", [
    "https://localhost",
    "http://localhost.example.com",
    "http://192.168.1.1",
    "http://0.0.0.0",
    "http://[::]",
    "http://127.1",
    "http://localhost:65536",
    "http://localhost:0",
    "http://localhost:",
    "http://user:password@localhost",
    "http://localhost@remote.example",
    "http://localhost/api",
    "http://localhost?value=1",
    "http://localhost#",
    "http://local\nhost",
    "http://localhost\\evil",
    "//localhost",
])
def test_invalid_local_endpoint(url):
    with pytest.raises(ValueError, match="LLM_BASE_URL"):
        load_llm_config({"LLM_BASE_URL": url})
