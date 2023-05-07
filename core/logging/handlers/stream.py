import logging

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
