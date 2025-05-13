#############################################################
# Title: Logging Configuration
# Author: Christopher Romanillos
# Description: Modular, dynamic logging setup using JSON logging
# Date: 04/11/25
# Version: 3.0
#############################################################
import os
import logging
import inspect
import yaml
from logging.config import dictConfig
from pythonjsonlogger import jsonlogger

_logger_initialized_paths = set()


def load_config():
    """
    Load the configuration from the YAML file located in the config directory.
    
    Returns:
        dict: Parsed YAML configuration.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))  # /app/src/utils
    config_path = os.path.join(base_dir, "..", "..", "config", "config.yaml")

    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise RuntimeError(f"Config file not found: {config_path}") from e
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing config file: {config_path}") from e


def setup_logging(log_file_path=None):
    """
    Set up JSON logging with configurable log file paths and log levels.
    
    Args:
        log_file_path (str, optional): Custom log file path. Defaults to None.
    """
    config = load_config()

    default_log_file = config["logging"].get("default_utilities_log", "../logs/utilities.log")
    log_level = config["logging"].get("level", "INFO").upper()

    log_file = log_file_path or default_log_file

    if log_file in _logger_initialized_paths:
        return
    _logger_initialized_paths.add(log_file)

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    numeric_level = getattr(logging, log_level, logging.INFO)

    # Define a custom JSON formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['level'] = record.levelname
            log_record['logger'] = record.name
            log_record['module'] = record.module
            log_record['function'] = record.funcName
            log_record['time'] = self.formatTime(record, self.datefmt)

    formatter = CustomJsonFormatter()

    handler = logging.FileHandler(log_file)
    handler.setLevel(numeric_level)
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    logger.addHandler(handler)

    # Optional: also stream to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def get_logger(module_name=None, log_file_path=None):
    """
    Returns a logger instance, automatically selecting the correct log file path
    from the logging section in config.yaml.

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

        # Load config and get corresponding log file from the logging section
        config = load_config()

        # Fetch the log file for the corresponding module from the logging section
        log_file_path = config["logging"].get(f"{calling_script}_log_file", config["logging"]["default_utilities_log"])

    setup_logging(log_file_path=log_file_path)

    logger = structlog.get_logger()
    return logger.bind(module=module_name or calling_script)

