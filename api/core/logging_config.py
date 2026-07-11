"""
Structured logging configuration.

Uses Python's built-in logging module — no print() anywhere in the app.
Separate loggers for prediction, HITL, and general API activity.

Log format includes timestamp, level, module, and message for easy
parsing and monitoring.
"""
from __future__ import annotations

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root and application loggers."""
    fmt = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt, datefmt=date_fmt))

    root = logging.getLogger()
    root.setLevel(level)
    # Avoid duplicate handlers on repeated calls
    if not root.handlers:
        root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("urllib3", "httpx", "httpcore", "tensorflow", "h5py"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


# Convenience logger factories
def get_prediction_logger() -> logging.Logger:
    """Logger for prediction requests — doubles as the monitoring audit trail."""
    return logging.getLogger("prediction")


def get_hitl_logger() -> logging.Logger:
    """Logger for HITL decisions — audit trail for clinician actions."""
    return logging.getLogger("hitl")


def get_api_logger() -> logging.Logger:
    """General API logger."""
    return logging.getLogger("api")
