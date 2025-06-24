#############################################################
# Title: Logging Configuration (modernized)
# Author: Christopher Romanillos, Copilot
# Description: Structured, dynamic logging to STDOUT only
# Date: 2025-05-18
# Version: 4.0 | in-use
#############################################################

import os
import logging
import inspect
import yaml
from pythonjsonlogger import jsonlogger
import structlog

_logger_initialized = False

def load_config(config_path=None):
    """
    Load the configuration from a YAML file.

    Args:
        config_path (str, optional): Custom path to the YAML config. Defaults to ../../config/config.yaml.

    Returns:
        dict: Parsed YAML config.
    """
    if config_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "..", "..", "config", "config.yaml")
    config_path = os.path.abspath(config_path)
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError as e:
        raise RuntimeError(f"Config file not found: {config_path}") from e
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing config file: {config_path}") from e

def setup_logging(config_path=None):
    """
    Set up logging using JSON formatter and values from config.
    Logs go to STDOUT only.
    """
    global _logger_initialized
    if _logger_initialized:
        return
    _logger_initialized = True

    config = load_config(config_path)
    log_level = config.get("logging", {}).get("level", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['level'] = record.levelname
            log_record['logger'] = record.name
            log_record['module'] = record.module
            log_record['function'] = record.funcName
            log_record['time'] = self.formatTime(record, self.datefmt)

    formatter = CustomJsonFormatter()

    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    # Remove all existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    # Add only a stream handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_logger(module_name=None, config_path=None):
    """
    Return a structured logger bound to a specific module.
    Args:
        module_name (str, optional): Name of the calling module. Inferred if None.
        config_path (str, optional): Path to config.yaml.

    Returns:
        structlog.BoundLogger: Configured structured logger.
    """
    if module_name is None:
        frame = inspect.stack()[1]
        module_name = os.path.splitext(os.path.basename(frame.filename))[0]

    setup_logging(config_path=config_path)
    logger = structlog.get_logger()
    return logger.bind(module=module_name)