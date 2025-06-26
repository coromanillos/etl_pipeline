#############################################################
# Title: Logging Configuration (modernized)
# Author: Christopher Romanillos, Copilot
# Description: Structured logging setup for standalone scripts only.
# Designed NOT to conflict with Airflow logging.
# Use-case: Scripts that run outside of Airflow and Docker.
# Date: 2025-06-25
# Version: 4.1
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

def is_running_in_airflow():
    """
    Detect if the current context is an Airflow task or worker process,
    by checking for common Airflow environment variables.
    """
    # AIRFLOW_CTX_DAG_ID is set inside task instances
    return "AIRFLOW_CTX_DAG_ID" in os.environ or "AIRFLOW_HOME" in os.environ

def setup_logging(config_path=None, force=False):
    """
    Set up logging using JSON formatter and values from config.
    Logs go to STDOUT only.

    Parameters:
    - config_path: path to config.yaml
    - force: if True, will initialize regardless of Airflow context (useful for testing)
    """
    global _logger_initialized
    if _logger_initialized:
        return
    # Skip setup if running inside Airflow unless forced
    if is_running_in_airflow() and not force:
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

    # Remove existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_logger(module_name=None, config_path=None, force_setup=False):
    """
    Return a structured logger bound to a specific module.

    - Does NOT initialize logging if inside Airflow by default.
    - To override (for standalone testing), set force_setup=True.

    Args:
        module_name (str, optional): Name of the calling module. Inferred if None.
        config_path (str, optional): Path to config.yaml.
        force_setup (bool): Force logging setup regardless of Airflow context.

    Returns:
        structlog.BoundLogger: Configured structured logger.
    """
    if module_name is None:
        frame = inspect.stack()[1]
        module_name = os.path.splitext(os.path.basename(frame.filename))[0]

    setup_logging(config_path=config_path, force=force_setup)
    logger = structlog.get_logger()
    return logger.bind(module=module_name)
