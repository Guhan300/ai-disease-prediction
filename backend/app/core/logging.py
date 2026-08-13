"""Structured application logging setup."""

import logging
import sys
from typing import Optional

from app.core.config import get_settings


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """
    Configure root logging for the application.

    Args:
        level: Optional log level override (e.g. INFO, DEBUG).

    Returns:
        Configured application logger.
    """
    settings = get_settings()
    log_level = (level or settings.log_level).upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logger = logging.getLogger("disease_risk")
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a named child logger."""
    return logging.getLogger(f"disease_risk.{name}")
