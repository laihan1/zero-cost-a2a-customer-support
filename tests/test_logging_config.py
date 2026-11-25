import logging
from unittest.mock import patch

import pytest

from shared.logging_config import configure_logging


@pytest.mark.parametrize("value, expected", [
    ("DEBUG", logging.DEBUG),
    ("INFO", logging.INFO),
    ("WARNING", logging.WARNING),
    ("ERROR", logging.ERROR),
    ("invalid", logging.INFO),
])
def test_logging_level(monkeypatch, value, expected):

    monkeypatch.setenv("LOG_LEVEL", value)

    with patch("logging.basicConfig") as mock_config:
        with patch("logging.getLogger"):

            configure_logging()

            assert mock_config.call_args.kwargs["level"] == expected


def test_default_logging_level(monkeypatch):

    monkeypatch.delenv("LOG_LEVEL", raising=False)

    with patch("logging.basicConfig") as mock_config:
        with patch("logging.getLogger"):

            configure_logging()

            assert (
                mock_config.call_args.kwargs["level"]
                == logging.INFO
            )