import logging
import os


def configure_logging():
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger()
    if logger.handlers:
        return logger

    logger.setLevel(level)
    fmt = os.environ.get("LOG_FORMAT", "%(asctime)s %(levelname)s %(name)s - %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)

    return logger
