import logging
from typing import Callable

from core.config import settings

logger = logging.getLogger()
formatter = logging.Formatter("%(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG if settings["LOG_LEVEL"] == "DEBUG" else logging.INFO)


def decorator(func):
    def wrapper(*args, **kwargs):
        level = logger.level
        logger.setLevel(logging.CRITICAL)
        result = func(*args, **kwargs)
        logger.setLevel(level)
        return result

    return wrapper


logger.disable: Callable = decorator
