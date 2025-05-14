#############################################################
# Title: Logging Configuration
# Author: Christopher Romanillos
# Description: Modular, dynamic logging setup using JSON logging
# Date: 05/14/25
# Version: 3.1
#############################################################

import os
import logging
import inspect
import yaml
from pythonjsonlogger import jsonlogger
import structlog

_logger_initialized_paths = set()

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

def setup_logging(log_file_path=None, config_path=None):
    """
    Set up logging using JSON formatter and values from config.

    Args:
        log_file_path (str, optional): Custom path to log file.
        config_path (str, optional): Path to YAML config.
    """
    config = load_config(config_path)

    log_level = config.get("logging", {}).get("level", "INFO").upper()
    log_file = log_file_path or config["logging"].get("default_utilities_log", "../logs/utilities.log")

    if log_file in _logger_initialized_paths:
        return
    _logger_initialized_paths.add(log_file)

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

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

    if logger.hasHandlers():
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_logger(module_name=None, log_file_path=None, config_path=None):
    """
    Return a structured logger bound to a specific module and log file.

    Args:
        module_name (str, optional): Name of the calling module. Inferred if None.
        log_file_path (str, optional): Path to the log file. If not provided, fetched from config.
        config_path (str, optional): Path to config.yaml.

    Returns:
        structlog.BoundLogger: Configured structured logger.
    """
    if log_file_path is None:
        frame = inspect.stack()[1]
        calling_script = os.path.splitext(os.path.basename(frame.filename))[0]

        config = load_config(config_path)
        log_file_path = config.get("logging", {}).get(
            f"{calling_script}_log_file",
            config["logging"].get("default_utilities_log")
        )
    else:
        calling_script = module_name or "unnamed"

    setup_logging(log_file_path=log_file_path, config_path=config_path)

    logger = structlog.get_logger()
    return logger.bind(module=module_name or calling_script)
