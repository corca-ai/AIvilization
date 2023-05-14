import logging
from typing import Callable

from core.config import settings
from core.logging.handlers.stream import stream_handler

log_level = logging.DEBUG if settings.LOG_LEVEL== "DEBUG" else logging.INFO

logger = logging.getLogger()

logger.addHandler(stream_handler)
logger.setLevel(log_level)

def decorator(func):
    def wrapper(*args, **kwargs):
        level = logger.level
        logger.setLevel(logging.CRITICAL)
        result = func(*args, **kwargs)
        logger.setLevel(level)
        return result

    return wrapper


logger.disable: Callable = decorator
