##############################################
# Title: Logging Configuration
# Author: Christopher Romanillos
# Description: Structlog-based logging setup
# Date: 3/06/25
# Version: 1.1
###############################################

import os
import logging
import structlog
from logging.config import dictConfig
import yaml

_logger_initialized = False  # Flag to prevent reinitialization

def load_config():
    """Load YAML configuration."""
    with open("config/config.yaml", "r") as file:
        return yaml.safe_load(file)

def setup_logging():
    global _logger_initialized

    if _logger_initialized:
        return structlog.get_logger()

    config = load_config()
    log_file = config["logging"]["log_file"]

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.processors.JSONRenderer()
            }
        },
        "handlers": {
            "info_stdout": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
                "level": "INFO"
            },
            "error_stderr": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stderr",
                "level": "ERROR"
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": log_file,
                "formatter": "json",
                "level": "INFO"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["info_stdout", "error_stderr", "file"]
        }
    })

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True
    )

    _logger_initialized = True
    return structlog.get_logger()
