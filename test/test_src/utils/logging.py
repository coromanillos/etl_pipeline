# logging.py
##############################################
# Title: Logging Configuration
# Author: Christopher Romanillos
# Description: Structlog-based logging setup
# Date: 3/06/25
# Version: 1.0
###############################################

import os
import logging
import structlog
from logging.config import dictConfig
import yaml

def load_config():
    """Load YAML configuration."""
    with open("config/config.yaml", "r") as file:
        return yaml.safe_load(file)

def setup_logging():
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

    return structlog.get_logger()

# Initialize logger to be imported elsewhere
logger = setup_logging()
