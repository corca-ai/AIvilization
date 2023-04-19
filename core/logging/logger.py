import logging

from core.config import settings

logger = logging.getLogger()
formatter = logging.Formatter("%(levelname)s: %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

if settings["LOG_LEVEL"] == "DEBUG":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
