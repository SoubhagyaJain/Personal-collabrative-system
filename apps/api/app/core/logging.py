import logging
import sys

from pythonjsonlogger import jsonlogger


def configure_logging(log_level: str) -> None:
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.setLevel(log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)