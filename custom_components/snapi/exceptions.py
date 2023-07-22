"""Storing error classes."""

import logging


class ApiError(Exception):
    """Exception raised for API-related errors."""

    def __init__(self, logger: logging.Logger, msg: str) -> None:
        logger.error(msg)
        super().__init__(msg)


class ApiAuthError(Exception):
    """Exception raised for Auth-related errors."""

    def __init__(self, logger: logging.Logger, msg: str) -> None:
        logger.error(msg)
        super().__init__(msg)

    pass
