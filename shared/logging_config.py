import logging
import os


def configure_logging() -> None:

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()

    level = getattr(logging, level_name, logging.INFO)

    if not isinstance(level, int):
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)