"""Centralized logging configuration for the toolkit."""

import logging as lg


def configure_logging(level: int = lg.INFO) -> None:
    """Configure basic logging with a specified level.

    Parameters:
    -----------
    Level : int
        Logging level (default: INFO).
    """
    lg.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
