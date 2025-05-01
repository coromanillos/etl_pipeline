##############################################
# Title: Logging Configuration
# Author: Christopher Romanillos
# Description: Modular, dynamic logging setup using structlog
# Date: 04/11/25
# Version: 2.0
##############################################

import os
import logging
import structlog
from logging.config import dictConfig
import yaml

_logger_initialized_paths = set()  # Track which log files have been initialized


def load_config():
    """Load the configuration from the YAML file."""
    with open("config/config.yaml", "r") as file:
        return yaml.safe_load(file)


def setup_logging(log_file_path=None):
    """
    Set up structured logging dynamically. Default log file is 'utilities.log'.
    :param log_file_path: Optional custom log file path for the current script/module.
    """
    config = load_config()
    default_log_file = config["logging"].get("default_utilities_log", "../logs/utilities.log")
    log_level = config["logging"].get("level", "INFO").upper()

    # Determine which log file to use
    log_file = log_file_path or default_log_file

    # Prevent re-initializing the same log file
    if log_file in _logger_initialized_paths:
        return
    _logger_initialized_paths.add(log_file)

    numeric_level = getattr(logging, log_level, logging.INFO)

    # Ensure directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Set up logging configuration
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
            "level": numeric_level,
            "handlers": ["info_stdout", "error_stderr", "file"]
        }
    })

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        cache_logger_on_first_use=True
    )


def get_logger(module_name=None, log_file_path=None):
    """
    Returns a logger instance for a module/script, with optional dynamic log file.
    :param module_name: Optional name of the script/module using this logger.
    :param log_file_path: Optional path to the log file.
    :return: A bound structlog logger.
    """
    setup_logging(log_file_path=log_file_path)
    logger = structlog.get_logger()
    return logger.bind(module=module_name) if module_name else logger
