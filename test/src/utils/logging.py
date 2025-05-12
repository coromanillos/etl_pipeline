#############################################################
# Title: Logging Configuration
# Author: Christopher Romanillos
# Description: Modular, dynamic logging setup using structlog
# Date: 04/11/25
# Version: 2.2
#############################################################
import os
import logging
import structlog
from logging.config import dictConfig
import yaml
import inspect

_logger_initialized_paths = set()

def load_config():
    """
    Load the configuration from the YAML file located in the config directory.
    This is intended to be the main configuration file for the app.
    
    Returns:
        dict: Parsed YAML configuration.
    """
    # Ensure logger is initialized first
    logger = structlog.get_logger()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))  # /app/src/utils
    config_path = os.path.join(base_dir, "..", "..", "config", "config.yaml")
    
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        logger.exception(f"Config file not found: {config_path}")  # Log the exception
        raise RuntimeError(f"Config file not found: {config_path}") from e
    except yaml.YAMLError as e:
        logger.exception(f"Error parsing config file: {config_path}")  # Log the exception
        raise RuntimeError(f"Error parsing config file: {config_path}") from e


def setup_logging(log_file_path=None):
    """
    Set up structured logging with configurable log file paths and log levels.
    
    Args:
        log_file_path (str, optional): Custom log file path. Defaults to None.
    """
    config = load_config()
    
    # Set default log file and log level from the configuration file
    default_log_file = config["logging"].get("default_utilities_log", "../logs/utilities.log")
    log_level = config["logging"].get("level", "INFO").upper()

    # Determine which log file to use (either provided or default)
    log_file = log_file_path or default_log_file

    # Prevent re-initializing the same log file
    if log_file in _logger_initialized_paths:
        return
    _logger_initialized_paths.add(log_file)

    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Convert log level to numeric value
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Configure standard logging setup using dictConfig
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": "%(message)s"
            }
        },
        "handlers": {
            "info_stdout": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
                "stream": "ext://sys.stdout",
                "level": "INFO"
            },
            "error_stderr": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
                "stream": "ext://sys.stderr",
                "level": "ERROR"
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": log_file,
                "formatter": "plain",
                "level": "INFO",
                "mode": "a"
            }
        },
        "root": {
            "level": numeric_level,
            "handlers": ["info_stdout", "error_stderr", "file"]
        }
    })

    # Setup structlog for structured logging
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
    Returns a logger instance, automatically selecting the correct log file path
    from the config.yaml based on the calling script's name if not explicitly passed.
    
    Args:
        module_name (str, optional): Name of the calling module. Defaults to None.
        log_file_path (str, optional): Path to the desired log file. Defaults to None.
    
    Returns:
        structlog.BoundLogger: Configured logger instance.
    """
    if log_file_path is None:
        # Try to infer the calling script name (e.g., extract, transform)
        frame = inspect.stack()[1]
        calling_script = os.path.splitext(os.path.basename(frame.filename))[0]

        # Load config and get corresponding log file from section
        config = load_config()
        log_file_path = config.get(calling_script, {}).get("log_file")

    setup_logging(log_file_path=log_file_path)

    logger = structlog.get_logger()
    return logger.bind(module=module_name or calling_script)
