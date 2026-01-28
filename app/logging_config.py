import logging
from pythonjsonlogger import jsonlogger
from app.config import settings


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(settings.log_level)

    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    # avoid duplicate logs on reload
    if not logger.handlers:
        logger.addHandler(handler)
