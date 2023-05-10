import logging
from typing import Callable

from core.config import settings
import datetime

logger = logging.getLogger()
formatter = logging.Formatter("[%(filename)s:%(lineno)s] %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG if settings["LOG_LEVEL"] == "DEBUG" else logging.INFO)


filename = 'logs/{date:%Y-%m-%d_%H:%M:%S}.ansi'.format(date=datetime.datetime.now())
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def decorator(func):
    def wrapper(*args, **kwargs):
        level = logger.level
        logger.setLevel(logging.CRITICAL)
        result = func(*args, **kwargs)
        logger.setLevel(level)
        return result

    return wrapper


logger.disable: Callable = decorator
