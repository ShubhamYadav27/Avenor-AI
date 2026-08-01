"""Structured logging setup."""
import logging
import sys
import structlog
from app.core.config import settings


def configure_logging() -> None:
    """Configure structlog — pretty in dev, JSON in production."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=False)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging for libraries
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    for lib in ("httpx", "httpcore", "celery.utils.functional", "sqlalchemy.engine"):
        logging.getLogger(lib).setLevel(logging.WARNING)


def get_logger(name: str):
    return structlog.get_logger(name)
