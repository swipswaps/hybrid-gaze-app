# Structured JSON Logging Configuration for FastAPI Production Deployments
# Reference: Python Logging Documentation (https://docs.python.org/3/library/logging.html)
# Reference: Python JSON Logger Package (https://github.com/madzak/python-json-logger)

import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_structured_logging(log_level: str = "INFO"):
    logger = logging.getLogger()
    logger.setLevel(log_level.upper())
    if logger.hasHandlers():
        logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(filename)s %(lineno)d',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("uvicorn.error").handlers = [handler]
