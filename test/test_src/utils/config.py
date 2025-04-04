##############################################
# Title: Modular Config Script
# Author: Christopher Romanillos
# Description: Modular config script
# Date: 11/23/24
# Version: 1.0
##############################################

import yaml
import logging
import sys
from dotenv import load_dotenv
from pathlib import Path
import os  # Still needed for environment variable loading

# Create a module-specific logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Prevent duplicate handlers if module is imported multiple times
logger.propagate = False

if not logger.handlers:
    # Create handler for stdout (INFO and lower)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)

    # Create handler for stderr (ERROR and CRITICAL)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)

    # Define a formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Apply the formatter to both handlers
    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)

def load_config(config_path):
    """Load configuration from a YAML file."""
    config_path = Path(config_path).resolve()  # Ensure absolute path
    logger.info(f"Loading configuration from {config_path}")

    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully.")
            return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        raise

def load_env_variables(key):
    """Load environment variables."""
    logger.info("Loading environment variables from .env file")
    load_dotenv()

    value = os.getenv(key)
    if value is None:
        logger.warning(f"Environment variable '{key}' is not set.")
    else:
        logger.info(f"Environment variable '{key}' loaded successfully.")

    return value
